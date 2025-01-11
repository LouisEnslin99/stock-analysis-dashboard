# finance/analysis/analysis_tables/analysis_table_cashflow.py

import streamlit as st
import pandas as pd

from finance.config.analysis_config import ANALYSIS_THRESHOLDS
from finance.analysis.analysis_formulas import (
    compute_growth_1y,
    compute_cagr_3y,
    compute_margin,
    classify_metric
)
from finance.analysis.analysis_utils import safe_val, format_cell, color_cell


def build_cashflow_analysis_table(cashflow_df, income_df):
    """
    Build and display an analysis table for the Cash Flow statement,
    with 1-year + 3-year growth. 
    Displays:
      1) Operating Cash Flow (€)
      2) Operating Cash Flow Margin (%)
         = (OperatingCashFlow / Revenue)*100 
         (assuming 'Total Revenue' row is present in this same DataFrame, 
         or else it remains None)

    We assume:
      - cashflow_df.columns[0] => latest
      - cashflow_df.columns[1] => 1-year ago
      - cashflow_df.columns[3] => 3-year ago
    If they are missing, some growth values are None.
    """

    # 1) Ensure enough columns for 1y & 3y
    cf_cols = list(cashflow_df.columns)
    inc_cols = list(income_df.columns)
    if len(cf_cols) < 2:
        st.warning("Not enough data columns for Cash Flow (need at least 2).")
        return

    # col[0] => latest, col[1] => 1-year, col[3] => 3-year
    latest_col = cf_cols[0]
    col_1y     = cf_cols[1] if len(cf_cols) >= 2 else None
    col_3y     = cf_cols[3] if len(cf_cols) >= 4 else None

    def get_growth_metrics(row_label):
        """
        For a row_label, fetch values from 
          cf_cols[0] => now,
          cf_cols[1] => 1-year,
          cf_cols[3] => 3-year
        then compute 1-year growth & 3-year CAGR.
        Returns (val_now, g1, g3).
        """
        val_now = safe_val(cashflow_df, row_label, latest_col)
        val_1y  = safe_val(cashflow_df, row_label, col_1y)
        val_3y  = safe_val(cashflow_df, row_label, col_3y)

        g1 = compute_growth_1y(val_now, val_1y)
        g3 = compute_cagr_3y(val_now, val_3y)
        return val_now, g1, g3

    def calc_growth_metrics(val_now, val_1, val_3):
        """
        For ratio or custom metrics,
        compute 1-year growth & 3-year CAGR from numeric values.
        """
        g1 = compute_growth_1y(val_now, val_1)
        g3 = compute_cagr_3y(val_now, val_3)
        return val_now, g1, g3

    rows = []

    # ------------------ 1) Operating Cash Flow (€) ------------------
    ocf_now, ocf_1y, ocf_3y = get_growth_metrics("Operating Cash Flow")
    ocf_class    = classify_metric(ocf_now, ANALYSIS_THRESHOLDS["OperatingCashFlow"])
    ocf_class_1y = classify_metric(ocf_1y, ANALYSIS_THRESHOLDS["OperatingCashFlowGrowth"])
    ocf_class_3y = classify_metric(ocf_3y, ANALYSIS_THRESHOLDS["OperatingCashFlowGrowth"])

    rows.append({
        "Metric": "Operating Cashflow (€)",
        "Latest Value": ocf_now,
        "1Y Growth (%)": ocf_1y,
        "3Y CAGR (%)": ocf_3y,
        "Color": ocf_class,
        "Color 1Y": ocf_class_1y,
        "Color 3Y": ocf_class_3y
    })

   # ------------------ 2) Operating Cashflow Margin (%) ------------------
    #   Formula: (Operating Cash Flow / Revenue) * 100

    # Fetch Operating Cash Flow values from Cash Flow DataFrame
    ocf_now = safe_val(cashflow_df, "Operating Cash Flow", cf_cols[0])
    ocf_1y = safe_val(cashflow_df, "Operating Cash Flow", cf_cols[1] if len(cf_cols) > 1 else None)
    ocf_3y = safe_val(cashflow_df, "Operating Cash Flow", cf_cols[3] if len(cf_cols) > 3 else None)

    # Fetch Revenue values from Income Statement
    rev_now = safe_val(income_df, "Total Revenue", inc_cols[0])
    rev_1y = safe_val(income_df, "Total Revenue", inc_cols[1] if len(inc_cols) > 1 else None)
    rev_3y = safe_val(income_df, "Total Revenue", inc_cols[3] if len(inc_cols) > 3 else None)

    # Initialize margin values
    ocf_margin_now = None
    ocf_margin_1 = None
    ocf_margin_3 = None

    # Calculate Operating Cashflow Margin
    if ocf_now is not None and rev_now and rev_now != 0:
        ocf_margin_now = (ocf_now / abs(rev_now)) * 100.0

    if ocf_1y is not None and rev_1y and rev_1y != 0:
        ocf_margin_1 = (ocf_1y / abs(rev_1y)) * 100.0

    if ocf_3y is not None and rev_3y and rev_3y != 0:
        ocf_margin_3 = (ocf_3y / abs(rev_3y)) * 100.0

    # Calculate growth metrics for Operating Cashflow Margin
    _, ocf_m_1y, ocf_m_3y = calc_growth_metrics(ocf_margin_now, ocf_margin_1, ocf_margin_3)


    # Classify the metrics
    ocf_margin_class = classify_metric(ocf_margin_now, ANALYSIS_THRESHOLDS["OperatingCashFlowMargin"])
    ocf_margin_class_1y = classify_metric(ocf_m_1y, ANALYSIS_THRESHOLDS["OperatingCashFlowMarginGrowth"])
    ocf_margin_class_3y = classify_metric(ocf_m_3y, ANALYSIS_THRESHOLDS["OperatingCashFlowMarginGrowth"])
    
    # Append results to rows
    rows.append({
        "Metric": "Operating Cashflow Margin (%)",
        "Latest Value": ocf_margin_now,
        "1Y Growth (%)": ocf_m_1y,
        "3Y CAGR (%)": ocf_m_3y,
        "Color": ocf_margin_class,
        "Color 1Y": ocf_margin_class_1y,
        "Color 3Y": ocf_margin_class_3y
    })


    # Convert rows -> DataFrame, then display
    df_analysis = pd.DataFrame(rows)
    _display_analysis_table(df_analysis)
    return df_analysis


def _display_analysis_table(df_analysis):
    """
    Takes a DataFrame with columns:
      "Metric"
      "Latest Value"
      "1Y Growth (%)"
      "3Y CAGR (%)"
      "Color", "Color 1Y", "Color 3Y"
    Then formats numeric cells and color-codes each row 
    before showing the final table in Streamlit.
    """

    if df_analysis.empty:
        st.info("No rows to display in the Cashflow analysis table.")
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

    # 3) Color-coding per row
    def row_style(row):
        idx = row.name
        color_main = df_formatted.loc[idx, "Color"]
        color_1y   = df_formatted.loc[idx, "Color 1Y"]
        color_3y   = df_formatted.loc[idx, "Color 3Y"]

        return [
            "",  # no background for "Metric" column
            color_cell(row["Latest Value"], color_main),
            color_cell(row["1Y Growth (%)"], color_1y),
            color_cell(row["3Y CAGR (%)"], color_3y),
        ]

    styled = df_display.style.apply(row_style, axis=1)
    st.table(styled)