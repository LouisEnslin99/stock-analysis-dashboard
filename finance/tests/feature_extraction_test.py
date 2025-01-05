"""
feature_extraction.py

Script to fetch Yahoo Finance data for a given ticker using yfinance, then
compute 30+ relative/growth features from Income, Balance, and Cash Flow statements.

Run:
  python feature_extraction.py
Or import the `extract_all_features(ticker, years=5)` function into your pipeline.

Requires:
  pip install yfinance pandas numpy
"""

import yfinance as yf
import pandas as pd
import numpy as np

def extract_all_features(ticker: str, years: int = 5) -> dict:
    """
    Fetch multi-year data from Yahoo Finance for the given `ticker`.
    Then compute 30+ scale-invariant or growth-based features:
    
    1)  Revenue Growth (1-year)
    2)  Revenue Growth (5-year CAGR)
    3)  Gross Margin (latest)
    4)  Operating Margin (latest)
    5)  Net Margin (latest)
    6)  EBITDA Margin (latest)
    7)  EBITDA Growth (1-year)
    8)  EBITDA Growth (5-year CAGR)
    9)  R&D-to-Revenue Ratio (latest)
    10) Debt-to-Equity Ratio (latest)
    11) Debt-to-Assets Ratio (latest)
    12) Current Ratio (latest)
    13) Quick Ratio (latest)
    14) TangibleBookValue/share Growth (1-year)
    15) Equity Growth (5-year CAGR)
    16) Working Capital Ratio (latest)
    17) Operating CF to Revenue (latest)
    18) Free CF to Revenue (latest)
    19) Operating CF Growth (1-year)
    20) Free CF Growth (5-year CAGR)
    21) CapEx-to-Revenue Ratio (latest)
    22) FCF Margin (latest)
    23) Cash Conversion Ratio (latest)
    24) ROA (Return on Assets) (latest)
    25) ROE (Return on Equity) (latest)
    26) ROIC (Return on Invested Capital) (latest)
    27) Dividends-to-FCF Ratio (latest)
    28) R&D Growth (1-year)
    29) SG&A-to-Revenue Ratio (latest)
    30) ShareCount Change (5-year)
    ... you can add more or adapt as needed.

    Returns a dictionary of features. If data is missing or insufficient,
    the corresponding feature is None.
    """

    ########################
    # 1) Fetch data via yfinance
    ########################
    stock = yf.Ticker(ticker)
    balance_sheet = stock.get_balance_sheet()
    income_stmt = stock.get_financials()
    cash_flow = stock.get_cashflow()

    # Sort columns oldest -> newest for easier year-based calculations
    # (yfinance often returns newest->oldest, so we reverse it).
    def sort_columns_oldest_to_newest(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()
        sorted_cols = sorted(df.columns)
        return df[sorted_cols]
    
    balance_sheet = sort_columns_oldest_to_newest(balance_sheet)
    income_stmt = sort_columns_oldest_to_newest(income_stmt)
    cash_flow = sort_columns_oldest_to_newest(cash_flow)

    # Helper to safely retrieve row/column
    def safe_val(df: pd.DataFrame, row_label: str, col) -> float:
        """Return numeric value from df.loc[row_label, col] or None if missing."""
        if df is None or df.empty:
            return None
        try:
            val = df.loc[row_label, col]
            return float(val) if pd.notnull(val) else None
        except KeyError:
            return None
        except:
            return None

    # Identify the columns (which represent fiscal year ends, e.g. '2018-09-30')
    # We'll focus on the last `years` columns (if possible).
    # Example: If we want 5-year calculations, we need at least 6 columns for 5-year growth.
    def get_relevant_cols(df: pd.DataFrame, n: int) -> list:
        if df is None or df.empty:
            return []
        all_cols = list(df.columns)
        if len(all_cols) < n:
            return all_cols
        return all_cols[-n:]  # last n columns

    # We'll define a small function to compute 1-year growth, 5-year CAGR, etc.
    #  (val_t - val_t-1) / val_t-1 * 100% for 1-year
    def growth_1y(df, row_label, cols) -> float:
        if len(cols) < 2:
            return None
        latest = safe_val(df, row_label, cols[-1])
        prev = safe_val(df, row_label, cols[-2])
        if latest is None or prev is None or prev == 0:
            return None
        return ((latest - prev) / abs(prev)) * 100.0

    # 5-year CAGR:  (val_t / val_t-5)^(1/5) - 1
    def growth_5yr_cagr(df, row_label, cols) -> float:
        if len(cols) < 6:
            return None
        val_now = safe_val(df, row_label, cols[-1])
        val_5y = safe_val(df, row_label, cols[-6])
        if val_now is None or val_5y is None or val_5y == 0:
            return None
        # CAGR in percentage
        return ((val_now / abs(val_5y))**(1.0/5.0) - 1.0) * 100.0

    # We'll define a ratio helper: ratio = (val_rowA / val_rowB)*100 or no *100 if we want raw ratio
    def ratio(dfA, rowA, colA, dfB, rowB, colB, multiplier=1.0):
        A = safe_val(dfA, rowA, colA)
        B = safe_val(dfB, rowB, colB)
        if A is None or B is None or B == 0:
            return None
        return (A / abs(B)) * multiplier

    # We also need to gather the last `years` columns from each statement for consistent indexing
    # Because for 5-year features, we might need 6 columns. Let's pick max(6, years).
    needed_cols = max(6, years)
    bal_cols = get_relevant_cols(balance_sheet, needed_cols)
    inc_cols = get_relevant_cols(income_stmt, needed_cols)
    cf_cols = get_relevant_cols(cash_flow, needed_cols)

    # The 'latest' column we'll reference often
    latest_bal_col = bal_cols[-1] if len(bal_cols) > 0 else None
    latest_inc_col = inc_cols[-1] if len(inc_cols) > 0 else None
    latest_cf_col = cf_cols[-1] if len(cf_cols) > 0 else None

    ########################
    # 2) Compute each feature
    ########################
    feats = {}
    feats["ticker"] = ticker

    # For convenience
    rev_1y_growth = growth_1y(income_stmt, "TotalRevenue", inc_cols)
    rev_5y_cagr   = growth_5yr_cagr(income_stmt, "TotalRevenue", inc_cols)
    feats["RevenueGrowth_1y"]      = rev_1y_growth
    feats["RevenueGrowth_5yCAGR"]  = rev_5y_cagr

    # 3) Gross Margin (latest) = (GrossProfit / TotalRevenue)*100
    feats["GrossMargin_latest"] = None
    if latest_inc_col:
        test1 = ratio(income_stmt, "GrossProfit", latest_inc_col,
                                            income_stmt, "TotalRevenue", latest_inc_col,
                                            multiplier=100.0)

        feats["GrossMargin_latest"] = test1
    # 4) Operating Margin (latest) = (OperatingIncome / TotalRevenue)*100
    feats["OperatingMargin_latest"] = None
    if latest_inc_col:
        feats["OperatingMargin_latest"] = ratio(income_stmt, "OperatingIncome", latest_inc_col,
                                                income_stmt, "TotalRevenue", latest_inc_col,
                                                multiplier=100.0)

    # 5) Net Margin (latest) = (NetIncome / TotalRevenue)*100
    feats["NetMargin_latest"] = None
    if latest_inc_col:
        feats["NetMargin_latest"] = ratio(income_stmt, "NetIncome", latest_inc_col,
                                          income_stmt, "TotalRevenue", latest_inc_col,
                                          multiplier=100.0)

    # 6) EBITDA Margin (latest) = (EBITDA / TotalRevenue)*100
    feats["EBITDAMargin_latest"] = None
    if latest_inc_col:
        feats["EBITDAMargin_latest"] = ratio(income_stmt, "EBITDA", latest_inc_col,
                                             income_stmt, "TotalRevenue", latest_inc_col,
                                             multiplier=100.0)

    # 7) EBITDA Growth (1-year)
    feats["EBITDAGrowth_1y"] = growth_1y(income_stmt, "EBITDA", inc_cols)
    # 8) EBITDA Growth (5-year CAGR)
    feats["EBITDAGrowth_5yCAGR"] = growth_5yr_cagr(income_stmt, "EBITDA", inc_cols)

    # 9) R&D-to-Revenue Ratio (latest) = (R&D / Revenue)*100
    feats["RDtoRevenue_latest"] = None
    if latest_inc_col:
        feats["RDtoRevenue_latest"] = ratio(income_stmt, "ResearchAndDevelopment", latest_inc_col,
                                            income_stmt, "TotalRevenue", latest_inc_col,
                                            multiplier=100.0)

    # 10) Debt-to-Equity Ratio (latest) = TotalDebt / CommonStockEquity
    feats["DebtEquity_latest"] = None
    if latest_bal_col:
        feats["DebtEquity_latest"] = ratio(balance_sheet, "TotalDebt", latest_bal_col,
                                           balance_sheet, "CommonStockEquity", latest_bal_col)

    # 11) Debt-to-Assets Ratio (latest) = TotalDebt / TotalAssets
    feats["DebtAssets_latest"] = None
    if latest_bal_col:
        feats["DebtAssets_latest"] = ratio(balance_sheet, "TotalDebt", latest_bal_col,
                                           balance_sheet, "TotalAssets", latest_bal_col)

    # 12) Current Ratio (latest) = CurrentAssets / CurrentLiabilities
    feats["CurrentRatio_latest"] = None
    if latest_bal_col:
        feats["CurrentRatio_latest"] = ratio(balance_sheet, "CurrentAssets", latest_bal_col,
                                             balance_sheet, "CurrentLiabilities", latest_bal_col)

    # 13) Quick Ratio (latest) = (CurrentAssets - Inventory) / CurrentLiabilities
    feats["QuickRatio_latest"] = None
    if latest_bal_col:
        current_assets = safe_val(balance_sheet, "CurrentAssets", latest_bal_col)
        inventory = safe_val(balance_sheet, "Inventory", latest_bal_col)
        cur_liab = safe_val(balance_sheet, "CurrentLiabilities", latest_bal_col)
        if current_assets is not None and inventory is not None and cur_liab and cur_liab != 0:
            feats["QuickRatio_latest"] = (current_assets - inventory) / abs(cur_liab)

    # 14) Tangible Book Value per Share Growth (1-year)
    # We'll approximate "TangibleBookValue" from 'TangibleBookValue' row in balance sheet,
    # but the "per share" might require "OrdinarySharesNumber" or "ShareIssued" row. 
    feats["TangibleBookValueShareGrowth_1y"] = None
    if len(bal_cols) >= 2:
        tbv_latest = safe_val(balance_sheet, "TangibleBookValue", bal_cols[-1])
        tbv_prev   = safe_val(balance_sheet, "TangibleBookValue", bal_cols[-2])
        shares_latest = safe_val(balance_sheet, "OrdinarySharesNumber", bal_cols[-1]) \
                        or safe_val(balance_sheet, "ShareIssued", bal_cols[-1])
        shares_prev   = safe_val(balance_sheet, "OrdinarySharesNumber", bal_cols[-2]) \
                        or safe_val(balance_sheet, "ShareIssued", bal_cols[-2])
        if tbv_latest and tbv_prev and shares_latest and shares_prev and shares_prev != 0:
            tbvps_latest = tbv_latest / abs(shares_latest)
            tbvps_prev   = tbv_prev / abs(shares_prev)
            if tbvps_prev != 0:
                feats["TangibleBookValueShareGrowth_1y"] = ((tbvps_latest - tbvps_prev)
                                                            / abs(tbvps_prev) * 100.0)

    # 15) Equity Growth (5-year CAGR) = (Equity_t / Equity_t-5)^(1/5) - 1
    feats["EquityGrowth_5yCAGR"] = growth_5yr_cagr(balance_sheet, "CommonStockEquity", bal_cols)

    # 16) Working Capital Ratio (latest) = WorkingCapital / TotalAssets
    feats["WorkingCapitalRatio_latest"] = None
    if latest_bal_col:
        wc_val = safe_val(balance_sheet, "WorkingCapital", latest_bal_col)
        ta_val = safe_val(balance_sheet, "TotalAssets", latest_bal_col)
        if wc_val and ta_val and ta_val != 0:
            feats["WorkingCapitalRatio_latest"] = wc_val / abs(ta_val)

    # 17) Operating CF to Revenue (latest) = (OperatingCashFlow / Revenue)*100
    feats["OpCFtoRevenue_latest"] = None
    if latest_cf_col and latest_inc_col:
        feats["OpCFtoRevenue_latest"] = ratio(cash_flow, "OperatingCashFlow", latest_cf_col,
                                              income_stmt, "TotalRevenue", latest_inc_col,
                                              multiplier=100.0)

    # 18) Free CF to Revenue (latest) = (FreeCashFlow / Revenue)*100
    feats["FCFtoRevenue_latest"] = None
    if latest_cf_col and latest_inc_col:
        feats["FCFtoRevenue_latest"] = ratio(cash_flow, "FreeCashFlow", latest_cf_col,
                                             income_stmt, "TotalRevenue", latest_inc_col,
                                             multiplier=100.0)

    # 19) Operating CF Growth (1-year)
    feats["OperatingCFGrowth_1y"] = growth_1y(cash_flow, "OperatingCashFlow", cf_cols)

    # 20) Free CF Growth (5-year CAGR)
    def fcf_5y_cagr():
        return growth_5yr_cagr(cash_flow, "FreeCashFlow", cf_cols)
    feats["FreeCFGrowth_5yCAGR"] = fcf_5y_cagr()

    # 21) CapEx-to-Revenue (latest) = (CapitalExpenditure / Revenue)*100
    feats["CapExtoRevenue_latest"] = None
    if latest_cf_col and latest_inc_col:
        feats["CapExtoRevenue_latest"] = ratio(cash_flow, "CapitalExpenditure", latest_cf_col,
                                               income_stmt, "TotalRevenue", latest_inc_col,
                                               multiplier=100.0)

    # 22) FCF Margin (latest) = (FreeCashFlow / Revenue)*100 (similar to #18)
    feats["FCFMargin_latest"] = feats["FCFtoRevenue_latest"]  # same or keep separate

    # 23) Cash Conversion Ratio (latest) = OperatingCashFlow / NetIncome
    feats["CashConversionRatio_latest"] = None
    if latest_cf_col and latest_inc_col:
        ocf = safe_val(cash_flow, "OperatingCashFlow", latest_cf_col)
        net_inc = safe_val(income_stmt, "NetIncome", latest_inc_col)
        if ocf and net_inc and net_inc != 0:
            feats["CashConversionRatio_latest"] = ocf / abs(net_inc)

    # 24) ROA (latest) = NetIncome / TotalAssets * 100
    feats["ROA_latest"] = None
    if latest_bal_col and latest_inc_col:
        feats["ROA_latest"] = ratio(income_stmt, "NetIncome", latest_inc_col,
                                    balance_sheet, "TotalAssets", latest_bal_col,
                                    multiplier=100.0)

    # 25) ROE (latest) = NetIncome / Equity * 100
    feats["ROE_latest"] = None
    if latest_bal_col and latest_inc_col:
        feats["ROE_latest"] = ratio(income_stmt, "NetIncome", latest_inc_col,
                                    balance_sheet, "CommonStockEquity", latest_bal_col,
                                    multiplier=100.0)

    # 26) ROIC (latest) ~ NOPAT / InvestedCapital * 100
    # We'll approximate NOPAT = OperatingIncome * (1 - TaxRate?), or use NetIncome for simplification.
    # For invested capital, we can use "InvestedCapital" from balance sheet if available.
    feats["ROIC_latest"] = None
    if latest_bal_col and latest_inc_col:
        # We'll approximate NOPAT using OperatingIncome minus 21% tax or so...
        op_inc = safe_val(income_stmt, "OperatingIncome", latest_inc_col)
        invested_cap = safe_val(balance_sheet, "InvestedCapital", latest_bal_col)
        if op_inc and invested_cap and invested_cap != 0:
            # approximate a 21% tax => NOPAT
            nopat = op_inc * 0.79
            feats["ROIC_latest"] = (nopat / abs(invested_cap)) * 100.0

    # 27) Dividends-to-FCF Ratio (latest) = (CommonStockDividendPaid / FreeCashFlow)*100
    feats["DividendsToFCF_latest"] = None
    if latest_cf_col:
        div_paid = safe_val(cash_flow, "CommonStockDividendPaid", latest_cf_col) \
                   or safe_val(cash_flow, "CashDividendsPaid", latest_cf_col)
        fcf_val = safe_val(cash_flow, "FreeCashFlow", latest_cf_col)
        if div_paid and fcf_val and fcf_val != 0:
            # div_paid is often negative in statements
            feats["DividendsToFCF_latest"] = (abs(div_paid) / abs(fcf_val)) * 100.0

    # 28) R&D Growth (1-year)
    feats["RAndDGrowth_1y"] = growth_1y(income_stmt, "ResearchAndDevelopment", inc_cols)

    # 29) SG&A-to-Revenue Ratio (latest) = (SellingGeneralAndAdministration / Revenue)*100
    feats["SGAtoRevenue_latest"] = None
    if latest_inc_col:
        feats["SGAtoRevenue_latest"] = ratio(income_stmt, "SellingGeneralAndAdministration",
                                             latest_inc_col,
                                             income_stmt, "TotalRevenue", latest_inc_col,
                                             multiplier=100.0)

    # 30) Share Count Change (5-year) = (Shares_t - Shares_t-5)/Shares_t-5 * 100
    feats["ShareCountChange_5y"] = None
    def share_5y_change():
        if len(bal_cols) < 6:
            return None
        share_now = safe_val(balance_sheet, "OrdinarySharesNumber", bal_cols[-1]) \
                    or safe_val(balance_sheet, "ShareIssued", bal_cols[-1])
        share_5y_ago = safe_val(balance_sheet, "OrdinarySharesNumber", bal_cols[-6]) \
                       or safe_val(balance_sheet, "ShareIssued", bal_cols[-6])
        if share_now and share_5y_ago and share_5y_ago != 0:
            return ((share_now - share_5y_ago) / abs(share_5y_ago)) * 100.0
        return None
    feats["ShareCountChange_5y"] = share_5y_change()

    ########################
    # Return the dictionary
    ########################
    return feats


if __name__ == "__main__":
    # Example usage
    test_ticker = "AAPL"
    features = extract_all_features(test_ticker, years=5)
    print(f"Extracted Features for {test_ticker}:")
    for k, v in features.items():
        print(k, "=", v)
