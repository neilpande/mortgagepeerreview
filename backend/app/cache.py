"""Local file cache for SEC companyfacts JSON (PRD Section 17).

Avoids re-fetching a company's full XBRL facts payload from data.sec.gov
on every request; period switches for the same company reuse the cached
payload until it goes stale.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Sequence

from . import extractor

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache" / "companyfacts"
TTL_SECONDS = 24 * 60 * 60  # 24 hours

# Per-CIK locks so concurrent requests for the same company (e.g. two
# people loading the dashboard, or two tabs, at the same moment the cache
# is cold) serialize onto a single SEC fetch instead of each launching
# their own -- important on a memory-constrained host, where several
# redundant concurrent fetches at once is what was tipping the process
# over. A dict-building lock guards lazily creating each CIK's lock.
_cik_locks: dict[str, threading.Lock] = {}
_cik_locks_guard = threading.Lock()


def _lock_for(cik: str) -> threading.Lock:
    with _cik_locks_guard:
        return _cik_locks.setdefault(cik, threading.Lock())


def _cache_path(cik: str) -> Path:
    return CACHE_DIR / f"{cik.zfill(10)}.json"


def get_company_facts(cik: str, *, force_refresh: bool = False) -> dict:
    """Return companyfacts JSON for a CIK, serving from disk when fresh."""
    with _lock_for(cik):
        return _get_company_facts_locked(cik, force_refresh=force_refresh)


def _get_company_facts_locked(cik: str, *, force_refresh: bool) -> dict:
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

    logger.info("Fetching fresh SEC companyfacts for CIK %s", cik)
    started = time.monotonic()
    try:
        facts = extractor.fetch_sec_facts(cik)
    except Exception:
        logger.exception(
            "SEC fetch failed for CIK %s after %.1fs", cik, time.monotonic() - started
        )
        raise
    logger.info("Fetched SEC companyfacts for CIK %s in %.1fs", cik, time.monotonic() - started)

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


def get_all_company_facts(ciks: Sequence[str]) -> list[dict]:
    """Return companyfacts for every given CIK, fetching any cache misses
    in parallel rather than one at a time.

    Every peer-group request loops all 7 companies; fetching cold-cache
    misses sequentially took ~40s each (SEC's response time from this
    host, not a hang), so a fully-cold request could take several
    minutes end to end. Fetching in parallel bounds the total time by the
    slowest single company instead of their sum.
    """
    with ThreadPoolExecutor(max_workers=max(len(ciks), 1)) as executor:
        return list(executor.map(get_company_facts, ciks))
