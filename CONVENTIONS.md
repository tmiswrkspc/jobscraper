# Coding Conventions

Follow these conventions exactly when adding or modifying code. They are already consistently applied across the codebase — all new code must match.

---

## Naming

| Element | Convention | Example |
|---|---|---|
| Variables | `snake_case` | `job_records`, `api_key`, `normalized_url` |
| Functions | `snake_case()` | `search_jobs()`, `deduplicate_jobs()` |
| Private methods | `_leading_underscore()` | `_normalize_results()`, `_search_jobs_endpoint()` |
| Classes | `PascalCase` | `SerperJobScraper`, `SerperAPI` |
| Constants | `UPPER_SNAKE_CASE` | `SEARCH_QUERIES`, `FUZZY_SIMILARITY_THRESHOLD` |
| Python files | `lowercase_with_underscores.py` | `serper_api.py`, `deduplicator.py` |
| Markdown docs | `UPPERCASE.md` | `README.md`, `ARCHITECTURE.md` |
| Output files | `{type}_{timestamp}.{ext}` | `jobs_20260309_143052.json` |

---

## Type Hints

Always use type hints on all function signatures. Import from `typing` for `List`, `Dict`, `Tuple`, `Optional`.

```python
from typing import List, Dict, Tuple, Optional

def search_jobs(
    self,
    query: str,
    location: str = "Bangalore, India",
    num_results: int = 10
) -> List[Dict]:
```

---

## Docstrings

Use Google-style docstrings on all public functions and classes.

```python
def deduplicate_jobs(jobs: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Remove duplicate job listings using two-phase algorithm.

    Args:
        jobs: List of raw job dictionaries from API

    Returns:
        Tuple of (unique_jobs list, stats dict)
    """
```

Private methods (`_leading_underscore`) may use shorter inline comments instead.

---

## Logging

Every module gets its own logger via `__name__`. Use the appropriate level — don't log everything at `info`.

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed trace info")
logger.info("Normal operational message")
logger.warning("Something unexpected but recoverable")
logger.error("Operation failed: {e}")
```

---

## Error Handling

Catch exceptions, log them, and return empty collections. Never propagate unhandled exceptions from API calls. Never return `None` where a list is expected.

```python
try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
except Exception as e:
    logger.error(f"API call failed: {e}")
    return []  # Always return empty list, not None
```

---

## String Formatting

Use f-strings. Do not use `%` formatting or `.format()`.

```python
# Correct
logger.info(f"Found {len(jobs)} jobs for query: {query}")

# Wrong
logger.info("Found %d jobs" % len(jobs))
logger.info("Found {} jobs".format(len(jobs)))
```

---

## Import Order

Standard library → third-party → local modules. One import per line. No wildcard imports.

```python
# Standard library
import os
import logging
import json
import csv
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from difflib import SequenceMatcher
from urllib.parse import urlparse, urlunparse

# Third-party
import requests
from dotenv import load_dotenv

# Local
from serper_api import SerperAPI
from deduplicator import deduplicate_jobs
from config import SEARCH_QUERIES, OUTPUT_DIR
```

---

## File Paths

Use `pathlib.Path` for all file operations. Never use string concatenation for paths.

```python
from pathlib import Path

Path(OUTPUT_DIR).mkdir(exist_ok=True)
json_path = Path(OUTPUT_DIR) / f"jobs_{timestamp}.json"
```

---

## List Operations

Prefer list comprehensions and generator expressions over explicit loops where readable.

```python
with_salary = sum(1 for job in jobs if job.get('salary'))
filtered = [job for job in jobs if job.get('title')]
```

---

## Configuration

- All constants belong in `config.py` — no magic numbers or hardcoded strings anywhere else
- API keys and secrets always come from `.env` via `os.getenv()`
- Never hardcode credentials, URLs, or thresholds in module logic

---

## Anti-Patterns — Never Do These

- ❌ Global mutable state — use class instances
- ❌ Hardcoded API keys or credentials
- ❌ Silent failures — always log errors
- ❌ Magic numbers — give them a named constant in `config.py`
- ❌ Nesting deeper than 3 levels
- ❌ Wildcard imports (`from module import *`)
- ❌ Relative imports — always use absolute imports
- ❌ Returning `None` where a list or dict is expected
