import json

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
