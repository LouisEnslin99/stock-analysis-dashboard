# finance/analysis_config.py

"""
Holds color-threshold config for each metric. 
We store for each metric a dictionary that defines 
the 'excellent'/'good'/'bad' thresholds, 
and optionally logic for inverting logic if needed.
"""

ANALYSIS_THRESHOLDS = {
    "Revenue": {
        # in EUR, e.g., 10_000_000_000 => 10 Mrd
        "excellent": 10_000_000_000,  # green if > 10bn
        "good": 500_000_000,         # yellow if between 500m and 10bn
        # below 500m => red
    },
    "RevenueGrowth": {
        # in percentage
        "excellent": 15.0,  # if > 15%, green
        "good": 5.0,        # 5-15% => yellow
        # below 5 => red
    },
    "GrossProfitMargin": {
        # in percentage
        "excellent": 25.0,
        "good": 15.0,
        # below 15 => red
    },
    "EBITMargin": {
        "excellent": 15.0,
        "good": 6.0,
        # below 6 => red
    },
    "InterestCoverage": {
        # e.g. EBIT / InterestExpense => # 
        # > 20 => excellent, 5-20 => good, below 5 => red
        "excellent": 20.0,
        "good": 5.0,
    },
    "NetIncomeMargin": {
        "excellent": 20.0,
        "good": 5.0,
    },
    "RDtoRevenueRatio": {
        # we interpret <7% as "excellent" => needs inverted logic
        # e.g., if < 7 => green, 7-20 => yellow, >20 => red
        "excellent": 7.0,
        "good": 20.0,
        # above 20 => red
        "inverted": True  # means smaller is better
    },
    "PersonnelExpenseRatio": {
        # <30 => green, 30-50 => yellow, > 50 => red
        "excellent": 30.0,
        "good": 50.0,
        "inverted": True  # smaller is better
    },
}
