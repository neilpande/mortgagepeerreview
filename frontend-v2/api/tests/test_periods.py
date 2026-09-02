from app.periods import Period, company_has_filed, discover_periods_for_company
from app.concepts import BY_KEY

FAKE_FACTS = {
    "facts": {
        "us-gaap": {
            "ServicingAssetAtFairValueAmount": {
                "units": {
                    "USD": [
                        {"form": "10-Q", "fy": 2026, "fp": "Q2", "filed": "2026-08-01", "val": 100},
                        {"form": "10-Q", "fy": 2026, "fp": "Q1", "filed": "2026-05-01", "val": 90},
                        {"form": "10-K", "fy": 2025, "fp": "FY", "filed": "2026-02-01", "val": 80},
                    ]
                }
            }
        }
    }
}


def test_discover_periods_for_company_finds_expected_periods():
    concepts = [BY_KEY["msr_fair_value"]]
    periods = discover_periods_for_company(FAKE_FACTS, concepts)
    assert periods == {
        Period.build("10-Q", 2026, "Q2"),
        Period.build("10-Q", 2026, "Q1"),
        Period.build("10-K", 2025, "FY"),
    }


def test_period_build_label_and_id():
    p = Period.build("10-Q", 2026, "Q2")
    assert p.id == "2026Q2"
    assert p.label == "Q2 2026 (10-Q)"

    fy = Period.build("10-K", 2025, "FY")
    assert fy.id == "2025FY"
    assert fy.label == "FY 2025 (10-K)"


def test_company_has_filed_true_for_a_period_present_in_any_tag():
    assert company_has_filed(FAKE_FACTS, Period.build("10-Q", 2026, "Q2")) is True


def test_company_has_filed_false_for_a_period_the_company_never_filed():
    assert company_has_filed(FAKE_FACTS, Period.build("10-Q", 2026, "Q3")) is False
