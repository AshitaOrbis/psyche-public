#!/usr/bin/env python3
"""Generate synthetic GRM item banks for CAT development/testing.

These use literature-typical discrimination and threshold parameters
for personality assessment items. Replace with SAPA-extracted parameters
for production use (see extract_irt_params.R).

Discrimination values: 0.8-1.8 (typical for personality items)
Thresholds: Ordered from negative to positive, spanning ~[-2, 2]
"""

import json
import random
from pathlib import Path

random.seed(42)

FACETS_BIG5 = {
    "N": [("N1", "Anxiety"), ("N2", "Anger"), ("N3", "Depression"),
          ("N4", "Self-Consciousness"), ("N5", "Immoderation"), ("N6", "Vulnerability")],
    "E": [("E1", "Friendliness"), ("E2", "Gregariousness"), ("E3", "Assertiveness"),
          ("E4", "Activity Level"), ("E5", "Excitement-Seeking"), ("E6", "Cheerfulness")],
    "O": [("O1", "Imagination"), ("O2", "Artistic Interests"), ("O3", "Emotionality"),
          ("O4", "Adventurousness"), ("O5", "Intellect"), ("O6", "Liberalism")],
    "A": [("A1", "Trust"), ("A2", "Morality"), ("A3", "Altruism"),
          ("A4", "Cooperation"), ("A5", "Modesty"), ("A6", "Sympathy")],
    "C": [("C1", "Self-Efficacy"), ("C2", "Orderliness"), ("C3", "Dutifulness"),
          ("C4", "Achievement-Striving"), ("C5", "Self-Discipline"), ("C6", "Cautiousness")],
}

FACETS_HEXACO = {
    "HH": [("HH1", "Sincerity"), ("HH2", "Fairness"), ("HH3", "Greed-Avoidance"), ("HH4", "Modesty")],
    "EM": [("EM1", "Fearfulness"), ("EM2", "Anxiety"), ("EM3", "Dependence"), ("EM4", "Sentimentality")],
    "EX": [("EX1", "Social Self-Esteem"), ("EX2", "Social Boldness"), ("EX3", "Sociability"), ("EX4", "Liveliness")],
    "AG": [("AG1", "Forgiveness"), ("AG2", "Gentleness"), ("AG3", "Flexibility"), ("AG4", "Patience")],
    "CO": [("CO1", "Organization"), ("CO2", "Diligence"), ("CO3", "Perfectionism"), ("CO4", "Prudence")],
    "OP": [("OP1", "Aesthetic Appreciation"), ("OP2", "Inquisitiveness"), ("OP3", "Creativity"), ("OP4", "Unconventionality")],
}

ITEMS_PER_FACET = 15  # Enough for CAT to have a deep pool


def generate_thresholds() -> list[float]:
    """Generate 4 ordered thresholds for 5-point Likert."""
    base = sorted([random.gauss(0, 1) for _ in range(4)])
    # Ensure minimum spacing of 0.3
    for i in range(1, len(base)):
        if base[i] - base[i - 1] < 0.3:
            base[i] = base[i - 1] + 0.3
    return [round(b, 4) for b in base]


def generate_item(facet_id: str, facet_name: str, item_num: int, reverse: bool = False) -> dict:
    disc = round(random.uniform(0.8, 1.8), 4)
    thresholds = generate_thresholds()
    return {
        "id": f"CAT-{facet_id}-{item_num:03d}",
        "text": f"[{facet_name} item {item_num}]",  # Placeholder
        "dimensionId": facet_id,
        "dimensionName": facet_name,
        "reverse": reverse,
        "discrimination": disc,
        "thresholds": thresholds,
        "numCategories": 5,
    }


def generate_bank(facets: dict[str, list[tuple[str, str]]]) -> list[dict]:
    items = []
    for domain, domain_facets in facets.items():
        for facet_id, facet_name in domain_facets:
            for i in range(1, ITEMS_PER_FACET + 1):
                reverse = i % 3 == 0  # ~33% reversed
                items.append(generate_item(facet_id, facet_name, i, reverse))
    return items


if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent.parent / "web" / "public" / "item-banks"
    output_dir.mkdir(parents=True, exist_ok=True)

    big5 = generate_bank(FACETS_BIG5)
    hexaco = generate_bank(FACETS_HEXACO)

    big5_path = output_dir / "big5-grm-params.json"
    hexaco_path = output_dir / "hexaco-grm-params.json"

    big5_path.write_text(json.dumps(big5, indent=2))
    hexaco_path.write_text(json.dumps(hexaco, indent=2))

    print(f"Big Five: {len(big5)} items -> {big5_path}")
    print(f"HEXACO:   {len(hexaco)} items -> {hexaco_path}")
