"""Export JSON Schema for every pydantic model to schemas/.

Run as: uv run python -m psycheeval.export_schemas
"""

from __future__ import annotations

import json
from pathlib import Path

from psycheeval.models import ALL_MODELS

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"


def export_all() -> list[Path]:
    SCHEMAS_DIR.mkdir(exist_ok=True)
    written: list[Path] = []
    for model in ALL_MODELS:
        schema = model.model_json_schema()
        snake = _camel_to_snake(model.__name__)
        out = SCHEMAS_DIR / f"{snake}.schema.json"
        out.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")
        written.append(out)
    return written


def _camel_to_snake(name: str) -> str:
    out: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and not name[i - 1].isupper():
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


if __name__ == "__main__":
    paths = export_all()
    print(f"Wrote {len(paths)} schema files to {SCHEMAS_DIR}")
    for p in paths:
        print(f"  {p.name}")
