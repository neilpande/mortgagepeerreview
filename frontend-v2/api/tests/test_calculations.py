import math

from app.calculations import (
    derive_delinquency_rate,
    derive_leverage,
    derive_price_mult,
    derive_servicing_fee_bps,
)


def test_derive_servicing_fee_bps_basic():
    # $2,501M annualized fee income on $1,640,000M ($1,640B) UPB
    result = derive_servicing_fee_bps(2501, 1_640_000)
    assert math.isclose(result, 2501 / 1_640_000 * 10_000, rel_tol=1e-9)


def test_derive_servicing_fee_bps_missing_input_is_none():
    assert derive_servicing_fee_bps(None, 1_000) is None
    assert derive_servicing_fee_bps(100, None) is None
    assert derive_servicing_fee_bps(100, 0) is None


def test_derive_price_mult_hand_computed():
    # UPB $1,640B, Fair Value $23.80B -> hand-computed price/mult
    upb = 1_640_000  # $M
    fair_value = 23_800  # $M
    fee_bps = derive_servicing_fee_bps(2501, upb)

    result = derive_price_mult(upb, fair_value, fee_bps)

    expected_price_bps = fair_value / upb * 10_000
    expected_mult = expected_price_bps / fee_bps
    assert math.isclose(result.price_bps, expected_price_bps, rel_tol=1e-9)
    assert math.isclose(result.mult, expected_mult, rel_tol=1e-9)

    # Mult should also equal fair_value / annualized fee income directly
    # (PRD Section 7's literal "Fair Value / Servicing Fee" formula).
    assert math.isclose(result.mult, fair_value / 2501, rel_tol=1e-9)


def test_derive_price_mult_missing_any_input_returns_none():
    assert derive_price_mult(None, 23_800, 15.3) is None
    assert derive_price_mult(1_640_000, None, 15.3) is None
    assert derive_price_mult(1_640_000, 23_800, None) is None
    assert derive_price_mult(0, 23_800, 15.3) is None


def test_derive_leverage_hand_computed():
    assert math.isclose(derive_leverage(27_200, 14_900), 27_200 / 14_900, rel_tol=1e-9)


def test_derive_leverage_missing_input_is_none():
    assert derive_leverage(None, 14_900) is None
    assert derive_leverage(27_200, None) is None
    assert derive_leverage(27_200, 0) is None


def test_derive_delinquency_rate_hand_computed():
    assert math.isclose(derive_delinquency_rate(31.16, 1640), 31.16 / 1640 * 100, rel_tol=1e-9)


def test_derive_delinquency_rate_missing_input_is_none():
    assert derive_delinquency_rate(None, 1640) is None
    assert derive_delinquency_rate(31.16, None) is None
    assert derive_delinquency_rate(31.16, 0) is None
