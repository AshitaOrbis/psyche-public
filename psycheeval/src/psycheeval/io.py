"""JSONL I/O helpers with pydantic validation."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def read_jsonl(path: Path, model: type[T]) -> Iterator[T]:
    """Yield validated model instances from a JSONL file."""
    with path.open() as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield model.model_validate_json(line)
            except Exception as e:
                raise ValueError(f"{path}:{i} failed validation: {e}") from e


def write_jsonl(path: Path, items: Iterable[BaseModel], *, append: bool = False) -> int:
    """Write models as JSONL. Returns count written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    count = 0
    with path.open(mode) as fh:
        for item in items:
            fh.write(item.model_dump_json())
            fh.write("\n")
            count += 1
    return count


def append_jsonl(path: Path, item: BaseModel) -> None:
    """Atomic-line append. Single write() with embedded newline is atomic
    under O_APPEND for payloads < PIPE_BUF (4096 bytes on Linux). Required
    when multiple processes append to the same file (e.g. parallel codex
    and opus judge pipelines writing anchored_judge_scores.jsonl)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(item.model_dump_json() + "\n")
