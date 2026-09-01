"""Central Concept Definitions with Dimension Axis Mapping."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Concept:
    key: str
    label: str
    tags: tuple[str, ...]
    period_type: str
    dimension_member: str | None = None  # Expected dimension keyword (e.g., "Prepayment", "Discount")
    unit: str = "USD"
    notes: str = ""
    swing_flag_ratio: float = 0.75


CONCEPTS: tuple[Concept, ...] = (
    # =========================================================================
    # 1. PRIMARY FINANCIAL STATEMENTS
    # =========================================================================
    Concept(
        key="revenue",
        label="Total revenue",
        tags=(
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "RevenueFromContractWithCustomerIncludingAssessedTax",
            "Revenues",
            "SalesRevenueNet",
            "SalesRevenueGoodsNet",
        ),
        period_type="duration",
        notes=(
            "ASC 606 split the old SalesRevenueNet into the two "
            "ContractWithCustomer tags in 2018. Pre-2018 filings use the "
            "legacy tags; the chain covers both eras."
        ),
    ),
    Concept(
        key="cost_of_revenue",
        label="Cost of revenue",
        tags=("CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"),
        period_type="duration",
    ),
    Concept(
        key="gross_profit",
        label="Gross profit",
        tags=("GrossProfit",),
        period_type="duration",
        notes=(
            "Many filers never tag GrossProfit; derive it as "
            "revenue - cost_of_revenue and mark the row derived."
        ),
    ),
    Concept(
        key="operating_income",
        label="Operating income",
        tags=("OperatingIncomeLoss",),
        period_type="duration",
    ),
    Concept(
        key="net_income",
        label="Net income",
        tags=(
            "NetIncomeLoss",
            "ProfitLoss",
            "NetIncomeLossAvailableToCommonStockholdersBasic",
        ),
        period_type="duration",
        notes=(
            "NetIncomeLoss is attributable to the parent; ProfitLoss "
            "includes noncontrolling interests. They differ for companies "
            "with minority stakes -- do not treat them as interchangeable "
            "without noting which you got."
        ),
    ),
    Concept(
        key="eps_diluted",
        label="Diluted EPS",
        tags=("EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"),
        period_type="duration",
        unit="USD/shares",
        notes="Unit string in companyfacts is literally 'USD/shares'.",
    ),
    Concept(
        key="assets",
        label="Total assets",
        tags=("Assets",),
        period_type="instant",
    ),
    Concept(
        key="liabilities",
        label="Total liabilities",
        tags=("Liabilities",),
        period_type="instant",
        notes=(
            "Some filers only tag LiabilitiesAndStockholdersEquity; if "
            "Liabilities is missing, derive it as that minus equity."
        ),
    ),
    Concept(
        key="equity",
        label="Stockholders equity",
        tags=(
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        ),
        period_type="instant",
    ),
    Concept(
        key="cash",
        label="Cash and equivalents",
        tags=(
            "CashAndCashEquivalentsAtCarryingValue",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        ),
        period_type="instant",
    ),
    Concept(
        key="cfo",
        label="Cash from operations",
        tags=(
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
        ),
        period_type="duration",
    ),

    # =========================================================================
    # 2. MORTGAGE BANKING & MSR METRICS (ALL 7 PEERS)
    # =========================================================================
    Concept(
        key="msr_fair_value",
        label="MSR Fair Value",
        tags=(
            "ServicingAssetAtFairValueAmount",
            "nrz:MortgageServicingRightsFairValue",
            "MortgageServicingRightsFairValue",
            "ServicingAsset",
        ),
        period_type="instant",
    ),
    Concept(
        key="msr_upb",
        label="MSR Unpaid Principal Balance (UPB)",
        tags=(
            "pfsi:ServicingAssetUnpaidPrincipalBalanceOfUnderlyingLoans",
            "pmt:FairValueUnpaidPrincipalOfUnderlyingLoansBalance",
            "onit:AssetsServiced",
            "SecuritizedAssetsAndAnyOtherFinancialAssetsManagedTogetherPrincipalAmountOutstanding",
            "nrz:UnpaidPrincipalBalanceOfUnderlyingLoans",
            "PrincipalAmountOutstandingOnLoansManagedAndSecuritized",
            "ServicingAssetUnpaidPrincipalBalanceOfUnderlyingLoans",
        ),
        period_type="instant",
    ),
    Concept(
        key="msr_cpr",
        label="Prepayment Speed (CPR)",
        tags=(
            "FairValueInputsPrepaymentRate",
            "ServicingAssetsAndServicingLiabilitiesAtFairValueAssumptionsUsedToEstimateFairValuePrepaymentSpeed",
            "pmt:FairValueInputsPricingSpread",
        ),
        period_type="instant",
        unit="pure",
        notes=(
            "The SEC companyfacts API never exposes dimensional (axis/member) "
            "facts, only each filer's plain top-level tags -- so unlike the "
            "reference design's single shared 'ServicingAssetMeasurementInput' "
            "tag split by MeasurementInputTypeAxis, this chain uses the "
            "distinct plain tags filers actually use for CPR specifically. "
            "Filers with no plain CPR tag in companyfacts (only disclosed in "
            "an untagged MD&A table) resolve to not-available for now -- "
            "recovering those would need full XBRL instance / R-file parsing, "
            "not this API."
        ),
    ),
    Concept(
        key="msr_discount_rate",
        label="Discount Rate / Yield",
        tags=(
            "FairValueInputsDiscountRate",
            "ServicingAssetsAndServicingLiabilitiesAtFairValueAssumptionsUsedToEstimateFairValueDiscountRate",
            "pmt:FairValueInputsOptionAdjustedSpread",
        ),
        period_type="instant",
        unit="pure",
        notes="See msr_cpr's note on why this chain uses plain per-filer tags rather than an axis member.",
    ),
    Concept(
        key="msr_cost_to_service",
        label="Cost to Service",
        tags=(
            "pfsi:AssumptionForFairValueOfInterestsContinuedToBeHeldByTransferorServicingAssetsOrLiabilitiesPerLoanCostOfServicing",
            "pmt:FairValueInputAnnualPerLoanCostOfServicing",
        ),
        period_type="instant",
        unit="USD",
        notes="See msr_cpr's note; cost-to-service has the narrowest plain-tag coverage of the three Level 3 inputs across the peer set.",
    ),
    Concept(
        key="servicing_fee_income",
        label="Servicing fee income",
        tags=(
            "ContractuallySpecifiedServicingFeesAmount",
            "FeesAndCommissionsMortgageBankingAndServicing",
            "CashFlowsBetweenTransfereeAndTransferorServicingFees",
        ),
        period_type="duration",
        notes=(
            "Input to the derived servicing_fee_bps used by the MSR & Level 3 "
            "tab's Price/Mult calculation (see calculations.py). The "
            "weighted-average fee rate itself is typically a company "
            "extension tag, not a standard one, so it is not chained here -- "
            "servicing_fee_bps is derived from this dollar figure and UPB "
            "instead. The third tag is a cash-flow-statement fallback "
            "(servicing fees actually collected, vs. the income-statement "
            "accrual) -- some filers (e.g. PFSI from FY2022 on) stopped "
            "tagging the income-statement figure and only tag this one."
        ),
    ),
    Concept(
        key="msr_sensitivity_prepay_10",
        label="MSR value impact: prepayment +10%",
        tags=(
            "SensitivityAnalysisOfFairValueOfInterestsContinuedToBeHeldByTransferorServicingAssetsOrLiabilitiesImpactOf10PercentAdverseChangeInPrepaymentSpeed",
        ),
        period_type="instant",
        unit="USD",
        notes="Plain per-scenario tag (not axis-dimensional) -- see msr_cpr's note on companyfacts not exposing dimensional facts.",
    ),
    Concept(
        key="msr_sensitivity_prepay_20",
        label="MSR value impact: prepayment +20%",
        tags=(
            "SensitivityAnalysisOfFairValueOfInterestsContinuedToBeHeldByTransferorServicingAssetsOrLiabilitiesImpactOf20PercentAdverseChangeInPrepaymentSpeed",
        ),
        period_type="instant",
        unit="USD",
    ),
    Concept(
        key="msr_sensitivity_discount_10",
        label="MSR value impact: discount rate +10%",
        tags=(
            "SensitivityAnalysisOfFairValueOfInterestsContinuedToBeHeldByTransferorServicingAssetsOrLiabilitiesImpactOf10PercentAdverseChangeInDiscountRate",
        ),
        period_type="instant",
        unit="USD",
    ),
    Concept(
        key="msr_sensitivity_discount_20",
        label="MSR value impact: discount rate +20%",
        tags=(
            "SensitivityAnalysisOfFairValueOfInterestsContinuedToBeHeldByTransferorServicingAssetsOrLiabilitiesImpactOf20PercentAdverseChangeInDiscountRate",
        ),
        period_type="instant",
        unit="USD",
    ),
    Concept(
        key="msr_number_of_loans",
        label="Number of Loans Serviced",
        tags=(
            "two:ContinuingInvolvementWithContinuedToBeRecognizedTransferredFinancialAssetsNumberOfLoans",
            "NumberOfLoansServiced",
        ),
        period_type="instant",
        unit="shares",
    ),

    # =========================================================================
    # 3. TAB 2 -- MSR ROLL-FORWARD (FLOWS & ECONOMICS)
    # =========================================================================
    Concept(
        key="msr_rf_originations",
        label="MSR roll-forward: originations retained",
        tags=("ServicingAssetAtFairValueAdditionsResultingFromTransfersOfFinancialAssets",),
        period_type="duration",
    ),
    Concept(
        key="msr_rf_purchases",
        label="MSR roll-forward: bulk and flow purchases",
        tags=("ServicingAssetAtFairValueAdditionsFromPurchasesOfServicingAssets",),
        period_type="duration",
    ),
    Concept(
        key="msr_rf_disposals",
        label="MSR roll-forward: disposals",
        tags=("ServicingAssetAtFairValueDisposals",),
        period_type="duration",
        notes="Reported positive by filers; flip the sign when presenting as a reduction.",
    ),
    Concept(
        key="msr_rf_valuation_change",
        label="MSR roll-forward: change from valuation inputs/assumptions",
        tags=("ServicingAssetAtFairValueChangesInFairValueResultingFromChangesInValuationInputsOrAssumptions",),
        period_type="duration",
    ),
    Concept(
        key="msr_rf_cashflow_realization",
        label="MSR roll-forward: other changes (cash-flow realization / runoff)",
        tags=("ServicingAssetAtFairValueOtherChangesInFairValue",),
        period_type="duration",
    ),
    Concept(
        key="msr_purchases_cash",
        label="MSR purchases, cash flow statement",
        tags=("PaymentsToAcquireMortgageServicingRightsMSR",),
        period_type="duration",
    ),
    Concept(
        key="msr_sale_proceeds_cash",
        label="MSR sale proceeds, cash flow statement",
        tags=("ProceedsFromSaleOfMortgageServicingRightsMSR",),
        period_type="duration",
    ),
    Concept(
        key="lhfs_origination_cash",
        label="Loans-held-for-sale origination & purchase cash outflow",
        tags=("PaymentsForOriginationAndPurchasesOfLoansHeldForSale",),
        period_type="duration",
    ),
    Concept(
        key="gain_on_sale",
        label="Gain on sale of loans",
        tags=("GainLossOnSalesOfLoansNet", "GainLossOnSaleOfMortgageLoans"),
        period_type="duration",
    ),
    Concept(
        key="late_fee_income",
        label="Late fee income",
        tags=("LateFeeIncomeGeneratedByServicingFinancialAssetsAmount",),
        period_type="duration",
    ),
    Concept(
        key="ancillary_fee_income",
        label="Ancillary fee income",
        tags=("AncillaryFeeIncomeGeneratedByServicingFinancialAssetsAmount",),
        period_type="duration",
    ),

    # =========================================================================
    # 4. TAB 3 -- CREDIT & BALANCE SHEET
    # =========================================================================
    Concept(
        key="delinquent_upb",
        label="Delinquent UPB on the managed portfolio",
        tags=("DelinquentAmountAtEndOfPeriodOnLoansManagedAndSecuritized",),
        period_type="instant",
    ),
    Concept(
        key="repo_liability",
        label="Repo / warehouse funding liability",
        tags=("AssetsSoldUnderAgreementsToRepurchaseRepurchaseLiability",),
        period_type="instant",
    ),
    Concept(
        key="servicing_liability",
        label="Servicing liability",
        tags=("ServicingLiabilityAtAmortizedValueBalance", "ServicingLiabilityAtFairValueAmount"),
        period_type="instant",
    ),
)

BY_KEY: dict[str, Concept] = {c.key: c for c in CONCEPTS}

# Reverse lookup mapping: maps standard and custom tags to concept keys
TAG_TO_CONCEPT: dict[str, list[str]] = {}
for _c in CONCEPTS:
    for _t in _c.tags:
        clean_tag = _t.split(":")[-1] if ":" in _t else _t
        TAG_TO_CONCEPT.setdefault(clean_tag, []).append(_c.key)
        TAG_TO_CONCEPT.setdefault(_t, []).append(_c.key)