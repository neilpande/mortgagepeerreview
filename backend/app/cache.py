"""Local file cache for SEC companyfacts JSON (PRD Section 17).

Avoids re-fetching a company's full XBRL facts payload from data.sec.gov
on every request; period switches for the same company reuse the cached
payload until it goes stale.
"""

from __future__ import annotations

import json
import os
import time
import uuid
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
            try:
                with path.open(encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                # A previous write was interrupted (e.g. the process was
                # killed mid-write) and left a truncated/corrupt file.
                # Treat it as a cache miss and refetch rather than letting
                # every subsequent request crash on the same broken file.
                pass

    facts = extractor.fetch_sec_facts(cik)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Write atomically: a reader can never observe a partially-written
    # file, because os.replace is a single filesystem operation -- a
    # process killed mid-write leaves the *temp* file damaged, never the
    # cache file readers actually use. The temp filename includes a random
    # token so concurrent requests for the same CIK (e.g. multiple tabs
    # loading at once) never race on the same temp path.
    tmp_path = path.with_suffix(f".{uuid.uuid4().hex}.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(facts, f)

    # On Windows, os.replace can transiently fail with PermissionError if
    # another thread has `path` open for reading at that exact instant
    # (POSIX allows replacing an open file; Windows doesn't) -- retry
    # briefly rather than surfacing a spurious error under concurrency.
    for attempt in range(5):
        try:
            os.replace(tmp_path, path)
            break
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.05)

    return facts
