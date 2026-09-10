# Fact-Check Report: PsycheEval v0.2

**Post**: 046-psycheeval-v0_2  
**Checked**: 2026-05-18  
**Model**: GPT-5.5 (xhigh reasoning) via Codex MCP  
**Claims Extracted**: 3 external claims + 1 internal reference

---

## Summary

| Verdict | Count | Claims |
|---------|-------|--------|
| Verified | 2 | Zheng et al. 2023, Shi et al. 2024 |
| Misleading | 1 | AB/BA as "standard correction" |
| Author's Data | 1+ | All internal PsycheEval v0.2 results |
| Reference Verified | 1 | Internal link to post 044 |

**Overall Assessment**: **PASS WITH CAVEATS** — External citations are accurate. One framing needs nuance. All internal claims are author's own data and cannot be externally verified; methodology descriptions are coherent and self-consistent.

---

## Critical Issues (Must Fix)

None. No inaccurate or misleading claims that block publication.

---

## Cautions (Should Review)

### Claim: "the standard correction is counterbalanced AB/BA rejudging"

**Status**: MISLEADING (Overstated Generality)

**What's accurate**:
- AB/BA counterbalancing is a **common first-line mitigation** for position bias in LLM judging
- Zheng et al. (2023) explicitly recommend calling the judge twice with swapped order
- It is standard practice in evaluation frameworks (LangSmith, OpenAI's eval guidance)

**What's misleading**:
- The phrasing "the standard correction" suggests AB/BA fully solves position bias
- Shi et al. (2024) and later work document that AB/BA **reduces** but **does not fully eliminate** position bias
- The safer framing is: "a common mitigation" or "a standard first-pass check" rather than "the standard correction"

**Evidence**:
- Zheng et al. 2023, arXiv:2306.05685 — "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS). Recommends "swap answer order and check consistency."
- Shi et al. 2024, arXiv:2406.07791 — "Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge." Shows AB/BA reduces bias but notes inconsistency-as-a-tie does NOT fully debiase.
- LangSmith docs: https://docs.langsmith.com/langsmith/evaluate-pairwise (exposes `randomize_order`)
- OpenAI eval guidance: https://platform.openai.com/docs/guides/evaluation-best-practices (lists position bias as known challenge)

**Recommendation**: Change "the standard correction" to "a standard first-pass mitigation" or "a common check." The post's actual use of AB/BA is sound; the framing just overstates generality. Example revision:

> "the standard first-pass mitigation is counterbalanced AB/BA rejudging..."

Or acknowledge the limitation:

> "the common mitigation is counterbalanced AB/BA rejudging — a necessary but not fully sufficient check..."

The post's methodology of using AB/BA is exactly right; the framing just needs precision.

---

## Verified Claims

| # | Claim | Source | Notes |
|---|-------|--------|-------|
| 1 | Zheng et al. (2023) documents position bias in LLM-as-judge | arXiv:2306.05685 / NeurIPS 2023 Datasets & Benchmarks Track | Title: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." Authorship and year correct. ✓ |
| 2 | Shi et al. 2024, "Judging the Judges" documents position bias in LLM judging | arXiv:2406.07791 (2024 preprint) / AACL-IJCNLP 2025 (published version) | Full title: "Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge." Authorship and year correct. ✓ |
| 3 | AB/BA counterbalancing is a recognized mitigation for position bias | Multiple sources (Zheng, Shi, LangSmith, OpenAI) | Post correctly applies the technique; framing just overstates as "the standard correction." ✓ |
| 4 | Post references "/posts/044-what-the-wiki-router-found" | File exists: `~/claudeworkspace/applications/ashitaorbis/shared/content/posts/044-what-the-wiki-router-found.md` | Internal link is valid and the post exists. ✓ |

---

## Author's Data & Internal Methodology

The post makes extensive claims about the PsycheEval v0.2 corpus, results, and analyses. These are **author's own data** and cannot be externally verified. Spot-checks for coherence:

| Aspect | Assessment |
|--------|-----------|
| **Methodological coherence** | ✓ COHERENT. The experimental design (C0–C5_CONTRACT conditions, AB/BA rejudging, per-judge breakdowns, bootstrap CIs) is internally consistent and standard to evaluation research. |
| **Statistical reporting** | ✓ CONSISTENT. Win rates, CIs, deltas, and per-judge numbers are reported consistently across tables and text. |
| **Audit pipeline description** | ✓ COHERENT. Three same-data audits (scalar–pairwise reconciliation, leave-one-out fragility, length matching) + AB/BA new-data audit all fit together logically. |
| **Retraction narrative** | ✓ LOGICAL. The story (headline predicts one outcome → audits predict collapse → AB/BA confirms) is internally consistent with no contradictions detected. |
| **Model names** | ✓ ACCURATE. GPT-5.4, GPT-5.5-xhigh, Opus 4.7 are correct model designations as of 2026-05 per `~/.claude/CLAUDE.md`. |

---

## Methodology Notes

- **Codex session ID**: 019e3d23-3964-7bc3-8fdf-cca350a9c999
- **Search strategy**: Web search for Zheng et al. 2023 and Shi et al. 2024 position-bias papers; verification of AB/BA as standard practice
- **Follow-up queries**: 1 (clarification on whether AB/BA is "standard correction" or "common mitigation")
- **Known limitations**: Cannot verify the internal PsycheEval results; all internal claims are author's own work. Spot-checked methodology descriptions for coherence rather than ground truth.

---

## Verdict

**READY FOR PUBLICATION WITH ONE FRAMING ADJUSTMENT**

The post is factually sound on external claims and methodologically coherent on internal claims. The only issue is the framing of AB/BA as "the standard correction" — change to "a standard first-pass mitigation" or similar qualifier to avoid overstating generality.

All author's data (results, analyses, statistics) cannot be externally verified but are internally consistent and clearly attributed as the author's own findings.
