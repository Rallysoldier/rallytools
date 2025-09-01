# rallytools

Personal Python utility toolkit for Rally Soldier. A modern, src-layout package you can import anywhere:

```python
import rallytools as rt
```

---

## Requirements
- **Python**: 3.11+
- **pip** and **venv** (or your preferred environment manager)

The repo includes optional dev tooling: **ruff** (lint), **black** (format), **pytest** (tests), and **pre-commit** hooks.

---

## Quick start (editable install)

Use this when you’re actively developing `rallytools` and want changes to reflect immediately in consumers.

```bash
# From the repo root (where pyproject.toml lives)
python -m venv .venv
. .venv/Scripts/activate  # on Windows
# or: source .venv/bin/activate

pip install -U pip
pip install -e ".[dev]"
```

Then in any script:

```python
import rallytools as rt

log = rt.get_logger(__name__)
log.info("Hello from rallytools")
```

---

## Layout

```text
rallytools/
├─ pyproject.toml
├─ README.md
├─ LICENSE
├─ src/
│  └─ rallytools/
│     ├─ __init__.py
│     ├─ log.py
│     ├─ io.py
│     └─ time.py
└─ tests/
   └─ test_smoke.py
```

- **src layout** ensures imports resolve as the *installed* package, preventing accidental local imports.

---

## Developer tools

- **ruff** for linting
- **black** for formatting
- **pytest** for tests
- **pre-commit** hooks

Install and enable dev tools:

```bash
pip install -e ".[dev]"
pre-commit install
```

Useful commands:

```bash
pre-commit run --all-files
ruff check src tests --fix
black src tests
pytest -q
```

---

## Using rallytools in other projects

Choose the approach that matches your workflow.

### 1) Editable install (best during active dev)
```bash
# in the consumer project's venv
pip install -e "C:/path/to/rallytools"   # Windows example
# or: pip install -e "/home/you/rallytools"
```

### 2) Install from a local build (wheel/SDist)
Use this for a reproducible, frozen snapshot.

```bash
# build in the rallytools repo (see next section)
pip install -U "C:/path/to/rallytools/dist/rallytools-<version>-py3-none-any.whl"
```

### 3) Install from Git (tag or commit)
In the consumer’s `pyproject.toml`:

```toml
[project.dependencies]
rallytools = { url = "git+https://your.git.host/you/rallytools.git@v0.1.2" }
# or pin to a commit SHA:
# rallytools = { url = "git+https://your.git.host/you/rallytools.git@<sha>" }
```

Then in the consumer environment:

```bash
pip install -U .
```

---

## Building a release (wheel/SDist)

From the `rallytools` repo root:

```bash
# 1) Ensure clean working tree and tests pass
pytest -q
pre-commit run --all-files

# 2) Install the build backend (once)
python -m pip install -U build

# 3) Build artifacts
python -m build
# Outputs to ./dist/:
#   - rallytools-<version>-py3-none-any.whl
#   - rallytools-<version>.tar.gz
```

**Install the built wheel** into any environment:

```bash
pip install -U dist/rallytools-<version>-py3-none-any.whl
```

---

## Versioning & releases

- Use **SemVer**: `MAJOR.MINOR.PATCH` (e.g., `0.1.0` → `0.1.1` for a bugfix).
- Version currently appears in two places:
  - `pyproject.toml` → `[project].version`
  - `src/rallytools/__init__.py` → `__version__`
- **Keep them in sync** when bumping.

Typical release flow:

```bash
# 1) Bump versions (pyproject + __init__.py)
git add -A
git commit -m "chore: bump version to 0.X.Y"

# 2) Tag (optional but recommended)
git tag -a v0.X.Y -m "rallytools v0.X.Y"
git push --follow-tags

# 3) Build artifacts
python -m build
```

> **Optional improvement (single-source version):**
> Replace the hardcoded `__version__` in `__init__.py` with:
> ```python
> from importlib.metadata import version, PackageNotFoundError
> try:
>     __version__ = version("rallytools")
> except PackageNotFoundError:
>     __version__ = "0.0.0"
> ```
> Then the truth lives only in `pyproject.toml`.

---

## Adding new utilities

1. Create a new module under `src/rallytools/` (e.g., `paths.py`, `subproc.py`, `presentmon.py`).
2. Write typed, documented functions with small examples.
3. Export chosen functions in `src/rallytools/__init__.py` to make them available via `import rallytools`.
4. Add tests under `tests/`.
5. Run `ruff`, `black`, and `pytest` before committing.

Example test:

```python
def test_new_helper_roundtrip(tmp_path):
    from rallytools import write_text, read_text
    p = tmp_path / "note.txt"
    write_text(p, "hi\n")
    assert read_text(p) == "hi\n"
```

---

## Included utilities

### Logging (`log.py`)

```python
import rallytools as rt

rt.setup_logging("INFO")           # level can be int or string; use json=True for JSONL
log = rt.get_logger(__name__)
log.info("hello")
```

### IO helpers (`io.py`)

```python
from rallytools import read_text, write_text, read_json, write_json

write_text("notes.txt", "hi\n")
print(read_text("notes.txt"))

write_json("data.json", {"a": 1})
print(read_json("data.json")["a"])
```

### Timing (`time.py`)

```python
from rallytools import timeit, Timer

@timeit
def work():
    ...

work()
print(work.last_runtime)

with Timer() as t:
    ...
print(t.elapsed)
```

---

## Troubleshooting

**Editable install doesn’t seem to pick up changes**
- Ensure you installed with `pip install -e .` from the repo root.
- If using multiple venvs, confirm you’re in the expected one.
- Restart long-running interpreters (e.g., notebooks, daemons).

**`ModuleNotFoundError: rallytools`**
- Confirm the `src/` layout and that `pyproject.toml` has:
  ```toml
  [tool.setuptools.packages.find]
  where = ["src"]
  ```
- Reinstall: `pip install -e .`

**Pre-commit not found**
- `pip install pre-commit` in your venv, then `pre-commit install`.

**Wheel build fails**
- Ensure `build` is installed: `python -m pip install -U build`.
- Delete `dist/` and retry; also check for syntax errors via `ruff`/`pytest`.

**Windows paths with spaces**
- Quote paths: `pip install -e "C:\Path With Spaces\rallytools"`.

---

## License
MIT © Rally Soldier
