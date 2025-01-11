# finance/analysis_config.py

"""
Holds color-threshold config for each metric. 
We store for each metric a dictionary that defines 
the 'excellent'/'good'/'bad' thresholds, 
and optionally logic for inverting logic if needed.
"""

ANALYSIS_THRESHOLDS = {
    # -------------------- Existing Income metrics --------------------
    "Revenue": {
        "excellent": 10_000_000_000,  # >10 bn => green
        "good": 500_000_000,         # 500m - 10bn => yellow
        # below => red
    },
    "RevenueGrowth": {
        "excellent": 15.0,  # >15% => green
        "good": 5.0,        # 5-15% => yellow
        # below 5 => red
    },
    "GrossProfit": None,
    "GrossProfitGrowth": None,
    "GrossProfitMargin": {
        "excellent": 25.0,
        "good": 15.0,
    },
    "GrossProfitMarginGrowth": None,
    "EBIT": None,
    "EBITGrowth": None,
    "EBITMargin": {
        "excellent": 15.0,  # >15% => green
        "good": 6.0,        # 6-15% => yellow
        # below 6 => red
    },
    "EBITMarginGrowth": None,
    "InterestCoverage": {
        "excellent": 20.0,  # >20 => green
        "good": 5.0,        # 5-20 => yellow
        # below 5 => red
    },
    "InterestCoverageGrowth": None,
    "NetIncome": None,
    "NetIncomeGrowth": None,
    "NetIncomeMargin": {
        "excellent": 20.0,  # >20% => green
        "good": 5.0,        # 5-20% => yellow
        # below 5 => red
    },
    "NetIncomeMarginGrowth": None,
    "RDtoRevenueRatio": {
        # smaller is better: <7 => green, 7-20 => yellow, >20 => red
        "excellent": 7.0,
        "good": 20.0,
        "inverted": True
    },
    "RDtoRevenueRatioGrowth": None,
    "PersonnelExpense": {
        # <30 => green, 30-50 => yellow, >50 => red
        "excellent": 30.0,
        "good": 50.0,
        "inverted": True
    },
    "PersonnelExpenseGrowth": None,

    # -------------------- Balance Sheet metrics --------------------
    # 1) Total current assets => no numeric thresholds => None
    "CurrentAssets": None,
    "CurrentAssetsGrowth": None,

    # 2) Total assets => no numeric thresholds => None
    "TotalAssets": None,
    "TotalAssetsGrowth": None,

    # 3) Current Liabilities => no numeric thresholds => None
    "CurrentLiabilities": None,
    "CurrentLiabilitiesGrowth": None,

    # 4) Total Liabilities => no numeric thresholds => None
    "TotalLiabilities": None,
    "TotalLiabilitiesGrowth": None,

    # 5) Working Capital => no numeric thresholds => None
    "WorkingCapital": None,
    "WorkingCapitalGrowth": None,

    # 6) Current Ratio (#)
    #  >3 => green, 1-3 => yellow, <1 => red
    #  => Not inverted, bigger ratio = better
    "CurrentRatio": {
        "excellent": 3.0,
        "good": 1.0,
        # below 1 => red
    },
    "CurrentRatioGrowth": None,

    # 7) Equity => no numeric thresholds => None
    "Equity": None,
    "EquityGrowth": None,  # for 1y & 3y

    "ReturnOnEquity": {
        "excellent": 15.0,
        "good": 8.0,
        # <8.0 -> red
    }, 
    "ReturnOnEquityGrowth": None,
    #   b) Equity ratio => "EquityRatio"
    #      >70 => green, 30-70 => yellow, <30 => red
    "EquityRatio": {
        "excellent": 70.0,
        "good": 30.0,
        # <30 => red
    },
    "EquityRatioGrowth": None,


    # 8) Dept Ratio (Gearing) => <20% => green, 20-40% => yellow, >40% => red
    # smaller is better => "inverted": True
    "DebtRatio": {
        "excellent": 20.0,
        "good": 40.0,
        "inverted": True
    },
    "DebtRatioGrowth": None,

    # 9) Dividends => no numeric thresholds => None
    "Dividends": None,
    "DividendsGrowth": None,

    # 10) DividendsToShare => >5 => green, 2-5 => yellow, <2 => red
    # bigger is better => not inverted
    "DividendsToShare": {
        "excellent": 5.0,
        "good": 2.0,
        # below 2 => red
    },
    "DividendsToShareGrowth": None,

    # -------------------- Cash Flow Sheet metrics --------------------
    # 1) Operating Cash flow
    "OperatingCashFlow": None, 
    "OperatingCashFlowGrowth": None,

    # 2) Operating Cash Flow Margin
    "OperatingCashFlowMargin": {
        "excellent": 15.0,
        "good": 5.0
    },
    "OperatingCashFlowMarginGrowth": None

}
