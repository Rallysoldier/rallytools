# rallytools

Personal Python utility toolkit for Rally Soldier.

## Quick start (editable install)

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

## Developer tools

- **ruff** for linting
- **black** for formatting
- **pytest** for tests
- **pre-commit** hooks

Install dev tools with:

```bash
pip install -e ".[dev]"
pre-commit install
```
