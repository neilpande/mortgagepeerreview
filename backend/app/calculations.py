"""Price/Mult derivation for the MSR & Level 3 tab (PRD Section 7).

Pure functions, deliberately free of any SEC/extraction/HTTP concerns so
they can be unit-tested by hand-computing expected values directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


def annualize_duration(
    value: float | None, start: str | None, end: str | None
) -> float | None:
    """Scale a duration fact (e.g. a quarterly or YTD fee figure) to a
    365-day run rate, using the fact's own start/end dates rather than
    assuming a fixed quarterly/YTD cadence (filers differ)."""
    if value is None or not start or not end:
        return None
    days = (date.fromisoformat(end) - date.fromisoformat(start)).days
    if days <= 0:
        return None
    return value * 365.0 / days


def derive_servicing_fee_bps(
    servicing_fee_income: float | None, upb: float | None
) -> float | None:
    """Annualized servicing fee rate, in basis points of UPB.

    servicing_fee_income is a period (duration) figure; callers are
    responsible for passing an already-annualized amount (e.g. doubling a
    6-month YTD figure) consistent with how UPB -- an instant, point-in-time
    figure -- is being compared against it.
    """
    if servicing_fee_income is None or upb is None or upb == 0:
        return None
    return servicing_fee_income / upb * 10_000


@dataclass(frozen=True)
class PriceMult:
    price_bps: float
    mult: float


def derive_price_mult(
    upb: float | None,
    fair_value: float | None,
    servicing_fee_bps: float | None,
) -> PriceMult | None:
    """Price (bps) and Mult, or None if any of the three inputs is missing.

    price_bps = fair_value / upb * 10,000
    mult      = price_bps / servicing_fee_bps
              = fair_value / annualized_servicing_fee_income  (algebraically
                identical -- both sides divide out the /upb*10,000 term)

    Never partially computed: PRD Section 7 requires a clear not-available
    indicator, not an incomplete or misleading figure, when any input is
    unavailable.
    """
    if upb is None or fair_value is None or servicing_fee_bps is None:
        return None
    if upb == 0 or servicing_fee_bps == 0:
        return None

    price_bps = fair_value / upb * 10_000
    mult = price_bps / servicing_fee_bps
    return PriceMult(price_bps=price_bps, mult=mult)


def derive_leverage(liabilities: float | None, equity: float | None) -> float | None:
    """Liabilities / equity, for the Tab 3 balance-sheet table."""
    if liabilities is None or equity is None or equity == 0:
        return None
    return liabilities / equity


def derive_delinquency_rate(delinquent_upb: float | None, upb: float | None) -> float | None:
    """Delinquent UPB as a percentage of total UPB, for the Tab 3 delinquency chart."""
    if delinquent_upb is None or upb is None or upb == 0:
        return None
    return delinquent_upb / upb * 100
