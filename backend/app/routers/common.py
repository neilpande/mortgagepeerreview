from __future__ import annotations

from fastapi import HTTPException

from .. import cache
from ..companies import COMPANIES
from ..concepts import BY_KEY
from ..periods import Period, discover_available_periods


def available_periods() -> list[Period]:
    all_facts = cache.get_all_company_facts([c.cik for c in COMPANIES])
    return discover_available_periods(all_facts, BY_KEY)


def resolve_period(period_id: str) -> Period:
    match = next((p for p in available_periods() if p.id == period_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail=f"Unknown or unavailable period '{period_id}'")
    return match
