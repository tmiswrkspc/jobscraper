# AGENTS

Instructions for AI agents (Kiro, Claude, Copilot) working in this repository.

---

## Understand Before You Change

Read these files before making structural changes:
- `ARCHITECTURE.md` — module relationships and data flow
- `DECISIONS.md` — why key choices were made (especially ADR-001 through ADR-007)
- `CONVENTIONS.md` — naming, patterns, import order

---

## What You Can Do Freely

- Add new search queries to `SEARCH_QUERIES` in `config.py`
- Add new helper methods to existing classes (follow naming conventions)
- Add logging statements
- Add docstrings or comments
- Write new tests in `test_api.py` or a new `tests/` directory
- Fix bugs in deduplication logic
- Improve error messages
- Add new export formats (e.g., Excel) — write to `output/`, follow timestamp naming

---

## What Requires Discussion First

- Adding new Python dependencies (keep the footprint minimal)
- Changing the job dict schema (field names or types break exports)
- Adding a database or any persistent storage mechanism
- Creating new Python modules (flat structure is intentional)
- Adding async/await patterns
- Changing `FUZZY_SIMILARITY_THRESHOLD` below 0.85

---

## What You Must Never Do

- **Do not hardcode `SERPER_API_KEY`** — it must always come from `.env`
- **Do not revert to browser scraping** — the Serper API migration was deliberate (see ADR-001)
- **Do not change the output file naming pattern** — `{type}_{timestamp}.{ext}`
- **Do not add constants to any module other than `config.py`**
- **Do not use wildcard imports** (`from module import *`)
- **Do not return `None` where a list or dict is expected** — return empty collections
- **Do not raise exceptions from API calls** — catch, log, return empty list (see ADR-007)
- **Do not commit `.env`, `venv/`, or `output/`** — all are gitignored

---

## Code Style Rules

- Python 3.8+ compatible syntax
- Type hints on all public function signatures
- Google-style docstrings on all public functions
- f-strings only (no `%` or `.format()`)
- Import order: stdlib → third-party → local
- `pathlib.Path` for all file paths
- `logging.getLogger(__name__)` in every module

---

## When Adding Features

1. Put constants in `config.py`
2. Put business logic in the most relevant existing module
3. Only create a new module if it has a single, clearly distinct responsibility
4. Update `ARCHITECTURE.md` if you change module relationships
5. Update `DECISIONS.md` if you make a significant architectural choice

---

## Testing

- There is no automated test suite (yet)
- `test_api.py` is a manual connectivity test — keep it working
- When adding tests, use `pytest` and place them in `tests/`
- Test `deduplicator.py` first — it has the most isolated, testable logic
