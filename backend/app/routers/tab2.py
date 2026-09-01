from __future__ import annotations

from fastapi import APIRouter

from ..schemas import Tab2Response
from ..tabs.tab2 import build_tab2_response
from .common import available_periods, resolve_period

router = APIRouter(prefix="/api")


@router.get("/tabs/2", response_model=Tab2Response)
def get_tab2(period: str):
    resolved = resolve_period(period)
    return build_tab2_response(resolved, available_periods())
