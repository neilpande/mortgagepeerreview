"""Extractor Engine (extractor.py)
Handles API fetching, XBRL dimension extraction, and HTML scraping.
"""

import json
import re
import urllib.request
from bs4 import BeautifulSoup

SEC_HEADERS = {'User-Agent': 'Cloverstone Edgar Dashboard/1.0 (neil@cloverstone.ai)'}
SEC_REQUEST_TIMEOUT_SECONDS = 20


def fetch_sec_facts(cik: str) -> dict:
    """Fetch raw XBRL company facts JSON from the SEC API.

    A network path that's slow or silently drops packets (rather than
    actively refusing) leaves urlopen with no default timeout blocked
    indefinitely, holding a thread forever with no error to log -- so an
    explicit timeout here is required, not just good practice.
    """
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
    req = urllib.request.Request(url, headers=SEC_HEADERS)
    with urllib.request.urlopen(req, timeout=SEC_REQUEST_TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode())


def extract_metric_with_dimensions(facts: dict, concept, year: int, form: str, period: str):
    """Layer 1 & 2: Extract tagged XBRL facts and filter by dimension axes.

    Among all facts matching (form, fy, fp[, dimension axis]), the winner is
    chosen by (filed, end) descending: the latest "filed" date wins first,
    so a later amendment/restatement for the same period takes precedence
    over an earlier as-originally-filed fact; ties on "filed" (facts from
    the same filing, e.g. a current-period duration fact and a prior-year
    comparative sharing the filing's fy/fp) are broken by the latest "end"
    date, so the current period wins over the comparative.
    """
    facts_data = facts.get("facts", {})
    target_tags = concept.tags
    dim_keyword = concept.dimension_member

    best = None
    for taxonomy, taxonomy_facts in facts_data.items():
        for tag in target_tags:
            clean_tag = tag.split(":")[-1]
            if clean_tag not in taxonomy_facts:
                continue

            entries = taxonomy_facts[clean_tag].get("units", {})
            for unit_key, fact_list in entries.items():
                for fact in fact_list:
                    # Match form, fiscal year, and period
                    if fact.get("form") == form and fact.get("fy") == year and fact.get("fp") == period:
                        # Check dimension axis if concept specifies one (e.g. CPR vs Discount Rate)
                        if dim_keyword:
                            dims = str(fact.get("dimensions", {})).lower()
                            if dim_keyword.lower() not in dims:
                                continue  # Axis doesn't match; skip to next entry

                        candidate = {
                            "value": fact.get("val"),
                            "tag": f"{taxonomy}:{clean_tag}",
                            "form": fact.get("form"),
                            "filed": fact.get("filed"),
                            "accn": fact.get("accn"),
                            "start": fact.get("start"),
                            "end": fact.get("end"),
                            "unit": unit_key
                        }
                        candidate_key = (candidate["filed"] or "", candidate["end"] or "")
                        best_key = (best["filed"] or "", best["end"] or "") if best else None
                        if best is None or candidate_key > best_key:
                            best = candidate
    return best


def extract_metric(facts: dict, concept, period):
    """Resolve a concept for an already-normalized Period (see periods.py)."""
    return extract_metric_with_dimensions(facts, concept, period.fy, period.form, period.fp)


def scrape_mda_html_fallback(cik: str, accession_num: str, primary_doc: str, target_keyword: str):
    """Layer 3: Scrape untagged HTML tables from MD&A filings if XBRL tags yield nothing."""
    accn_clean = accession_num.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn_clean}/{primary_doc}"
    
    try:
        req = urllib.request.Request(url, headers=SEC_HEADERS)
        with urllib.request.urlopen(req) as resp:
            soup = BeautifulSoup(resp.read().decode('utf-8', errors='ignore'), 'html.parser')
            
        for table in soup.find_all('table'):
            text = table.text
            if target_keyword.lower() in text.lower():
                matches = re.findall(r'(\d+\.\d+)\s*%', text)
                if matches:
                    return {"value": float(matches[0]), "source": "HTML Scraped MD&A Table"}
    except Exception as e:
        print(f"HTML Scrape Error: {e}")
    return None