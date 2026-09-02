"""In-memory cache for SEC companyfacts JSON (PRD Section 17).

Avoids re-fetching a company's full XBRL facts payload from data.sec.gov
on every request within a warm serverless instance; period switches for
the same company reuse the cached payload until it goes stale.

Deliberately not disk-backed: Vercel Functions don't guarantee a
persistent, shared filesystem across invocations, so a disk cache would
be unreliable at best and (as happened when this ran on a traditional
host) a source of real corruption/race bugs at worst. An in-memory dict
scoped to the process gets the same benefit across a warm container's
lifetime with none of that complexity -- a cold container just refetches,
which the parallel/deduped fetch below keeps fast.
"""

from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Sequence

from . import extractor

logger = logging.getLogger(__name__)

TTL_SECONDS = 24 * 60 * 60  # 24 hours

_memory_cache: dict[str, tuple[float, dict]] = {}

# Per-CIK locks so concurrent requests for the same company (e.g. two tabs
# loading at once, or two people hitting a cold cache together) serialize
# onto a single SEC fetch instead of each launching their own.
_cik_locks: dict[str, threading.Lock] = {}
_cik_locks_guard = threading.Lock()


def _lock_for(cik: str) -> threading.Lock:
    with _cik_locks_guard:
        return _cik_locks.setdefault(cik, threading.Lock())


def get_company_facts(cik: str, *, force_refresh: bool = False) -> dict:
    """Return companyfacts JSON for a CIK, serving from memory when fresh."""
    with _lock_for(cik):
        if not force_refresh and cik in _memory_cache:
            cached_at, facts = _memory_cache[cik]
            if time.time() - cached_at < TTL_SECONDS:
                return facts

        logger.info("Fetching fresh SEC companyfacts for CIK %s", cik)
        started = time.monotonic()
        try:
            facts = extractor.fetch_sec_facts(cik)
        except Exception:
            logger.exception(
                "SEC fetch failed for CIK %s after %.1fs", cik, time.monotonic() - started
            )
            raise
        logger.info(
            "Fetched SEC companyfacts for CIK %s in %.1fs", cik, time.monotonic() - started
        )

        _memory_cache[cik] = (time.time(), facts)
        return facts


def get_all_company_facts(ciks: Sequence[str]) -> list[dict]:
    """Return companyfacts for every given CIK, fetching any cache misses
    in parallel rather than one at a time.

    Every peer-group request loops all 7 companies; fetching cold-cache
    misses sequentially can take tens of seconds each, so a fully-cold
    request could take minutes end to end. Fetching in parallel bounds the
    total time by the slowest single company instead of their sum.
    """
    with ThreadPoolExecutor(max_workers=max(len(ciks), 1)) as executor:
        return list(executor.map(get_company_facts, ciks))
