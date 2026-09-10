#!/usr/bin/env -S uv run
# /// script
# dependencies = ["openai>=1.0"]
# ///
"""
Psyche Model Comparison: 7 models across DeepInfra + Claude CLI (alias + pinned 4.6)

Generates personality reports from each MODELS entry using identical prompts,
scores prediction accuracy against ground truth, and runs tri-judge
evaluation: Opus current (alias), Opus 4.6 (pinned), GPT-5.4.

Each per-run JSON records both the alias the caller used and the resolved
full model ID at invocation time, so results remain interpretable after
aliases move across releases.

Usage:
    export DEEPINFRA_API_KEY=...
    ./benchmark/run_eval.py [--phase prepare|generate|score|judge|analyze|all]
"""
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

from openai import OpenAI

# --- Constants ---

BENCHMARK_DIR = Path(__file__).parent
REPORTS_DIR = BENCHMARK_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

PROFILE_DIR = BENCHMARK_DIR.parent / "profiles"

# Real ground-truth vector is PRIVATE (gitignored ground_truth.json beside this
# file; see benchmark/.gitignore). The committed fallback is a synthetic
# midpoint profile so the harness stays runnable from a public checkout —
# scores computed against it are placeholders, not the subject's data.
_GT_FILE = BENCHMARK_DIR / "ground_truth.json"
if _GT_FILE.exists():
    GROUND_TRUTH = json.loads(_GT_FILE.read_text())
else:
    GROUND_TRUTH = {"N": 50.0, "E": 50.0, "O": 50.0, "A": 50.0, "C": 50.0}

MODELS = {
    # Prices below re-read live from api.deepinfra.com/models/list on
    # 2026-07-31T17:52Z. Three entries were stale (row 232 found this on
    # 07-30; confirmed live again today): DeepSeek-V3 understated its OUTPUT
    # price 2.3x, GLM-5 and Nemotron overstated by ~25%. Costs already stored
    # in reports/*.json were computed at generation time with the old numbers
    # and are NOT retroactively corrected — see
    # reports/luna-psyche-harness-2026-07-31.md for the corrected figures.
    "deepseek-v3": {
        "id": "deepseek-ai/DeepSeek-V3",
        "provider": "deepinfra",
        "cost_in": 0.32,
        "cost_out": 0.89,
    },
    "nemotron-3-super": {
        "id": "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B",
        "provider": "deepinfra",
        "cost_in": 0.085,
        "cost_out": 0.40,
    },
    "kimi-k2.5": {
        "id": "moonshotai/Kimi-K2.5",
        "provider": "deepinfra",
        "cost_in": 0.45,
        "cost_out": 2.25,
    },
    "kimi-k2": {
        "id": "moonshotai/Kimi-K2-Instruct-0905",
        "provider": "deepinfra",
        "cost_in": 0.40,
        "cost_out": 2.00,
    },
    "glm-5": {
        "id": "zai-org/GLM-5",
        "provider": "deepinfra",
        "cost_in": 0.60,
        "cost_out": 2.08,
    },
    # Same model + provider as "kimi-k2.5", re-run 2026-07-31 so the production
    # incumbent has a SAME-DAY cost/latency measurement to compare the GPT-5.6
    # tiers against (row 34a). Separate key so the cached 2026-03-31 artifact is
    # never overwritten. Doubles as the harness's first repeat-generation, i.e.
    # its first run-to-run variance datapoint.
    "kimi-k2.5-rerun-20260731": {
        "id": "moonshotai/Kimi-K2.5",
        "provider": "deepinfra",
        "cost_in": 0.45,
        "cost_out": 2.25,
    },
    "hermes-3-405b": {
        "id": "NousResearch/Hermes-3-Llama-3.1-405B",
        "provider": "deepinfra",
        "cost_in": 1.00,
        "cost_out": 1.00,
    },
    "kimi-k2.6": {
        "id": "moonshotai/Kimi-K2.6",
        "provider": "openrouter",
        "cost_in": 0.75,
        "cost_out": 3.50,
    },
    # GPT-5.6 cheap tiers (added 2026-07-31, rows 243 / 34a). Prices are the
    # OpenRouter catalog rates read at run time; see reports/luna-*.md for the
    # measurement cutoff.
    "luna": {
        "id": "openai/gpt-5.6-luna",
        "provider": "openrouter",
        "cost_in": 0.10,
        "cost_out": 0.60,
    },
    "terra": {
        "id": "openai/gpt-5.6-terra",
        "provider": "openrouter",
        "cost_in": 1.00,
        "cost_out": 6.00,
    },
    # Row 452 bench program (owner authorization 2026-08-05T17:42-17:48Z):
    # GLM-5.2 + DeepSeek V4 Flash + third pick, same frozen stimulus. Prices
    # read live from api.deepinfra.com/models/list at 2026-08-05T18:0xZ.
    "glm-5.2": {
        "id": "zai-org/GLM-5.2",
        "provider": "deepinfra",
        "cost_in": 0.75,
        "cost_out": 2.40,
    },
    "deepseek-v4-flash": {
        "id": "deepseek-ai/DeepSeek-V4-Flash",
        "provider": "deepinfra",
        "cost_in": 0.09,
        "cost_out": 0.18,
    },
    "deepseek-v4-pro": {
        "id": "deepseek-ai/DeepSeek-V4-Pro",
        "provider": "deepinfra",
        "cost_in": 1.30,
        "cost_out": 2.60,
    },
    # Length-fix confirmation run (2026-08-05, q-psyche-route-deploy-452 deploy):
    # same model+route as "luna", generated under the v1.1.0 prompt (the
    # "stay close to 1500 words" reinforcement). Separate key so the 07-31
    # pre-fix artifact is never overwritten.
    "luna-lengthfix-20260805": {
        "id": "openai/gpt-5.6-luna",
        "provider": "openrouter",
        "cost_in": 0.10,
        "cost_out": 0.60,
    },
    # Alias-based entry: `"opus"` tracks the current Claude Opus generation
    # as resolved by `claude -p --model opus`. This intentionally drifts with
    # releases — a later run under this key produces results from the
    # newer model. Provenance captured at runtime in the per-run JSON below.
    "opus": {
        "id": "opus",
        "provider": "claude-cli",
        "cost_in": 0,
        "cost_out": 0,
    },
    # Pinned historical entry: explicit claude-opus-4-6 for cross-generation
    # comparison. Remove when 4.6 is no longer callable.
    "opus-4.6-pinned": {
        "id": "claude-opus-4-6",
        "provider": "claude-cli",
        "cost_in": 0,
        "cost_out": 0,
    },
}


# Alias -> current full model ID. Mirrors psyche_analysis/config.py; kept
# duplicated here so the benchmark has no package dependency on the
# analysis tree. Keep in sync with ~/.claude/CLAUDE.md contemporary-models.
_ALIAS_TO_FULL_ID = {
    "opus":   "claude-opus-4-7",
    "sonnet": "claude-sonnet-4-6",
    "haiku":  "claude-haiku-4-5",
}


def resolve_model_alias(id_or_alias: str) -> str:
    """Return the resolved full model ID for an alias, or pass through."""
    return _ALIAS_TO_FULL_ID.get(id_or_alias, id_or_alias)

JUDGE_RUBRIC = {
    "evidence_integration": {
        "weight": 0.25,
        "description": "Are interview quotes cited to support personality claims? 0=none cited, 50=some paraphrased, 100=specific quotes woven throughout",
    },
    "insight_depth": {
        "weight": 0.25,
        "description": "Does it go beyond restating scores to find cross-instrument patterns? 0=just lists scores, 50=some synthesis, 100=reveals non-obvious patterns across instruments",
    },
    "tension_identification": {
        "weight": 0.20,
        "description": "Does it catch discrepancies (e.g. Agreeableness self-report vs interview, Dutifulness vs Orderliness)? 0=ignores contradictions, 50=notes one, 100=identifies and explains multiple tensions",
    },
    "clinical_safety": {
        "weight": 0.10,
        "description": "Does it avoid diagnosing disorders or implying the person is sick/broken? Standard personality psychology terms (attachment styles, Dark Triad scales, emotion regulation strategies) are EXPECTED and should NOT be penalized — they are the vocabulary of the instruments being reported. Penalize only: diagnosing clinical disorders (e.g. 'you have BPD'), pathologizing normal behavior as symptoms, or framing coping strategies as trauma responses without evidence. Respecting the person's own framing of their experiences (including religious/spiritual) is correct, not a safety failure. 0=diagnoses disorders or pathologizes, 50=inconsistent (some pathologizing mixed with appropriate framing), 100=consistently respectful personality framing throughout",
    },
    "narrative_quality": {
        "weight": 0.20,
        "description": "Coherent, readable, second-person, appropriate length (~1500 words)? 0=incoherent/wrong person, 50=readable but uneven, 100=polished, well-structured narrative",
    },
}

INTERVIEW_PROMPTS = [
    "Describe yourself as you would to a stranger who will never see you. Be as honest as possible.",
    "What are you most proud of? What are you least proud of?",
    "How do you typically respond to conflict or disagreement?",
    "Describe a decision you made recently that you found difficult. What made it hard?",
    "What gives you energy? What drains you?",
    "How have you changed in the last five years? What caused the change?",
    "What do your closest friends value most about you? What do they wish you'd change?",
    "Describe your relationship with uncertainty and ambiguity.",
    "What topic could you talk about for hours? Why does it matter to you?",
    "If you could design your ideal day with no obligations, what would it look like?",
]

SYSTEM_PROMPT = """You are a personality assessment specialist. You will receive:
1. Psychometric instrument scores (normalized 0-100 per scale) from validated instruments
2. Free-text interview responses to 10 self-reflection prompts

Your task: Generate a comprehensive personality report that synthesizes quantitative scores with qualitative interview data.

Output format:
1. A JSON block with structured personality predictions (between <json> tags)
2. A ~1500-word narrative report (between <report> tags) — stay close to 1500 words; do not exceed 1800

The JSON predictions should have this structure:
{
  "big_five": { "openness": 0-100, "conscientiousness": 0-100, "extraversion": 0-100, "agreeableness": 0-100, "neuroticism": 0-100 },
  "key_traits": ["trait1", "trait2", ...],
  "strengths": ["strength1", "strength2", ...],
  "growth_areas": ["area1", "area2", ...],
  "interview_themes": ["theme1", "theme2", ...]
}

The narrative report should:
- Integrate quantitative scores with qualitative evidence from interview responses
- Be written in second person ("You tend to...")
- Avoid clinical jargon; use accessible language
- Highlight patterns where multiple instruments converge on the same trait
- Note any interesting tensions between self-report scores and interview content
- Be honest but compassionate — acknowledge difficulties without pathologizing
- Include specific quotes or paraphrases from interview responses as evidence

IMPORTANT: This is NOT a clinical diagnosis. Frame all findings as personality patterns and tendencies, not disorders.

When discussing behavioral patterns:
- Describe coping strategies as learned or chosen behaviors, not as trauma responses. Even when someone describes difficult history, frame their current patterns as active strategies ("you tend to withdraw when overwhelmed") not nervous-system explanations ("your nervous system learned to stay on high alert"). The person is an agent making choices, not a body executing threat responses.
- Use hedged language for psychological constructs ("consistent with", "suggests a pattern of") rather than categorical labels ("you are anxious-preoccupied")
- Avoid pathologizing language in section headers — use descriptive framing ("How You Process Emotion") not clinical framing ("Anhedonic Depression", "Obsession")
- Stay in the lane of personality description. Do not recommend therapeutic techniques or treatment constructs (e.g. "earned secure attachment", "exposure work"). Growth areas should be framed as observations, not prescriptions."""


# --- Phase 1: Prepare ---

def prepare_input() -> tuple[str, str]:
    """Build the identical system+user prompts for all 3 models."""
    scored_path = PROFILE_DIR / "self-report-scored.json"
    with open(scored_path) as f:
        data = json.load(f)

    # Build scores JSON (excluding open-ended metadata)
    scores = {}
    for k, v in data["results"].items():
        if k == "open-ended":
            continue
        scores[k] = v
    scores_json = json.dumps(scores, indent=2)

    # Build interview responses
    interview_responses = []
    session = data["sessions"]["open-ended"]
    for i, resp in enumerate(session["responses"]):
        interview_responses.append(resp["value"])

    # Build user prompt matching buildReportPrompt() format
    user_prompt = "## Psychometric Scores\n\n```json\n" + scores_json + "\n```\n\n"
    user_prompt += "## Interview Responses\n\n"
    for i, (prompt_text, response_text) in enumerate(
        zip(INTERVIEW_PROMPTS, interview_responses)
    ):
        user_prompt += f"### Q: {prompt_text}\n\n{response_text}\n\n"

    # Save prepared prompts
    prepared = {
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "ground_truth_big_five": GROUND_TRUTH,
    }
    with open(BENCHMARK_DIR / "prepared_input.json", "w") as f:
        json.dump(prepared, f, indent=2)

    print(f"Prepared input saved. User prompt: {len(user_prompt)} chars")
    return SYSTEM_PROMPT, user_prompt


# --- Phase 2: Generate ---

def generate_deepinfra(
    model_key: str, system_prompt: str, user_prompt: str
) -> dict:
    """Call a DeepInfra model via OpenAI-compatible API."""
    api_key = os.environ.get("DEEPINFRA_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPINFRA_API_KEY not set")

    model_id = MODELS[model_key]["id"]
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepinfra.com/v1/openai",
    )

    print(f"  Calling {model_key} ({model_id})...")
    start = time.time()
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=16384,
                temperature=0.3,
            )
            break
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = 15 * (attempt + 1)
                print(f"    Rate limited, retrying in {wait}s (attempt {attempt + 2}/{max_retries})...")
                time.sleep(wait)
            else:
                raise
    elapsed = time.time() - start

    content = response.choices[0].message.content or ""
    usage = {
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
    }

    cost = (
        usage["prompt_tokens"] / 1_000_000 * MODELS[model_key]["cost_in"]
        + usage["completion_tokens"] / 1_000_000 * MODELS[model_key]["cost_out"]
    )

    result = {
        "model_key": model_key,
        "model_id": model_id,
        "content": content,
        "usage": usage,
        "cost_usd": round(cost, 6),
        "latency_s": round(elapsed, 1),
        "finish_reason": response.choices[0].finish_reason if response.choices else None,
    }

    out_path = REPORTS_DIR / f"{model_key}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    # Also save raw report as markdown
    with open(REPORTS_DIR / f"{model_key}.md", "w") as f:
        f.write(content)

    print(f"  {model_key}: {usage['completion_tokens']} tokens, ${cost:.4f}, {elapsed:.1f}s")
    return result


def generate_openrouter(
    model_key: str, system_prompt: str, user_prompt: str
) -> dict:
    """Call an OpenRouter model via OpenAI-compatible API."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    model_id = MODELS[model_key]["id"]
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    print(f"  Calling {model_key} ({model_id}) via OpenRouter...")
    start = time.time()
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=16384,
                temperature=0.3,
            )
            break
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = 15 * (attempt + 1)
                print(f"    Rate limited, retrying in {wait}s (attempt {attempt + 2}/{max_retries})...")
                time.sleep(wait)
            else:
                raise
    elapsed = time.time() - start

    content = response.choices[0].message.content or ""
    usage = {
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
    }

    cost = (
        usage["prompt_tokens"] / 1_000_000 * MODELS[model_key]["cost_in"]
        + usage["completion_tokens"] / 1_000_000 * MODELS[model_key]["cost_out"]
    )

    result = {
        "model_key": model_key,
        "model_id": model_id,
        "content": content,
        "usage": usage,
        "cost_usd": round(cost, 6),
        "latency_s": round(elapsed, 1),
        "finish_reason": response.choices[0].finish_reason if response.choices else None,
    }

    out_path = REPORTS_DIR / f"{model_key}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    # Also save raw report as markdown
    with open(REPORTS_DIR / f"{model_key}.md", "w") as f:
        f.write(content)

    print(f"  {model_key}: {usage['completion_tokens']} tokens, ${cost:.4f}, {elapsed:.1f}s")
    return result


def generate_opus(system_prompt: str, user_prompt: str, model_key: str = "opus") -> dict:
    """Call Claude Opus via claude -p CLI for a candidate report.

    ``model_key`` must be a key present in ``MODELS`` whose provider is
    ``claude-cli``. The ``id`` field is passed directly to ``claude -p --model``
    (can be an alias like ``"opus"`` or a pinned ID like ``"claude-opus-4-6"``).
    """
    model_id = MODELS[model_key]["id"]
    resolved_full_id = resolve_model_alias(model_id)

    # Build the full prompt for claude -p (system + user combined)
    full_prompt = f"<system>\n{system_prompt}\n</system>\n\n{user_prompt}"

    print(f"  Calling {model_key} (--model {model_id}) via claude -p...")
    start = time.time()

    # Must unset CLAUDECODE to avoid nested session error
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)

    # --safe-mode + neutral cwd: context isolation (plain claude -p loads
    # ~/.claude/CLAUDE.md incl. the subject's psychometric profile; runs
    # before 2026-06-09 were not isolated — see
    # ../docs/reviews/context-contamination-audit-2026-06-09.md).
    result = subprocess.run(
        ["claude", "-p", "--safe-mode", "--model", model_id],
        input=full_prompt,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"  ERROR: claude -p failed: {result.stderr[:500]}")
        raise RuntimeError(f"claude -p failed: {result.stderr[:200]}")

    content = result.stdout.strip()

    # Provenance: record both the requested (alias or ID) and the resolved
    # full ID so results stay interpretable after the alias moves.
    result_data = {
        "model_key": model_key,
        "model_requested": model_id,
        "model_resolved": resolved_full_id,
        "content": content,
        "usage": {"prompt_tokens": 0, "completion_tokens": 0},  # Not available via CLI
        "cost_usd": 0,
        "latency_s": round(elapsed, 1),
    }

    out_path = REPORTS_DIR / f"{model_key}.json"
    with open(out_path, "w") as f:
        json.dump(result_data, f, indent=2)

    with open(REPORTS_DIR / f"{model_key}.md", "w") as f:
        f.write(content)

    print(f"  {model_key}: {len(content)} chars, {elapsed:.1f}s")
    return result_data


def generate_all(system_prompt: str, user_prompt: str) -> dict[str, dict]:
    """Generate reports from all models, skipping those already cached."""
    print("\n=== Phase 2: Generating Reports ===")
    results = {}

    # DeepInfra models
    deepinfra_models = [k for k, v in MODELS.items() if v["provider"] == "deepinfra"]
    for model_key in deepinfra_models:
        cached = REPORTS_DIR / f"{model_key}.json"
        if cached.exists():
            print(f"  {model_key}: using cached result")
            with open(cached) as f:
                results[model_key] = json.load(f)
            continue
        results[model_key] = generate_deepinfra(model_key, system_prompt, user_prompt)

    # Claude via CLI (all `claude-cli` providers, cached per-key)
    claude_cli_models = [k for k, v in MODELS.items() if v["provider"] == "claude-cli"]
    for model_key in claude_cli_models:
        cached = REPORTS_DIR / f"{model_key}.json"
        if cached.exists():
            print(f"  {model_key}: using cached result")
            with open(cached) as f:
                results[model_key] = json.load(f)
        else:
            results[model_key] = generate_opus(system_prompt, user_prompt, model_key=model_key)

    # OpenRouter models
    openrouter_models = [k for k, v in MODELS.items() if v["provider"] == "openrouter"]
    for model_key in openrouter_models:
        cached = REPORTS_DIR / f"{model_key}.json"
        if cached.exists():
            print(f"  {model_key}: using cached result")
            with open(cached) as f:
                results[model_key] = json.load(f)
            continue
        results[model_key] = generate_openrouter(model_key, system_prompt, user_prompt)

    return results


# --- Phase 3: Score Predictions ---

def parse_json_block(content: str) -> dict | None:
    """Extract JSON from <json>...</json> tags."""
    import re

    match = re.search(r"<json>\s*(.*?)\s*</json>", content, re.DOTALL)
    if not match:
        # Try finding raw JSON block
        match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def parse_report_block(content: str) -> str:
    """Extract narrative from <report>...</report> tags."""
    import re

    match = re.search(r"<report>\s*(.*?)\s*</report>", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: return everything after the JSON block
    json_end = content.find("</json>")
    if json_end > 0:
        return content[json_end + 7:].strip()
    return content


def score_predictions(results: dict[str, dict]) -> dict[str, dict]:
    """Compute MAE against ground truth Big Five for each model."""
    print("\n=== Phase 3: Prediction Accuracy ===")

    b5_map = {
        "openness": "O",
        "conscientiousness": "C",
        "extraversion": "E",
        "agreeableness": "A",
        "neuroticism": "N",
    }

    scores = {}
    for model_key, result in results.items():
        parsed = parse_json_block(result["content"])
        if not parsed or "big_five" not in parsed:
            print(f"  {model_key}: FAILED to parse JSON predictions")
            scores[model_key] = {
                "predictions": None,
                "mae": None,
                "accuracy_score": 0,
            }
            continue

        predictions = parsed["big_five"]
        errors = {}
        for trait_name, trait_code in b5_map.items():
            pred = predictions.get(trait_name, 50)
            actual = GROUND_TRUTH[trait_code]
            errors[trait_code] = abs(pred - actual)

        mae = sum(errors.values()) / len(errors)
        accuracy_score = max(0, 100 - mae * 2)

        scores[model_key] = {
            "predictions": {
                b5_map[k]: v for k, v in predictions.items() if k in b5_map
            },
            "errors": errors,
            "mae": round(mae, 2),
            "accuracy_score": round(accuracy_score, 1),
        }

        print(
            f"  {model_key}: MAE={mae:.1f}, Score={accuracy_score:.1f}"
            f"  errors={json.dumps({k: round(v,1) for k,v in errors.items()})}"
        )

    with open(BENCHMARK_DIR / "prediction_scores.json", "w") as f:
        json.dump(scores, f, indent=2)

    return scores


# --- Phase 4: Judge Evaluation ---

JUDGE_SYSTEM_PROMPT = """You are an expert evaluator of personality assessment reports. You will receive:
1. The psychometric input data (scores + interview responses) that was given to a model
2. The ground truth Big Five scores from a comprehensive multi-method assessment
3. A personality report generated by an AI model (identity hidden)
4. A scoring rubric with 5 dimensions

Your task: Score the report on each dimension (0-100) with brief reasoning.

Output ONLY valid JSON in this exact format:
{
  "evidence_integration": {"score": 0-100, "reasoning": "..."},
  "insight_depth": {"score": 0-100, "reasoning": "..."},
  "tension_identification": {"score": 0-100, "reasoning": "..."},
  "clinical_safety": {"score": 0-100, "reasoning": "..."},
  "narrative_quality": {"score": 0-100, "reasoning": "..."}
}

Score anchors for each dimension:
- 0-20: Completely absent or actively harmful
- 21-40: Minimal presence, major gaps
- 41-60: Adequate but unremarkable
- 61-80: Good, clear competence
- 81-100: Excellent, noteworthy quality"""


def build_judge_prompt(
    user_prompt: str, report_content: str, report_label: str
) -> str:
    """Build the judge evaluation prompt."""
    rubric_text = "\n".join(
        f"- **{dim}** (weight {info['weight']}): {info['description']}"
        for dim, info in JUDGE_RUBRIC.items()
    )

    narrative = parse_report_block(report_content)

    return f"""## Input Data Given to the Model

{user_prompt}

## Ground Truth Big Five (from comprehensive multi-method assessment)

N={GROUND_TRUTH['N']}, E={GROUND_TRUTH['E']}, O={GROUND_TRUTH['O']}, A={GROUND_TRUTH['A']}, C={GROUND_TRUTH['C']}

## Report to Evaluate: {report_label}

{narrative}

## Scoring Rubric

{rubric_text}

Score {report_label} on all 5 dimensions. Output ONLY valid JSON."""


# Optional raw-output retention hook. When set to a callable, every judge
# invocation passes it the raw model stdout BEFORE any JSON parsing, so runs
# that require raw-output provenance can keep it on disk. None = off (default
# behaviour, unchanged). Added 2026-07-31 for the row-243 Luna run.
RAW_JUDGE_SINK = None


def _emit_raw(judge_id: str, content: str) -> None:
    if RAW_JUDGE_SINK is not None:
        RAW_JUDGE_SINK(judge_id, content)


def judge_with_claude_cli(prompt: str, claude_model: str) -> dict | None:
    """Run a Claude judge via ``claude -p --model <claude_model>``.

    ``claude_model`` can be an alias (``"opus"``) or a pinned full ID
    (``"claude-opus-4-6"``). The alias path drifts with releases — desired
    for tracking the current generation. The pinned path locks a specific
    generation for cross-generation comparison.
    """
    full_prompt = f"<system>\n{JUDGE_SYSTEM_PROMPT}\n</system>\n\n{prompt}"

    env = os.environ.copy()
    env.pop("CLAUDECODE", None)

    # --safe-mode: context-isolated judging (see note in generate_opus).
    result = subprocess.run(
        ["claude", "-p", "--safe-mode", "--model", claude_model],
        input=full_prompt,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"    Claude judge ({claude_model}) error: {result.stderr[:200]}")
        _emit_raw(claude_model, f"<<RETURNCODE {result.returncode}>>\n{result.stderr}")
        return None

    content = result.stdout.strip()
    _emit_raw(claude_model, content)
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
            except json.JSONDecodeError:
                print(f"    Failed to parse Claude judge response ({claude_model})")
                return None
        else:
            print(f"    Failed to parse Claude judge response ({claude_model})")
            return None

    # Provenance capture: embed the judge identity in every rubric row so
    # downstream analysis can track which generation produced which score.
    parsed["_judge_requested"] = claude_model
    parsed["_judge_resolved"] = resolve_model_alias(claude_model)
    return parsed


def judge_with_opus(prompt: str) -> dict | None:
    """Alias-based Opus judge — tracks current Opus generation (resolves to
    claude-opus-4-7 as of 2026-04-18)."""
    return judge_with_claude_cli(prompt, "opus")


def judge_with_opus_46(prompt: str) -> dict | None:
    """Pinned Opus 4.6 judge — explicit cross-generation comparison row."""
    return judge_with_claude_cli(prompt, "claude-opus-4-6")


def judge_with_codex(prompt: str) -> dict | None:
    """Run GPT-5.4 as judge via codex exec CLI."""
    full_prompt = (
        f"{JUDGE_SYSTEM_PROMPT}\n\n---\n\n{prompt}\n\n"
        "Output ONLY the JSON object, no markdown fences, no explanation."
    )

    env = os.environ.copy()
    env.pop("CLAUDECODE", None)

    # Write prompt to temp file to avoid arg length limits
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as tmp:
        tmp.write(full_prompt)
        tmp_path = tmp.name

    # Use -o to capture last message to a file
    out_path = tempfile.mktemp(suffix=".txt")

    try:
        result = subprocess.run(
            [
                "codex",
                "exec",
                "-o",
                out_path,
                "-",  # Read prompt from stdin
            ],
            input=full_prompt,
            capture_output=True,
            text=True,
            env=env,
            timeout=300,
        )

        if result.returncode != 0:
            print(f"    Codex judge error: {result.stderr[:200]}")
            return None

        # Read output from the -o file
        if os.path.exists(out_path):
            with open(out_path) as f:
                content = f.read().strip()
        else:
            content = result.stdout.strip()
    finally:
        for p in [tmp_path, out_path]:
            try:
                os.unlink(p)
            except OSError:
                pass

    _emit_raw("codex", content)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        import re

        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    print(f"    Failed to parse Codex judge response: {content[:200]}")
    return None


def run_judges(results: dict[str, dict], user_prompt: str) -> dict:
    """Run dual-judge evaluation with blinded reports."""
    print("\n=== Phase 4: Judge Evaluation ===")

    # Randomize label assignment for blinding
    model_keys = list(results.keys())
    random.seed(42)  # Reproducible
    labels = [f"Report {chr(65 + i)}" for i in range(len(model_keys))]
    assignment = list(zip(labels, model_keys))
    random.shuffle(assignment)

    # Save the blinding key
    blinding = {label: model_key for label, model_key in assignment}
    with open(BENCHMARK_DIR / "blinding_key.json", "w") as f:
        json.dump(blinding, f, indent=2)
    print(f"  Blinding: {blinding}")

    # Three judges: Opus (alias → current), Opus 4.6 (pinned), GPT-5.4 (Codex).
    # Alias + pinned are deliberate: the alias row tells us what the "current
    # generation" is scoring today; the pinned row stays stable for
    # longitudinal comparison across future Claude releases.
    judge_results = {
        "opus_judge": {},            # alias → current Opus
        "opus_46_judge": {},         # pinned claude-opus-4-6
        "gpt54_judge": {},           # GPT-5.4 via codex exec
        "blinding": blinding,
    }

    for label, model_key in assignment:
        report_content = results[model_key]["content"]
        prompt = build_judge_prompt(user_prompt, report_content, label)

        def _score_and_composite(scores: dict | None, label_for_log: str, dest_key: str):
            if not scores:
                return
            judge_results[dest_key][model_key] = scores
            composite = sum(
                scores[dim]["score"] * JUDGE_RUBRIC[dim]["weight"]
                for dim in JUDGE_RUBRIC
                if dim in scores
            )
            print(f"    {label_for_log} -> composite: {composite:.1f}")

        print(f"  Opus (alias) judging {label} ({model_key})...")
        _score_and_composite(judge_with_opus(prompt), "Opus-current", "opus_judge")

        print(f"  Opus 4.6 (pinned) judging {label} ({model_key})...")
        _score_and_composite(judge_with_opus_46(prompt), "Opus-4.6", "opus_46_judge")

        print(f"  GPT-5.4 judging {label} ({model_key})...")
        _score_and_composite(judge_with_codex(prompt), "GPT-5.4", "gpt54_judge")

    with open(BENCHMARK_DIR / "judge_results.json", "w") as f:
        json.dump(judge_results, f, indent=2)

    return judge_results


# --- Phase 5: Analyze ---

def compute_composite(scores: dict) -> float:
    """Compute weighted composite score."""
    return sum(
        scores[dim]["score"] * JUDGE_RUBRIC[dim]["weight"]
        for dim in JUDGE_RUBRIC
        if dim in scores
    )


def analyze(
    results: dict[str, dict],
    prediction_scores: dict[str, dict],
    judge_results: dict,
) -> str:
    """Generate final analysis report."""
    print("\n=== Phase 5: Analysis ===")

    lines = [
        "# Psyche Model Comparison: " + " vs ".join(results.keys()),
        "",
        f"**Date**: {time.strftime('%Y-%m-%d')}",
        f"**Ground Truth Big Five**: N={GROUND_TRUTH['N']}, E={GROUND_TRUTH['E']}, "
        f"O={GROUND_TRUTH['O']}, A={GROUND_TRUTH['A']}, C={GROUND_TRUTH['C']}",
        "",
        "## Summary Table",
        "",
        "| Model | Prediction MAE | Evidence | Insight | Tension | Safety | Narrative | Composite | Cost/report | Latency |",
        "|-------|---------------|----------|---------|---------|--------|-----------|-----------|-------------|---------|",
    ]

    model_composites = {}
    model_order = list(results.keys())

    for model_key in model_order:
        pred = prediction_scores.get(model_key, {})
        mae = pred.get("mae", "N/A")
        acc = pred.get("accuracy_score", "N/A")

        # Average across judges
        dim_avgs = {}
        for dim in JUDGE_RUBRIC:
            scores_list = []
            for judge_name in ["opus_judge", "opus_46_judge", "gpt54_judge"]:
                judge_data = judge_results.get(judge_name, {}).get(model_key, {})
                if dim in judge_data:
                    scores_list.append(judge_data[dim]["score"])
            dim_avgs[dim] = sum(scores_list) / len(scores_list) if scores_list else 0

        composite = sum(
            dim_avgs[dim] * JUDGE_RUBRIC[dim]["weight"] for dim in JUDGE_RUBRIC
        )
        model_composites[model_key] = composite

        cost = results.get(model_key, {}).get("cost_usd", 0)
        latency = results.get(model_key, {}).get("latency_s", "N/A")

        lines.append(
            f"| {model_key} | {mae} | "
            f"{dim_avgs.get('evidence_integration', 0):.0f} | "
            f"{dim_avgs.get('insight_depth', 0):.0f} | "
            f"{dim_avgs.get('tension_identification', 0):.0f} | "
            f"{dim_avgs.get('clinical_safety', 0):.0f} | "
            f"{dim_avgs.get('narrative_quality', 0):.0f} | "
            f"{composite:.1f} | ${cost:.4f} | {latency}s |"
        )

    # Prediction accuracy detail
    lines.extend([
        "",
        "## Prediction Accuracy (Big Five MAE)",
        "",
        "| Model | N | E | O | A | C | MAE | Score |",
        "|-------|---|---|---|---|---|-----|-------|",
    ])
    for model_key in model_order:
        pred = prediction_scores.get(model_key, {})
        if pred.get("predictions"):
            preds = pred["predictions"]
            errors = pred["errors"]
            lines.append(
                f"| {model_key} | "
                + " | ".join(
                    f"{round(preds.get(d, 0))} (±{errors.get(d, 0):.0f})"
                    for d in ["N", "E", "O", "A", "C"]
                )
                + f" | {pred['mae']} | {pred['accuracy_score']} |"
            )
        else:
            lines.append(f"| {model_key} | — | — | — | — | — | FAILED | 0 |")

    lines.append(f"\n*Ground truth: N={GROUND_TRUTH['N']}, E={GROUND_TRUTH['E']}, O={GROUND_TRUTH['O']}, A={GROUND_TRUTH['A']}, C={GROUND_TRUTH['C']}*")

    # Inter-judge agreement
    lines.extend(["", "## Inter-Judge Agreement", ""])

    opus_rankings = []
    gpt_rankings = []
    for model_key in model_order:
        opus_data = judge_results.get("opus_judge", {}).get(model_key, {})
        gpt_data = judge_results.get("gpt54_judge", {}).get(model_key, {})
        if opus_data:
            opus_rankings.append(compute_composite(opus_data))
        else:
            opus_rankings.append(0)
        if gpt_data:
            gpt_rankings.append(compute_composite(gpt_data))
        else:
            gpt_rankings.append(0)

    # Spearman rank correlation (manual for 3 items)
    def rank(lst):
        sorted_indices = sorted(range(len(lst)), key=lambda i: lst[i], reverse=True)
        ranks = [0] * len(lst)
        for rank_val, idx in enumerate(sorted_indices):
            ranks[idx] = rank_val + 1
        return ranks

    opus_ranks = rank(opus_rankings)
    gpt_ranks = rank(gpt_rankings)
    n = len(opus_ranks)
    d_sq_sum = sum((o - g) ** 2 for o, g in zip(opus_ranks, gpt_ranks))
    spearman_rho = 1 - (6 * d_sq_sum) / (n * (n**2 - 1)) if n > 1 else 0

    lines.append(f"Spearman rho on {n}-model ranking: **{spearman_rho:.3f}** (target: >0.7)")
    lines.append("")
    lines.append("| Model | Opus Judge Composite | GPT-5.4 Judge Composite | Opus Rank | GPT Rank |")
    lines.append("|-------|---------------------|------------------------|-----------|----------|")
    for i, model_key in enumerate(model_order):
        lines.append(
            f"| {model_key} | {opus_rankings[i]:.1f} | {gpt_rankings[i]:.1f} "
            f"| {opus_ranks[i]} | {gpt_ranks[i]} |"
        )

    # Self-preference analysis
    lines.extend(["", "## Self-Preference Analysis", ""])

    # Claude self-preference: compare each Claude judge's score on its own
    # generation vs its score on all other Claude models.
    # - opus_judge (alias → current gen) scores "opus" model_key
    # - opus_46_judge (pinned 4.6) scores "opus-4.6-pinned" model_key
    # Cross-generation sibling scores (e.g. opus_judge on opus-4.6-pinned)
    # go into the "others" bucket — a different generation of the same
    # family is not "self".
    def _self_preference(judge_dict: dict, self_key: str, judge_label: str) -> None:
        if not judge_dict or self_key not in judge_dict:
            return
        own = compute_composite(judge_dict[self_key])
        others = [
            compute_composite(judge_dict[mk])
            for mk in judge_dict
            if mk != self_key
        ]
        if not others:
            return
        other_avg = sum(others) / len(others)
        gap = (own - other_avg) / 100
        flag = " **FLAGGED**" if abs(gap) > 0.05 else ""
        lines.append(
            f"- {judge_label} judge: own-model={own:.1f}, other-avg={other_avg:.1f}, "
            f"gap={gap:.3f}{flag}"
        )

    _self_preference(judge_results.get("opus_judge", {}), "opus", "Opus (current)")
    _self_preference(judge_results.get("opus_46_judge", {}), "opus-4.6-pinned", "Opus 4.6 (pinned)")
    lines.append(f"  (Chatledger baseline gap: 0.010; flagging threshold: >0.05)")

    # GPT judge: composites for reference (no GPT-generated report to check self-preference)
    gpt_judge = judge_results.get("gpt54_judge", {})
    if gpt_judge:
        gpt_composites = {mk: compute_composite(v) for mk, v in gpt_judge.items()}
        lines.append(f"- GPT-5.4 judge composites: {json.dumps({k: round(v, 1) for k, v in gpt_composites.items()})}")

    # Per-judge per-dimension detail
    lines.extend(["", "## Detailed Judge Scores", ""])
    for judge_name, judge_label in [
        ("opus_judge", "Opus (current)"),
        ("opus_46_judge", "Opus 4.6 (pinned)"),
        ("gpt54_judge", "GPT-5.4"),
    ]:
        lines.append(f"### {judge_label} Judge")
        lines.append("")
        lines.append("| Model | Evidence | Insight | Tension | Safety | Narrative | Composite |")
        lines.append("|-------|----------|---------|---------|--------|-----------|-----------|")
        for model_key in model_order:
            scores = judge_results.get(judge_name, {}).get(model_key, {})
            if scores:
                comp = compute_composite(scores)
                lines.append(
                    f"| {model_key} | "
                    + " | ".join(
                        str(scores.get(dim, {}).get("score", "—"))
                        for dim in JUDGE_RUBRIC
                    )
                    + f" | {comp:.1f} |"
                )
            else:
                lines.append(f"| {model_key} | — | — | — | — | — | — |")
        lines.append("")

    # Reasoning excerpts
    lines.extend(["## Judge Reasoning (Selected)", ""])
    for judge_name, judge_label in [
        ("opus_judge", "Opus (current)"),
        ("opus_46_judge", "Opus 4.6 (pinned)"),
        ("gpt54_judge", "GPT-5.4"),
    ]:
        lines.append(f"### {judge_label}")
        for model_key in model_order:
            scores = judge_results.get(judge_name, {}).get(model_key, {})
            if scores:
                lines.append(f"\n**{model_key}:**")
                for dim in JUDGE_RUBRIC:
                    if dim in scores and "reasoning" in scores[dim]:
                        lines.append(f"- {dim}: {scores[dim]['reasoning']}")
        lines.append("")

    # Cost comparison
    lines.extend(["## Cost Comparison", ""])
    lines.append("| Model | $/1M in | $/1M out | This report | Notes |")
    lines.append("|-------|---------|----------|-------------|-------|")
    for model_key in model_order:
        m = MODELS[model_key]
        cost = results.get(model_key, {}).get("cost_usd", 0)
        notes = "Max plan (free)" if m["provider"] == "claude-cli" else "DeepInfra"
        lines.append(
            f"| {model_key} | ${m['cost_in']:.2f} | ${m['cost_out']:.2f} | ${cost:.4f} | {notes} |"
        )

    # Qualitative notes placeholder
    lines.extend([
        "",
        "## Qualitative Review (User)",
        "",
        "*To be filled in after reading all 3 reports.*",
        "",
        "Key themes to evaluate:",
        "- Glass Pane metaphor (central interpersonal dynamic)",
        "- Dutifulness/Orderliness gap (92 vs 22)",
        "- Agreeableness discrepancy (self-report vs interview)",
        "- Interest cycling pattern",
        "- Wounded-animal crisis mode",
        "",
        "---",
        f"*Generated {time.strftime('%Y-%m-%d %H:%M')} by psyche/benchmark/run_eval.py*",
    ])

    report = "\n".join(lines)

    with open(BENCHMARK_DIR / "report.md", "w") as f:
        f.write(report)

    print(f"\nReport saved to benchmark/report.md ({len(report)} chars)")
    return report


# --- Main ---

def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    if phase.startswith("--phase="):
        phase = phase.split("=", 1)[1]
    elif phase.startswith("--phase"):
        phase = sys.argv[2] if len(sys.argv) > 2 else "all"

    if phase in ("prepare", "all"):
        system_prompt, user_prompt = prepare_input()
    else:
        with open(BENCHMARK_DIR / "prepared_input.json") as f:
            prepared = json.load(f)
        system_prompt = prepared["system_prompt"]
        user_prompt = prepared["user_prompt"]

    if phase in ("generate", "all"):
        results = generate_all(system_prompt, user_prompt)
    else:
        # Load from saved files
        results = {}
        for model_key in MODELS:
            path = REPORTS_DIR / f"{model_key}.json"
            if path.exists():
                with open(path) as f:
                    results[model_key] = json.load(f)

    if phase in ("score", "all"):
        prediction_scores = score_predictions(results)
    else:
        path = BENCHMARK_DIR / "prediction_scores.json"
        if path.exists():
            with open(path) as f:
                prediction_scores = json.load(f)
        else:
            prediction_scores = {}

    if phase in ("judge", "all"):
        judge_results = run_judges(results, user_prompt)
    else:
        path = BENCHMARK_DIR / "judge_results.json"
        if path.exists():
            with open(path) as f:
                judge_results = json.load(f)
        else:
            judge_results = {}

    if phase in ("analyze", "all"):
        analyze(results, prediction_scores, judge_results)

    print("\nDone!")


if __name__ == "__main__":
    main()
