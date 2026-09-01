"""Local file cache for SEC companyfacts JSON (PRD Section 17).

Avoids re-fetching a company's full XBRL facts payload from data.sec.gov
on every request; period switches for the same company reuse the cached
payload until it goes stale.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from . import extractor

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache" / "companyfacts"
TTL_SECONDS = 24 * 60 * 60  # 24 hours


def _cache_path(cik: str) -> Path:
    return CACHE_DIR / f"{cik.zfill(10)}.json"


def get_company_facts(cik: str, *, force_refresh: bool = False) -> dict:
    """Return companyfacts JSON for a CIK, serving from disk when fresh."""
    path = _cache_path(cik)

    if not force_refresh and path.exists():
        age = time.time() - path.stat().st_mtime
        if age < TTL_SECONDS:
            with path.open(encoding="utf-8") as f:
                return json.load(f)

    facts = extractor.fetch_sec_facts(cik)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(facts, f)
    return facts
