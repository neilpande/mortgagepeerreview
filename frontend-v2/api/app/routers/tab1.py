from __future__ import annotations

from fastapi import APIRouter

from ..schemas import PeriodInfo, PeriodsResponse, Tab1Response
from ..tabs.tab1 import best_period_for_coverage, build_tab1_response
from .common import available_periods, resolve_period

router = APIRouter(prefix="/api")


@router.get("/periods", response_model=PeriodsResponse)
def get_periods():
    periods = available_periods()
    default = best_period_for_coverage(periods)
    return PeriodsResponse(
        periods=[
            PeriodInfo(id=p.id, form=p.form, fy=p.fy, fp=p.fp, label=p.label)
            for p in periods
        ],
        default_period_id=default.id,
    )


@router.get("/tabs/1", response_model=Tab1Response)
def get_tab1(period: str):
    return build_tab1_response(resolve_period(period))
