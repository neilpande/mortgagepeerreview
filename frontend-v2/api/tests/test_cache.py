import threading
import time

from app import cache


def test_get_company_facts_caches_and_avoids_refetching(monkeypatch):
    monkeypatch.setattr(cache, "_memory_cache", {})
    cik = "0001234567"

    calls = []

    def fake_fetch(cik):
        calls.append(cik)
        return {"facts": {"us-gaap": {"ok": True}}}

    monkeypatch.setattr(cache.extractor, "fetch_sec_facts", fake_fetch)

    first = cache.get_company_facts(cik)
    second = cache.get_company_facts(cik)

    assert first == {"facts": {"us-gaap": {"ok": True}}}
    assert second == first
    assert calls == [cik]  # second call served from memory, no refetch


def test_get_company_facts_refetches_after_ttl_expires(monkeypatch):
    monkeypatch.setattr(cache, "_memory_cache", {})
    monkeypatch.setattr(cache, "TTL_SECONDS", 0)
    cik = "0001234567"

    calls = []

    def fake_fetch(cik):
        calls.append(cik)
        return {"facts": {"call": len(calls)}}

    monkeypatch.setattr(cache.extractor, "fetch_sec_facts", fake_fetch)

    cache.get_company_facts(cik)
    cache.get_company_facts(cik)

    assert calls == [cik, cik]


def test_concurrent_requests_for_same_cik_dedupe_to_one_fetch(monkeypatch):
    # Regression test: overlapping requests for the same company hitting a
    # cold cache at the same time (different tabs, page reloads) used to
    # each launch their own SEC fetch, multiplying memory/network use.
    monkeypatch.setattr(cache, "_memory_cache", {})
    monkeypatch.setattr(cache, "_cik_locks", {})
    cik = "0001234567"

    fetch_count = []

    def fake_fetch(cik):
        fetch_count.append(cik)
        time.sleep(0.05)
        return {"facts": {"us-gaap": {"ok": True}}}

    monkeypatch.setattr(cache.extractor, "fetch_sec_facts", fake_fetch)

    errors = []

    def worker():
        try:
            cache.get_company_facts(cik)
        except Exception as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    assert fetch_count == [cik]


def test_get_all_company_facts_fetches_in_parallel_not_sequentially(monkeypatch):
    monkeypatch.setattr(cache, "_memory_cache", {})
    monkeypatch.setattr(cache, "_cik_locks", {})
    ciks = [f"000000000{i}" for i in range(5)]

    def slow_fetch(cik):
        time.sleep(0.2)
        return {"facts": {"cik": cik}}

    monkeypatch.setattr(cache.extractor, "fetch_sec_facts", slow_fetch)

    started = time.monotonic()
    results = cache.get_all_company_facts(ciks)
    elapsed = time.monotonic() - started

    assert len(results) == 5
    assert {r["facts"]["cik"] for r in results} == set(ciks)
    # Sequential would take ~1.0s (5 x 0.2s); parallel should be close to
    # a single fetch's duration.
    assert elapsed < 0.6
