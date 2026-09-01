from app.concepts import BY_KEY
from app.extractor import extract_metric, extract_metric_with_dimensions
from app.periods import Period

FAKE_FACTS = {
    "facts": {
        "us-gaap": {
            "ServicingAssetAtFairValueAmount": {
                "units": {
                    "USD": [
                        {
                            "form": "10-Q", "fy": 2026, "fp": "Q2",
                            "filed": "2026-08-01", "val": 100, "accn": "amended",
                        },
                        {
                            "form": "10-Q", "fy": 2026, "fp": "Q2",
                            "filed": "2026-07-15", "val": 95, "accn": "original",
                        },
                    ]
                }
            }
        }
    }
}


def test_prefers_latest_filed_fact_over_earliest():
    concept = BY_KEY["msr_fair_value"]
    result = extract_metric_with_dimensions(FAKE_FACTS, concept, 2026, "10-Q", "Q2")
    assert result["value"] == 100
    assert result["accn"] == "amended"


def test_extract_metric_uses_period_object():
    concept = BY_KEY["msr_fair_value"]
    period = Period.build("10-Q", 2026, "Q2")
    result = extract_metric(FAKE_FACTS, concept, period)
    assert result["value"] == 100


def test_prefers_current_period_over_prior_year_comparative_on_filed_tie():
    # Same filing (same "filed" date) tags both the current period and a
    # prior-year comparative under the same fy/fp -- must not silently pick
    # the comparative just because it happens to be encountered first.
    facts = {
        "facts": {
            "us-gaap": {
                "ContractuallySpecifiedServicingFeesAmount": {
                    "units": {
                        "USD": [
                            {
                                "form": "10-Q", "fy": 2026, "fp": "Q2", "filed": "2026-08-07",
                                "start": "2025-01-01", "end": "2025-06-30", "val": 802_000_000,
                            },
                            {
                                "form": "10-Q", "fy": 2026, "fp": "Q2", "filed": "2026-08-07",
                                "start": "2026-01-01", "end": "2026-06-30", "val": 2_149_000_000,
                            },
                        ]
                    }
                }
            }
        }
    }
    concept = BY_KEY["servicing_fee_income"]
    result = extract_metric_with_dimensions(facts, concept, 2026, "10-Q", "Q2")
    assert result["value"] == 2_149_000_000
    assert result["end"] == "2026-06-30"


def test_missing_concept_returns_none():
    concept = BY_KEY["msr_fair_value"]
    result = extract_metric_with_dimensions(FAKE_FACTS, concept, 1999, "10-Q", "Q1")
    assert result is None
