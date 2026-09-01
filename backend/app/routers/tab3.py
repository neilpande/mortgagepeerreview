from __future__ import annotations

from fastapi import APIRouter

from ..schemas import Tab3Response
from ..tabs.tab3 import build_tab3_response
from .common import resolve_period

router = APIRouter(prefix="/api")


@router.get("/tabs/3", response_model=Tab3Response)
def get_tab3(period: str):
    return build_tab3_response(resolve_period(period))
