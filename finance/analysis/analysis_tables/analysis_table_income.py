# finance/analysis/analysis_tables/analysis_table_income.py

import streamlit as st
import pandas as pd

from finance.config.analysis_config import ANALYSIS_THRESHOLDS
from finance.analysis.analysis_formulas import (
    compute_growth_1y, compute_cagr_3y, compute_margin, compute_interest_coverage,
    classify_metric
)
from finance.analysis.analysis_utils import safe_val, format_cell, color_cell


def build_income_analysis_table(income_df):
    """
    Build and display an analysis table for the Income Statement.
    Demonstrates usage with metrics like:
      - Revenue ($)
      - Gross-Profit ($)
      - Gross-Profit-Margin (%)
      - EBIT ($)
      - EBIT Margin (%)
      - Interest Coverage Ratio (#)
      - Net Income ($)
      - Net Income Margin (%)
      - R&D to Revenue Ratio (%)
      - Personell Expense (%)

    Each row shows 1-year Growth, 3-year CAGR, and color classifications 
    based on thresholds in the config.
    """

    # 1) Ensure enough columns for 1y & 3y comparisons
    inc_cols = list(income_df.columns)
    if len(inc_cols) < 2:
        st.warning("Not enough data columns for Income Statement (need at least 2).")
        return

    # By assumption:
    #   inc_cols[0] => latest
    #   inc_cols[1] => 1-year ago
    #   inc_cols[3] => 3-year ago
    latest_col = inc_cols[0]
    prev_col   = inc_cols[1] if len(inc_cols) >= 2 else None
    old_3y_col = inc_cols[3] if len(inc_cols) >= 4 else None

    def get_growth_metrics(row_label):
        """
        For a given row_label (e.g. 'Total Revenue'), retrieve:
          - value_now (inc_cols[0])
          - 1-year growth vs inc_cols[1]
          - 3-year CAGR vs inc_cols[3]
        """
        val_latest = safe_val(income_df, row_label, latest_col)
        val_prev   = safe_val(income_df, row_label, prev_col)
        val_3y     = safe_val(income_df, row_label, old_3y_col)

        g1 = compute_growth_1y(val_latest, val_prev)
        g3 = compute_cagr_3y(val_latest, val_3y)
        return val_latest, g1, g3

    def calc_growth_metrics(val_now, val_1y, val_3y_ago):
        """
        A helper to compute 1-year growth & 3-year CAGR 
        from already-fetched numeric values.
        """
        g1 = compute_growth_1y(val_now, val_1y)
        g3 = compute_cagr_3y(val_now, val_3y_ago)
        return val_now, g1, g3

    def get_all_metrics(row_label):
        """
        For a given row_label, safely retrieve up to 4 columns:
          inc_cols[0], inc_cols[1], inc_cols[2], inc_cols[3]
        """
        latest_0 = safe_val(income_df, row_label, inc_cols[0])
        latest_1 = safe_val(income_df, row_label, inc_cols[1])
        latest_2 = safe_val(income_df, row_label, inc_cols[2]) if len(inc_cols) > 2 else None
        latest_3 = safe_val(income_df, row_label, inc_cols[3]) if len(inc_cols) > 3 else None
        return latest_0, latest_1, latest_2, latest_3

    rows = []

    # ------------------ 1) Revenue ($) ------------------
    revenue_now, rev_growth_1y, rev_growth_3y = get_growth_metrics("Total Revenue")
    revenue_class     = classify_metric(revenue_now, ANALYSIS_THRESHOLDS["Revenue"])
    revenue_class_1y  = classify_metric(rev_growth_1y, ANALYSIS_THRESHOLDS["RevenueGrowth"])
    revenue_class_3y  = classify_metric(rev_growth_3y, ANALYSIS_THRESHOLDS["RevenueGrowth"])

    rows.append({
        "Metric": "Revenue ($)",
        "Latest Value": revenue_now,
        "1Y Growth (%)": rev_growth_1y,
        "3Y CAGR (%)": rev_growth_3y,
        "Color": revenue_class,
        "Color 1Y": revenue_class_1y,
        "Color 3Y": revenue_class_3y
    })

    # ------------------ 2) Gross-Profit ($) ------------------
    gp_now, gp1y_val, gp3y_val = get_growth_metrics("Gross Profit")
    gp_class     = classify_metric(gp_now, ANALYSIS_THRESHOLDS["GrossProfit"])
    gp_class_1y  = classify_metric(gp1y_val, ANALYSIS_THRESHOLDS["GrossProfitGrowth"])
    gp_class_3y  = classify_metric(gp3y_val, ANALYSIS_THRESHOLDS["GrossProfitGrowth"])

    rows.append({
        "Metric": "Gross-Profit ($)",
        "Latest Value": gp_now,
        "1Y Growth (%)": gp1y_val,
        "3Y CAGR (%)": gp3y_val,
        "Color": gp_class,
        "Color 1Y": gp_class_1y,
        "Color 3Y": gp_class_3y
    })

    # ------------------ 3) Gross-Profit-Margin (%) ------------------
    gp_now4, gp_1, _, gp_3 = get_all_metrics("Gross Profit")
    rev_now4, rev_1, _, rev_3 = get_all_metrics("Total Revenue")

    gpm_now = compute_margin(gp_now4, rev_now4)  # now
    gpm_1   = compute_margin(gp_1, rev_1)        # 1-year
    gpm_3   = compute_margin(gp_3, rev_3)        # 3-year

    # Growth for GPM
    _, gpm_1y, gpm_3y = calc_growth_metrics(gpm_now, gpm_1, gpm_3)

    gpm_class    = classify_metric(gpm_now, ANALYSIS_THRESHOLDS["GrossProfitMargin"])
    gpm_class_1y = classify_metric(gpm_1, ANALYSIS_THRESHOLDS["GrossProfitMarginGrowth"])
    gpm_class_3y = classify_metric(gpm_3, ANALYSIS_THRESHOLDS["GrossProfitMarginGrowth"])

    rows.append({
        "Metric": "Gross-Profit-Margin (%)",
        "Latest Value": gpm_now,
        "1Y Growth (%)": gpm_1y,
        "3Y CAGR (%)": gpm_3y,
        "Color": gpm_class,
        "Color 1Y": gpm_class_1y,
        "Color 3Y": gpm_class_3y
    })

    # ------------------ 4) EBIT ($) ------------------
    ebit_latest, ebit_growth_1y, ebit_growth_3y = get_growth_metrics("EBIT")
    ebit_class     = classify_metric(ebit_latest, ANALYSIS_THRESHOLDS["EBIT"])
    ebit_class_1y  = classify_metric(ebit_growth_1y, ANALYSIS_THRESHOLDS["EBITGrowth"])
    ebit_class_3y  = classify_metric(ebit_growth_3y, ANALYSIS_THRESHOLDS["EBITGrowth"])

    rows.append({
        "Metric": "EBIT ($)",
        "Latest Value": ebit_latest,
        "1Y Growth (%)": ebit_growth_1y,
        "3Y CAGR (%)": ebit_growth_3y,
        "Color": ebit_class,
        "Color 1Y": ebit_class_1y,
        "Color 3Y": ebit_class_3y
    })

    # ------------------ 5) EBIT Margin (%) ------------------
    ebit_now4, ebit_1, _, ebit_3 = get_all_metrics("EBIT")
    # Reuse rev_now4, rev_1, rev_3 from earlier if desired, or re-fetch:
    rev2_now, rev2_1, _, rev2_3 = get_all_metrics("Total Revenue")

    ebit_margin_now = compute_margin(ebit_now4, rev2_now)
    ebit_margin_1   = compute_margin(ebit_1, rev2_1)
    ebit_margin_3   = compute_margin(ebit_3, rev2_3)

    _, ebit_m_1y, ebit_m_3y = calc_growth_metrics(ebit_margin_now, ebit_margin_1, ebit_margin_3)

    ebit_m_class     = classify_metric(ebit_margin_now, ANALYSIS_THRESHOLDS["EBITMargin"])
    ebit_m_class_1y  = classify_metric(ebit_margin_1, ANALYSIS_THRESHOLDS["EBITMarginGrowth"])
    ebit_m_class_3y  = classify_metric(ebit_margin_3, ANALYSIS_THRESHOLDS["EBITMarginGrowth"])

    rows.append({
        "Metric": "EBIT Margin (%)",
        "Latest Value": ebit_margin_now,
        "1Y Growth (%)": ebit_m_1y,
        "3Y CAGR (%)": ebit_m_3y,
        "Color": ebit_m_class,
        "Color 1Y": ebit_m_class_1y,
        "Color 3Y": ebit_m_class_3y
    })

    # ------------------ 6) Interest Coverage Ratio (#) ------------------
    # (EBIT / Interest Expense)
    # We'll retrieve 4 data points for EBIT & Interest Expense
    ebit_cov_0, ebit_cov_1, ebit_cov_2, ebit_cov_3 = get_all_metrics("EBIT")
    int_now0, int_1, _, int_3 = get_all_metrics("Interest Expense")

    coverage_now = compute_interest_coverage(ebit_cov_0, int_now0)
    coverage_1   = compute_interest_coverage(ebit_cov_1, int_1)
    coverage_3   = compute_interest_coverage(ebit_cov_3, int_3)

    # Growth
    _, coverage_1y, coverage_3y = calc_growth_metrics(coverage_now, coverage_1, coverage_3)

    coverage_class     = classify_metric(coverage_now, ANALYSIS_THRESHOLDS["InterestCoverage"])
    coverage_class_1y  = classify_metric(coverage_1, ANALYSIS_THRESHOLDS["InterestCoverageGrowth"])
    coverage_class_3y  = classify_metric(coverage_3, ANALYSIS_THRESHOLDS["InterestCoverageGrowth"])

    rows.append({
        "Metric": "Interest coverage ratio (#)",
        "Latest Value": coverage_now,
        "1Y Growth (%)": coverage_1y,
        "3Y CAGR (%)": coverage_3y,
        "Color": coverage_class,
        "Color 1Y": coverage_class_1y,
        "Color 3Y": coverage_class_3y
    })

    # ------------------ 7) Net Income ($) ------------------
    ni_latest, ni_1y, ni_3y = get_growth_metrics("Net Income")
    ni_class     = classify_metric(ni_latest, ANALYSIS_THRESHOLDS["NetIncome"])
    ni_class_1y  = classify_metric(ni_1y, ANALYSIS_THRESHOLDS["NetIncomeGrowth"])
    ni_class_3y  = classify_metric(ni_3y, ANALYSIS_THRESHOLDS["NetIncomeGrowth"])

    rows.append({
        "Metric": "Net Income ($)",
        "Latest Value": ni_latest,
        "1Y Growth (%)": ni_1y,
        "3Y CAGR (%)": ni_3y,
        "Color": ni_class,
        "Color 1Y": ni_class_1y,
        "Color 3Y": ni_class_3y
    })

    # ------------------ 8) Net Income Margin (%) ------------------
    ni_0, ni_1, _, ni_3 = get_all_metrics("Net Income")
    rev3_0, rev3_1, _, rev3_3 = get_all_metrics("Total Revenue")

    ni_margin_now = compute_margin(ni_0, rev3_0)
    ni_margin_1   = compute_margin(ni_1, rev3_1)
    ni_margin_3   = compute_margin(ni_3, rev3_3)

    _, ni_m_1y, ni_m_3y = calc_growth_metrics(ni_margin_now, ni_margin_1, ni_margin_3)

    ni_m_class    = classify_metric(ni_margin_now, ANALYSIS_THRESHOLDS["NetIncomeMargin"])
    ni_m_class_1y = classify_metric(ni_margin_1, ANALYSIS_THRESHOLDS["NetIncomeMarginGrowth"])
    ni_m_class_3y = classify_metric(ni_margin_3, ANALYSIS_THRESHOLDS["NetIncomeMarginGrowth"])

    rows.append({
        "Metric": "Net Income Margin (%)",
        "Latest Value": ni_margin_now,
        "1Y Growth (%)": ni_m_1y,
        "3Y CAGR (%)": ni_m_3y,
        "Color": ni_m_class,
        "Color 1Y": ni_m_class_1y,
        "Color 3Y": ni_m_class_3y
    })

    # ------------------ 9) R&D to Revenue Ratio (%) ------------------
    rd_0, rd_1, _, rd_3 = get_all_metrics("Research And Development")
    rev4_0, rev4_1, _, rev4_3 = get_all_metrics("Total Revenue")

    rd_ratio_now = compute_margin(rd_0, rev4_0)       # margin => (R&D / Revenue)*100
    rd_ratio_1   = compute_margin(rd_1, rev4_1)
    rd_ratio_3   = compute_margin(rd_3, rev4_3)

    _, rd_ratio_1y, rd_ratio_3y = calc_growth_metrics(rd_ratio_now, rd_ratio_1, rd_ratio_3)

    rd_ratio_class     = classify_metric(rd_ratio_now, ANALYSIS_THRESHOLDS["RDtoRevenueRatio"])
    rd_ratio_class_1y  = classify_metric(rd_ratio_1, ANALYSIS_THRESHOLDS["RDtoRevenueRatioGrowth"])
    rd_ratio_class_3y  = classify_metric(rd_ratio_3, ANALYSIS_THRESHOLDS["RDtoRevenueRatioGrowth"])

    rows.append({
        "Metric": "R&D to Revenue Ratio (%)",
        "Latest Value": rd_ratio_now,
        "1Y Growth (%)": rd_ratio_1y,
        "3Y CAGR (%)": rd_ratio_3y,
        "Color": rd_ratio_class,
        "Color 1Y": rd_ratio_class_1y,
        "Color 3Y": rd_ratio_class_3y
    })

    # ------------------ 10) Personell Expense (%) ------------------
    # Often approximated by 'Selling General And Administration' if no dedicated row
    pers_0, pers_1, _, pers_3 = get_all_metrics("Selling General And Administration")
    rev5_0, rev5_1, _, rev5_3 = get_all_metrics("Total Revenue")

    pers_ratio_now = compute_margin(pers_0, rev5_0)
    pers_ratio_1   = compute_margin(pers_1, rev5_1)
    pers_ratio_3   = compute_margin(pers_3, rev5_3)

    _, pers_ratio_1y, pers_ratio_3y = calc_growth_metrics(pers_ratio_now, pers_ratio_1, pers_ratio_3)

    pers_class     = classify_metric(pers_ratio_now, ANALYSIS_THRESHOLDS["PersonnelExpense"])
    pers_class_1y  = classify_metric(pers_ratio_1, ANALYSIS_THRESHOLDS["PersonnelExpenseGrowth"])
    pers_class_3y  = classify_metric(pers_ratio_3, ANALYSIS_THRESHOLDS["PersonnelExpenseGrowth"])

    rows.append({
        "Metric": "Personell Expense (%)",
        "Latest Value": pers_ratio_now,
        "1Y Growth (%)": pers_ratio_1y,
        "3Y CAGR (%)": pers_ratio_3y,
        "Color": pers_class,
        "Color 1Y": pers_class_1y,
        "Color 3Y": pers_class_3y
    })

    # 2) Convert the collected rows -> DataFrame
    df_analysis = pd.DataFrame(rows)
    _display_analysis_table(df_analysis)
    return df_analysis


def _display_analysis_table(df_analysis):
    """
    Takes a DataFrame of rows with columns:
      [Metric, Latest Value, 1Y Growth (%), 3Y CAGR (%), Color, Color 1Y, Color 3Y]
    Then does the formatting & color styling before showing in streamlit.
    """

    if df_analysis.empty:
        st.info("No rows to display.")
        return

    # 1) Format numeric cells
    formatted_data = []
    for _, row in df_analysis.iterrows():
        formatted_row = {
            "Metric": row["Metric"],
            "Latest Value": format_cell(row["Latest Value"], row["Metric"]),
            "1Y Growth (%)": format_cell(row["1Y Growth (%)"], "%"),
            "3Y CAGR (%)": format_cell(row["3Y CAGR (%)"], "%"),
            "Color": row.get("Color", "gray"),
            "Color 1Y": row.get("Color 1Y", "gray"),
            "Color 3Y": row.get("Color 3Y", "gray")
        }
        formatted_data.append(formatted_row)

    df_formatted = pd.DataFrame(formatted_data)

    # 2) We'll style the DataFrame
    display_cols = ["Metric", "Latest Value", "1Y Growth (%)", "3Y CAGR (%)"]
    df_display = df_formatted[display_cols]

    def row_style(row):
        idx = row.name
        color_main = df_formatted.loc[idx, "Color"]
        color_1y   = df_formatted.loc[idx, "Color 1Y"]
        color_3y   = df_formatted.loc[idx, "Color 3Y"]
        return [
            "",  # Metric => no color
            color_cell(row["Latest Value"], color_main),
            color_cell(row["1Y Growth (%)"], color_1y),
            color_cell(row["3Y CAGR (%)"], color_3y),
        ]

    styled = df_display.style.apply(row_style, axis=1)
    st.table(styled)
