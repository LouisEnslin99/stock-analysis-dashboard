# finance/analysis/analysis_tables/analysis_table.py

import streamlit as st
import pandas as pd

from finance.config.analysis_config import ANALYSIS_THRESHOLDS
from finance.analysis.analysis_formulas import (
    compute_growth_1y, compute_cagr_3y, compute_margin, compute_interest_coverage,
    classify_metric
)
from finance.analysis.analysis_utils import safe_val, format_cell, color_cell


def build_balance_analysis_table(balance_df, income_df):
    """
    Build and display an analysis table for the Balance Sheet
    with 1-year and 3-year growth calculations.

    The assumption:
      balance_df.columns[0] => latest
      balance_df.columns[1] => 1-year ago
      balance_df.columns[3] => 3-year ago
    If they don't exist, some growth values will be None.

    Metrics displayed:
      - Current Assets (€)
      - Total Assets (€)
      - Current Liabilities (€)
      - Total Liabilities Net Minority Interest (€)
      - Working Capital (€)
      - Current Ratio (#)
      - Common Stock Equity (labeled as "Equity (€)")
      - Equity Ratio (%) = Common Stock Equity / Total Assets
      - Dept Ratio (Gearing) (%) = Total Liabilities / Equity
      - Dividendes (€)
      - Dividendes to share (%)

    Make sure these row labels match your actual DataFrame index.
    """

    # 1) Ensure enough columns exist for 1-year & 3-year
    bal_cols = list(balance_df.columns)
    inc_cols = list(income_df.columns)
    if len(bal_cols) < 2:
        st.warning("Not enough data columns for Balance Sheet (need at least 2).")
        return

    # col[0] => latest, col[1] => 1-year, col[3] => 3-year
    latest_col = bal_cols[0]
    col_1y     = bal_cols[1] if len(bal_cols) >= 2 else None
    col_3y     = bal_cols[3] if len(bal_cols) >= 4 else None

    def get_growth_metrics(row_label):
        """
        Safely retrieve:
          - val_now   => bal_cols[0]
          - val_1yago => bal_cols[1]
          - val_3yago => bal_cols[3]
        Then compute 1-year growth & 3-year CAGR.
        Returns (latest_value, one_year_growth, three_year_cagr).
        """
        val_now = safe_val(balance_df, row_label, latest_col)
        val_1y  = safe_val(balance_df, row_label, col_1y)
        val_3y  = safe_val(balance_df, row_label, col_3y)

        g1 = compute_growth_1y(val_now, val_1y)
        g3 = compute_cagr_3y(val_now, val_3y)
        return val_now, g1, g3

    def calc_growth_metrics(val_now, val_1, val_3):
        """
        Compute 1-year growth & 3-year CAGR from numeric values 
        (used for ratios).
        """
        g1 = compute_growth_1y(val_now, val_1)
        g3 = compute_cagr_3y(val_now, val_3)
        return val_now, g1, g3

    rows = []

    # ------------------ 1) Current Assets (€) ------------------
    ca_now, ca_1y, ca_3y = get_growth_metrics("Current Assets")
    ca_class    = classify_metric(ca_now, ANALYSIS_THRESHOLDS["CurrentAssets"])
    ca_class_1y = classify_metric(ca_1y, ANALYSIS_THRESHOLDS["CurrentAssetsGrowth"])
    ca_class_3y = classify_metric(ca_3y, ANALYSIS_THRESHOLDS["CurrentAssetsGrowth"])

    rows.append({
        "Metric": "Current Assets (€)",
        "Latest Value": ca_now,
        "1Y Growth (%)": ca_1y,
        "3Y CAGR (%)": ca_3y,
        "Color": ca_class,
        "Color 1Y": ca_class_1y,
        "Color 3Y": ca_class_3y
    })

    # ------------------ 2) Total Assets (€) ------------------
    ta_now, ta_1y, ta_3y = get_growth_metrics("Total Assets")
    ta_class    = classify_metric(ta_now, ANALYSIS_THRESHOLDS["TotalAssets"])
    ta_class_1y = classify_metric(ta_1y, ANALYSIS_THRESHOLDS["TotalAssetsGrowth"])
    ta_class_3y = classify_metric(ta_3y, ANALYSIS_THRESHOLDS["TotalAssetsGrowth"])

    rows.append({
        "Metric": "Total Assets (€)",
        "Latest Value": ta_now,
        "1Y Growth (%)": ta_1y,
        "3Y CAGR (%)": ta_3y,
        "Color": ta_class,
        "Color 1Y": ta_class_1y,
        "Color 3Y": ta_class_3y
    })

    # ------------------ 3) Current Liabilities (€) ------------------
    cl_now, cl_1y, cl_3y = get_growth_metrics("Current Liabilities")
    cl_class    = classify_metric(cl_now, ANALYSIS_THRESHOLDS["CurrentLiabilities"])
    cl_class_1y = classify_metric(cl_1y, ANALYSIS_THRESHOLDS["CurrentLiabilitiesGrowth"])
    cl_class_3y = classify_metric(cl_3y, ANALYSIS_THRESHOLDS["CurrentLiabilitiesGrowth"])

    rows.append({
        "Metric": "Current Liabilities (€)",
        "Latest Value": cl_now,
        "1Y Growth (%)": cl_1y,
        "3Y CAGR (%)": cl_3y,
        "Color": cl_class,
        "Color 1Y": cl_class_1y,
        "Color 3Y": cl_class_3y
    })

    # ------------------ 4) Total Liabilities (€) ------------------
    # According to your new index, 
    # "Total Liabilities Net Minority Interest" is the row for total liabilities
    tl_now, tl_1y, tl_3y = get_growth_metrics("Total Liabilities Net Minority Interest")
    tl_class    = classify_metric(tl_now, ANALYSIS_THRESHOLDS["TotalLiabilities"])
    tl_class_1y = classify_metric(tl_1y, ANALYSIS_THRESHOLDS["TotalLiabilitiesGrowth"])
    tl_class_3y = classify_metric(tl_3y, ANALYSIS_THRESHOLDS["TotalLiabilitiesGrowth"])

    rows.append({
        "Metric": "Total Liabilities (€)",
        "Latest Value": tl_now,
        "1Y Growth (%)": tl_1y,
        "3Y CAGR (%)": tl_3y,
        "Color": tl_class,
        "Color 1Y": tl_class_1y,
        "Color 3Y": tl_class_3y
    })

    # ------------------ 5) Working Capital (€) ------------------
    wc_now, wc_1y, wc_3y = get_growth_metrics("Working Capital")
    wc_class    = classify_metric(wc_now, ANALYSIS_THRESHOLDS["WorkingCapital"])
    wc_class_1y = classify_metric(wc_1y, ANALYSIS_THRESHOLDS["WorkingCapitalGrowth"])
    wc_class_3y = classify_metric(wc_3y, ANALYSIS_THRESHOLDS["WorkingCapitalGrowth"])

    rows.append({
        "Metric": "Working Capital (€)",
        "Latest Value": wc_now,
        "1Y Growth (%)": wc_1y,
        "3Y CAGR (%)": wc_3y,
        "Color": wc_class,
        "Color 1Y": wc_class_1y,
        "Color 3Y": wc_class_3y
    })

    # ------------------ 6) Current Ratio (#) ------------------
    # = Current Assets / Current Liabilities
    ca_latest = safe_val(balance_df, "Current Assets", bal_cols[0])
    cl_latest = safe_val(balance_df, "Current Liabilities", bal_cols[0])
    cr_now = None
    if ca_latest and cl_latest and cl_latest != 0:
        cr_now = ca_latest / abs(cl_latest)

    ca_1_ = safe_val(balance_df, "Current Assets", bal_cols[1]) if len(bal_cols) > 1 else None
    cl_1_ = safe_val(balance_df, "Current Liabilities", bal_cols[1]) if len(bal_cols) > 1 else None
    cr_1  = (ca_1_ / abs(cl_1_)) if (ca_1_ and cl_1_ and cl_1_ != 0) else None

    ca_3_ = safe_val(balance_df, "Current Assets", bal_cols[3]) if len(bal_cols) > 3 else None
    cl_3_ = safe_val(balance_df, "Current Liabilities", bal_cols[3]) if len(bal_cols) > 3 else None
    cr_3  = (ca_3_ / abs(cl_3_)) if (ca_3_ and cl_3_ and cl_3_ != 0) else None

    _, cr_1y, cr_3y = calc_growth_metrics(cr_now, cr_1, cr_3)

    cr_class    = classify_metric(cr_now, ANALYSIS_THRESHOLDS["CurrentRatio"])
    cr_class_1y = classify_metric(cr_1, ANALYSIS_THRESHOLDS["CurrentRatioGrowth"])
    cr_class_3y = classify_metric(cr_3, ANALYSIS_THRESHOLDS["CurrentRatioGrowth"])

    rows.append({
        "Metric": "Current Ratio (#)",
        "Latest Value": cr_now,
        "1Y Growth (%)": cr_1y,
        "3Y CAGR (%)": cr_3y,
        "Color": cr_class,
        "Color 1Y": cr_class_1y,
        "Color 3Y": cr_class_3y
    })

    # ------------------ 7) Common Stock Equity (€) => "Equity" ------------------
    eq_now, eq_1y, eq_3y = get_growth_metrics("Common Stock Equity")
    eq_class    = classify_metric(eq_now, ANALYSIS_THRESHOLDS["Equity"])
    eq_class_1y = classify_metric(eq_1y, ANALYSIS_THRESHOLDS["EquityGrowth"])
    eq_class_3y = classify_metric(eq_3y, ANALYSIS_THRESHOLDS["EquityGrowth"])

    rows.append({
        "Metric": "Equity (€)",
        "Latest Value": eq_now,
        "1Y Growth (%)": eq_1y,
        "3Y CAGR (%)": eq_3y,
        "Color": eq_class,
        "Color 1Y": eq_class_1y,
        "Color 3Y": eq_class_3y
    })

    # ------------------ 8) Return on Equity (ROE) (%) ------------------
    #   ROE = Net Income / Common Stock Equity * 100

    # Fetch required values from the income statement and balance sheet
    ni_now = safe_val(income_df, "Net Income", inc_cols[0])
    ni_1y = safe_val(income_df, "Net Income", inc_cols[1] if len(inc_cols) >= 2 else None)
    ni_3y = safe_val(income_df, "Net Income", inc_cols[3] if len(inc_cols) >= 4 else None)

    eq_now = safe_val(balance_df, "Common Stock Equity", bal_cols[0])  # Fetch equity from balance sheet
    eq_1y = safe_val(balance_df, "Common Stock Equity", bal_cols[1] if len(bal_cols) >= 2 else None)
    eq_3y = safe_val(balance_df, "Common Stock Equity", bal_cols[3] if len(bal_cols) >= 4 else None)

    # Initialize ROE values
    roe_now = None
    roe_1 = None
    roe_3 = None

    # Calculate ROE values
    if eq_now and eq_now != 0 and ni_now is not None:
        roe_now = (ni_now / abs(eq_now)) * 100.0

    if eq_1y and eq_1y != 0 and ni_1y is not None:
        roe_1 = (ni_1y / abs(eq_1y)) * 100.0

    if eq_3y and eq_3y != 0 and ni_3y is not None:
        roe_3 = (ni_3y / abs(eq_3y)) * 100.0

    # Calculate growth metrics
    _, roe_1y_growth, roe_3y_cagr = calc_growth_metrics(roe_now, roe_1, roe_3)


    # Classify ROE metrics
    roe_class = classify_metric(roe_now, ANALYSIS_THRESHOLDS["ReturnOnEquity"])
    roe_class_1y = classify_metric(roe_1y_growth, ANALYSIS_THRESHOLDS["ReturnOnEquityGrowth"])
    roe_class_3y = classify_metric(roe_3y_cagr, ANALYSIS_THRESHOLDS["ReturnOnEquityGrowth"])


    # Append ROE row to the results
    rows.append({
        "Metric": "Return on Equity (%)",
        "Latest Value": roe_now,
        "1Y Growth (%)": roe_1y_growth,
        "3Y CAGR (%)": roe_3y_cagr,
        "Color": roe_class,
        "Color 1Y": roe_class_1y,
        "Color 3Y": roe_class_3y
    })

    # ------------------ 9) Equity Ratio (%) => Common Stock Equity / Total Assets * 100
    eq_c0 = safe_val(balance_df, "Common Stock Equity", bal_cols[0])
    ta_c0 = safe_val(balance_df, "Total Assets", bal_cols[0])
    eq_ratio_now = (eq_c0 / abs(ta_c0))*100 if (eq_c0 and ta_c0 and ta_c0 != 0) else None

    eq_c1 = safe_val(balance_df, "Common Stock Equity", bal_cols[1]) if len(bal_cols) > 1 else None
    ta_c1 = safe_val(balance_df, "Total Assets", bal_cols[1]) if len(bal_cols) > 1 else None
    eq_ratio_1 = (eq_c1 / abs(ta_c1))*100 if (eq_c1 and ta_c1 and ta_c1 != 0) else None

    eq_c3 = safe_val(balance_df, "Common Stock Equity", bal_cols[3]) if len(bal_cols) > 3 else None
    ta_c3 = safe_val(balance_df, "Total Assets", bal_cols[3]) if len(bal_cols) > 3 else None
    eq_ratio_3 = (eq_c3 / abs(ta_c3))*100 if (eq_c3 and ta_c3 and ta_c3 != 0) else None

    _, eqr_1y, eqr_3y = calc_growth_metrics(eq_ratio_now, eq_ratio_1, eq_ratio_3)

    eq_ratio_class    = classify_metric(eq_ratio_now, ANALYSIS_THRESHOLDS["EquityRatio"])
    eq_ratio_class_1y = classify_metric(eq_ratio_1, ANALYSIS_THRESHOLDS["EquityRatioGrowth"])
    eq_ratio_class_3y = classify_metric(eq_ratio_3, ANALYSIS_THRESHOLDS["EquityRatioGrowth"])

    rows.append({
        "Metric": "Equity Ratio (%)",
        "Latest Value": eq_ratio_now,
        "1Y Growth (%)": eqr_1y,
        "3Y CAGR (%)": eqr_3y,
        "Color": eq_ratio_class,
        "Color 1Y": eq_ratio_class_1y,
        "Color 3Y": eq_ratio_class_3y
    })

    # ------------------ 10) Dept Ratio (Gearing) (%) => Total Liabilities / Equity * 100
    tl_0 = safe_val(balance_df, "Total Liabilities Net Minority Interest", bal_cols[0])
    eq_0 = safe_val(balance_df, "Common Stock Equity", bal_cols[0])
    d_ratio_now = (tl_0 / abs(eq_0))*100 if (tl_0 and eq_0 and eq_0 != 0) else None

    tl_1 = safe_val(balance_df, "Total Liabilities Net Minority Interest", bal_cols[1]) if len(bal_cols) > 1 else None
    eq_1 = safe_val(balance_df, "Common Stock Equity", bal_cols[1]) if len(bal_cols) > 1 else None
    d_ratio_1 = (tl_1 / abs(eq_1))*100 if (tl_1 and eq_1 and eq_1 != 0) else None

    tl_3 = safe_val(balance_df, "Total Liabilities Net Minority Interest", bal_cols[3]) if len(bal_cols) > 3 else None
    eq_3 = safe_val(balance_df, "Common Stock Equity", bal_cols[3]) if len(bal_cols) > 3 else None
    d_ratio_3 = (tl_3 / abs(eq_3))*100 if (tl_3 and eq_3 and eq_3 != 0) else None

    _, d_r_1y, d_r_3y = calc_growth_metrics(d_ratio_now, d_ratio_1, d_ratio_3)

    d_ratio_class    = classify_metric(d_ratio_now, ANALYSIS_THRESHOLDS["DebtRatio"])
    d_ratio_class_1y = classify_metric(d_r_1y, ANALYSIS_THRESHOLDS["DebtRatioGrowth"])
    d_ratio_class_3y = classify_metric(d_r_3y, ANALYSIS_THRESHOLDS["DebtRatioGrowth"])

    rows.append({
        "Metric": "Dept Ratio (Gearing) (%)",
        "Latest Value": d_ratio_now,
        "1Y Growth (%)": d_r_1y,
        "3Y CAGR (%)": d_r_3y,
        "Color": d_ratio_class,
        "Color 1Y": d_ratio_class_1y,
        "Color 3Y": d_ratio_class_3y
    })


    # 2) Convert rows -> DataFrame, then display
    df_analysis = pd.DataFrame(rows)
    _display_analysis_table(df_analysis)
    return df_analysis


def _display_analysis_table(df_analysis):
    """
    Takes a DataFrame with columns:
      "Metric", "Latest Value", "1Y Growth (%)", "3Y CAGR (%)",
      "Color", "Color 1Y", "Color 3Y"
    Then formats numeric cells and color-codes each row 
    before showing the final table in Streamlit.
    """

    if df_analysis.empty:
        st.info("No rows to display in the Balance Sheet analysis table.")
        return

    # 1) Format numeric cells
    formatted_data = []
    for _, row in df_analysis.iterrows():
        formatted_row = {
            "Metric":         row["Metric"],
            "Latest Value":   format_cell(row["Latest Value"], row["Metric"]),
            "1Y Growth (%)":  format_cell(row["1Y Growth (%)"], "%"),
            "3Y CAGR (%)":    format_cell(row["3Y CAGR (%)"], "%"),
            "Color":          row.get("Color", "gray"),
            "Color 1Y":       row.get("Color 1Y", "gray"),
            "Color 3Y":       row.get("Color 3Y", "gray")
        }
        formatted_data.append(formatted_row)

    df_formatted = pd.DataFrame(formatted_data)

    # 2) We show columns in a specific order
    display_cols = ["Metric", "Latest Value", "1Y Growth (%)", "3Y CAGR (%)"]
    df_display = df_formatted[display_cols]

    # 3) Color-coding for each row
    def row_style(row):
        idx = row.name
        color_main = df_formatted.loc[idx, "Color"]
        color_1y   = df_formatted.loc[idx, "Color 1Y"]
        color_3y   = df_formatted.loc[idx, "Color 3Y"]

        return [
            "",  # no background color for Metric
            color_cell(row["Latest Value"], color_main),
            color_cell(row["1Y Growth (%)"], color_1y),
            color_cell(row["3Y CAGR (%)"], color_3y),
        ]

    styled = df_display.style.apply(row_style, axis=1)
    st.table(styled)
