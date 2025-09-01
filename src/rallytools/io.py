from __future__ import annotations
from pathlib import Path
import json
from typing import Any

def _p(path: str | Path) -> Path:
    return path if isinstance(path, Path) else Path(path)

def read_text(path: str | Path, *, encoding: str = "utf-8") -> str:
    """Read a UTF-8 text file."""
    return _p(path).read_text(encoding=encoding)

def write_text(path: str | Path, data: str, *, encoding: str = "utf-8", newline: str = "\n") -> None:
    """Write text atomically (best-effort) with newline normalization."""
    p = _p(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(data.replace("\r\n", "\n").replace("\r", "\n").replace("\n", newline), encoding=encoding)
    tmp.replace(p)

def read_json(path: str | Path, *, encoding: str = "utf-8") -> Any:
    """Read JSON file with UTF-8."""
    with _p(path).open("r", encoding=encoding) as f:
        return json.load(f)

def write_json(path: str | Path, data: Any, *, encoding: str = "utf-8", indent: int = 2) -> None:
    """Write JSON file with stable formatting."""
    p = _p(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with tmp.open("w", encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=indent, sort_keys=True)
        f.write("\n")
    tmp.replace(p)
