"""Period discovery and normalization (PRD Sections 5 and 14).

Scans cached companyfacts payloads for the (form, fiscal year, fiscal
period) combinations that are actually available, so the frontend's
reporting-period selector is built from real filings rather than a
hardcoded list.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .concepts import Concept

# Concepts whose availability we scan to discover periods. These are the
# primary-table inputs -- if a company has filed any of these for a given
# (form, fy, fp), that period is selectable.
PERIOD_PROBE_KEYS = ("msr_upb", "msr_fair_value", "servicing_fee_income")

_FP_RANK = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4, "FY": 5}


@dataclass(frozen=True)
class Period:
    id: str
    form: str
    fy: int
    fp: str
    label: str

    @staticmethod
    def build(form: str, fy: int, fp: str) -> "Period":
        pid = f"{fy}{fp}"
        label = f"{fp} {fy} ({form})" if fp != "FY" else f"FY {fy} ({form})"
        return Period(id=pid, form=form, fy=fy, fp=fp, label=label)


def period_sort_key(p: Period) -> tuple[int, int]:
    """Chronological sort key (fiscal year, then fiscal period within it)."""
    return (p.fy, _FP_RANK.get(p.fp, 0))


def discover_periods_for_company(
    facts: dict, concepts: Sequence[Concept] = ()
) -> set[Period]:
    """Find every (form, fy, fp) combination present for the given concepts."""
    facts_data = facts.get("facts", {})
    tags_to_scan: set[str] = set()
    for concept in concepts:
        for tag in concept.tags:
            tags_to_scan.add(tag.split(":")[-1])

    found: set[Period] = set()
    for taxonomy_facts in facts_data.values():
        for clean_tag, tag_data in taxonomy_facts.items():
            if tags_to_scan and clean_tag not in tags_to_scan:
                continue
            for fact_list in tag_data.get("units", {}).values():
                for fact in fact_list:
                    form = fact.get("form")
                    fy = fact.get("fy")
                    fp = fact.get("fp")
                    if form not in ("10-Q", "10-K") or fy is None or fp is None:
                        continue
                    found.add(Period.build(form, fy, fp))
    return found


def company_has_filed(facts: dict, period: Period) -> bool:
    """Whether this company has any 10-Q/10-K fact at all for this exact
    (form, fy, fp) -- i.e. whether they have actually filed for this period,
    as opposed to simply not tagging the specific fields a tab needs.

    Distinguishes "not yet filed" from "filed but didn't tag this metric" --
    a period can be selectable (some other peer filed for it) while a given
    company hasn't filed yet, and those are different facts worth saying
    differently to the user.
    """
    return period in discover_periods_for_company(facts, ())


def discover_available_periods(
    all_facts: Iterable[dict], concepts_by_key: dict[str, Concept]
) -> list[Period]:
    """Union of selectable periods across every peer company, newest first."""
    probe_concepts = [
        concepts_by_key[k] for k in PERIOD_PROBE_KEYS if k in concepts_by_key
    ]
    union: dict[str, Period] = {}
    for facts in all_facts:
        for period in discover_periods_for_company(facts, probe_concepts):
            union[period.id] = period
    return sorted(union.values(), key=period_sort_key, reverse=True)
