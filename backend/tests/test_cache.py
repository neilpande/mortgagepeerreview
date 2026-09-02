import json
import threading

from app import cache


def test_get_company_facts_self_heals_from_corrupt_cache_file(monkeypatch, tmp_path):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    cik = "0001234567"
    path = cache._cache_path(cik)
    path.write_text('{"facts": {"broken', encoding="utf-8")  # truncated JSON

    calls = []

    def fake_fetch(cik):
        calls.append(cik)
        return {"facts": {"us-gaap": {}}}

    monkeypatch.setattr(cache.extractor, "fetch_sec_facts", fake_fetch)

    result = cache.get_company_facts(cik)

    assert result == {"facts": {"us-gaap": {}}}
    assert calls == [cik]
    # The cache file on disk is now valid, atomically replaced.
    assert json.loads(path.read_text(encoding="utf-8")) == {"facts": {"us-gaap": {}}}


def test_get_company_facts_serves_valid_cache_without_refetching(monkeypatch, tmp_path):
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    cik = "0001234567"
    path = cache._cache_path(cik)
    path.write_text(json.dumps({"facts": {"us-gaap": {"ok": True}}}), encoding="utf-8")

    def fail_fetch(cik):
        raise AssertionError("should not refetch a valid, fresh cache file")

    monkeypatch.setattr(cache.extractor, "fetch_sec_facts", fail_fetch)

    result = cache.get_company_facts(cik)

    assert result == {"facts": {"us-gaap": {"ok": True}}}


def test_concurrent_cache_misses_for_same_cik_dont_race(monkeypatch, tmp_path):
    # Regression test: two requests for the same CIK hitting a cold cache
    # at the same time (e.g. two tabs loading together) used to race on a
    # shared, non-unique temp filename, so one's os.replace could steal
    # the other's temp file out from under it (FileNotFoundError).
    monkeypatch.setattr(cache, "CACHE_DIR", tmp_path)
    cik = "0001234567"

    def fake_fetch(cik):
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
