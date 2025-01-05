# analysis_tab.py

import streamlit as st
import pandas as pd

from finance.data_fetcher import fetch_financial_statements
from finance.config.analysis_config import ANALYSIS_THRESHOLDS
from finance.analysis_formulas import (
    compute_growth_1y, compute_cagr_3y, compute_margin, compute_interest_coverage,
    classify_metric
)



def show_analysis_tab(selected_ticker):
    """
    Given the yfinance 'income' DataFrame (with columns = e.g. 2024-09-30, 2023-09-30..., 
    and row labels like 'Total Revenue', 'Gross Profit', 'EBIT', 'Net Income', etc.),
    display the analysis table with color-coded cells.
    
    We'll demonstrate with the 10 metrics from your table. 
    We'll compute 1-year and 3-year CAGR for each relevant line as well.
    """

    st.subheader("Income Statement")
    balance_df, income_df, cashflow_df = fetch_financial_statements(selected_ticker)

    # 1) Get columns of income dataframe
    inc_cols = income_df.columns
    bal_cols = balance_df.columns
    cash_cols = cashflow_df.columns

    # We'll need the most recent column vs. 1 year prior vs. 4 years prior
    # e.g. income_df.columns[0] = latest, income_df.columns[1] = 1 year back, income_df.columns[3] = 3 years back
    if len(inc_cols) < 2:
        st.warning("Not enough data columns (need at least 2 years).")
        return

    # Helper to safely fetch a value
    def safe_val(row_name, col_name):
        try:
            val = income_df.loc[row_name, col_name]
            return None if pd.isna(val) else float(val)
        except KeyError:
            return None
        except:
            return None
        
    ###### Income specific columns calculations #######
    latest_col = inc_cols[0]
    prev_col   = inc_cols[1] if len(inc_cols) >= 2 else None
    # 3-year older column
    old_3y_col = inc_cols[3] if len(inc_cols) >= 4 else None



    ### 2) Build a DataFrame that holds rows we want in the final display
    rows = []

    # A small helper to compute 1y/3y growth for a specific row label (like "Total Revenue")
    def get_growth_metrics(row_label):
        val_latest = safe_val(row_label, latest_col)
        val_prev   = safe_val(row_label, prev_col)   if prev_col else None
        val_3y     = safe_val(row_label, old_3y_col) if old_3y_col else None
        g1 = compute_growth_1y(val_latest, val_prev)
        g3 = compute_cagr_3y(val_latest, val_3y)
        return val_latest, g1, g3

    # 2.1) Revenue
    revenue_now, rev_growth_1y, rev_growth_3y = get_growth_metrics("Total Revenue")
    revenue_class = classify_metric(revenue_now, ANALYSIS_THRESHOLDS["Revenue"])

    rows.append({
      "Metric": "Revenue (€)",
      "Latest Value": revenue_now,
      "1Y Growth (%)": rev_growth_1y,
      "3Y CAGR (%)": rev_growth_3y,
      "Color": revenue_class,
      "Color 1Y": "gray",
      "Color 3Y": "gray"
    })

    # 2.2) Gross Profit Margin
    gp_now = safe_val("Gross Profit", latest_col)
    # margin = (Gross Profit / Total Revenue)*100
    gpm = None
    if revenue_now and revenue_now != 0:
        gpm = (gp_now / abs(revenue_now)) * 100.0 if gp_now else None
    gpm_class = classify_metric(gpm, ANALYSIS_THRESHOLDS["GrossProfitMargin"])

    # 1y & 3y growth for "Gross Profit"
    gp_latest, gp_growth_1y, gp_growth_3y = get_growth_metrics("Gross Profit")

    rows.append({
      "Metric": "Gross-Profit-Margin (%)",
      "Latest Value": gpm,
      "1Y Growth (%)": gp_growth_1y,
      "3Y CAGR (%)": gp_growth_3y,
      "Color": gpm_class,
      "Color 1Y": "gray",
      "Color 3Y": "gray"
    })

    # 2.3) EBIT Margin
    ebit_now = safe_val("EBIT", latest_col)
    ebit_margin = None
    if ebit_now and revenue_now and revenue_now != 0:
        ebit_margin = (ebit_now / abs(revenue_now))*100.0
    ebit_margin_class = classify_metric(ebit_margin, ANALYSIS_THRESHOLDS["EBITMargin"])
    # 1y & 3y growth for EBIT
    ebit_latest, ebit_growth_1y, ebit_growth_3y = get_growth_metrics("EBIT")

    rows.append({
      "Metric": "EBIT Margin (%)",
      "Latest Value": ebit_margin,
      "1Y Growth (%)": ebit_growth_1y,
      "3Y CAGR (%)": ebit_growth_3y,
      "Color": ebit_margin_class,
      "Color 1Y": "gray",
      "Color 3Y": "gray"
    })

    # 2.4) Interest coverage ratio = EBIT / Interest Expense
    interest_exp = safe_val("Interest Expense", latest_col)
    icr = None
    if ebit_now and interest_exp and interest_exp != 0:
        icr = ebit_now / abs(interest_exp)
    icr_class = classify_metric(icr, ANALYSIS_THRESHOLDS["InterestCoverage"])
    # For growth, we can do 1y & 3y for interest coverage if needed:
    # That might be out of scope. We'll skip to keep it short.

    rows.append({
      "Metric": "Interest coverage ratio (#)",
      "Latest Value": icr,
      "1Y Growth (%)": None,
      "3Y CAGR (%)": None,
      "Color": icr_class,
      "Color 1Y": "gray",
      "Color 3Y": "gray"
    })

    # 2.5) Net Income Margin
    ni_now = safe_val("Net Income", latest_col)
    ni_margin = None
    if ni_now and revenue_now and revenue_now != 0:
        ni_margin = (ni_now / abs(revenue_now))*100.0
    ni_margin_class = classify_metric(ni_margin, ANALYSIS_THRESHOLDS["NetIncomeMargin"])
    # 1y & 3y growth for net income
    ni_latest, ni_growth_1y, ni_growth_3y = get_growth_metrics("Net Income")

    rows.append({
      "Metric": "Net Income Margin (%)",
      "Latest Value": ni_margin,
      "1Y Growth (%)": ni_growth_1y,
      "3Y CAGR (%)": ni_growth_3y,
      "Color": ni_margin_class,
      "Color 1Y": "gray",
      "Color 3Y": "gray"
    })

    # 2.6) R&D to Revenue Ratio
    rd_now = safe_val("Research And Development", latest_col)
    rd_ratio = None
    if rd_now and revenue_now and revenue_now != 0:
        rd_ratio = (rd_now / abs(revenue_now))*100.0
    rd_class = classify_metric(rd_ratio, ANALYSIS_THRESHOLDS["RDtoRevenueRatio"])
    # 1y & 3y growth for R&D
    rd_latest, rd_g1, rd_g3 = get_growth_metrics("Research And Development")

    rows.append({
      "Metric": "R&D to Revenue Ratio (%)",
      "Latest Value": rd_ratio,
      "1Y Growth (%)": rd_g1,
      "3Y CAGR (%)": rd_g3,
      "Color": rd_class,
      "Color 1Y": "gray",
      "Color 3Y": "gray"
    })

    # 2.7) Personell Expense => 'Selling General And Administration' might not be exactly the same.
    # Some statements have a separate "Personnel Expense" row, but let's approximate with "S G & A".
    # Or if you truly have a "Personnel Expense" row, adapt accordingly.
    pers_now = safe_val("Selling General And Administration", latest_col)
    pers_ratio = None
    if pers_now and revenue_now and revenue_now != 0:
        pers_ratio = (pers_now / abs(revenue_now))*100.0
    pers_class = classify_metric(pers_ratio, ANALYSIS_THRESHOLDS["PersonnelExpenseRatio"])
    # Growth
    pers_latest, pers_g1, pers_g3 = get_growth_metrics("Selling General And Administration")

    rows.append({
      "Metric": "Personell Expense (%)",
      "Latest Value": pers_ratio,
      "1Y Growth (%)": pers_g1,
      "3Y CAGR (%)": pers_g3,
      "Color": pers_class,
      "Color 1Y": "gray",
      "Color 3Y": "gray"
    })

    ### 3) Convert rows -> DataFrame for display
    df_analysis = pd.DataFrame(rows)

    # 3.1) Define the formatting function
    def format_cell(value, metric):
        """
        Format cell values based on the metric type:
        - Currency: No decimals, add commas (€, $).
        - Percentage: 2 decimals.
        - Replace NaN with 'n/a'.
        """
        if pd.isna(value):
            return "n/a"
        if "€" in metric or "$" in metric:  # Currency formatting
            return f"{int(value):,}"
        elif "%" in metric:  # Percentage formatting
            return f"{value:.2f}%"
        else:  # General numeric formatting
            return f"{value:.2f}"

    # 3.2) Apply formatting to the DataFrame
    formatted_data = []
    for _, row in df_analysis.iterrows():
        formatted_row = {
            "Metric": row["Metric"],
            "Latest Value": format_cell(row["Latest Value"], row["Metric"]),
            "1Y Growth (%)": format_cell(row["1Y Growth (%)"], "%"),
            "3Y CAGR (%)": format_cell(row["3Y CAGR (%)"], "%"),
            "Color": row["Color"],
            "Color 1Y": row["Color 1Y"],
            "Color 3Y": row["Color 3Y"]
        }
        formatted_data.append(formatted_row)

    df_formatted = pd.DataFrame(formatted_data)

    # 4) We'll style the DataFrame to color-code the columns "Latest Value", "1Y Growth (%)", "3Y CAGR (%)"
    #    based on the "Color", "Color 1Y", "Color 3Y" columns.

    def color_cell(val, color_code):
        # Return background color CSS
        colors = {
            "green": "background-color: #3CB371;",  # light green
            "yellow": "background-color: #D2B55B;", # light yellow
            "red": "background-color: #CD5C5C;",    # light red
            "gray": "background-color: #696969;",
        }
        return colors.get(color_code, "")

    # 4.1) Re-organize columns for display
    display_cols = ["Metric", "Latest Value", "1Y Growth (%)", "3Y CAGR (%)"]
    df_display = df_formatted[display_cols]

    # 4.2) Apply row-wise styling for color-coding
    def row_style(row):
        # Get row index
        idx = row.name
        color_main = df_formatted.loc[idx, "Color"]
        color_1y = df_formatted.loc[idx, "Color 1Y"]
        color_3y = df_formatted.loc[idx, "Color 3Y"]

        # Style the relevant columns
        return [
            "",  # Metric (no color)
            color_cell(row["Latest Value"], color_main),
            color_cell(row["1Y Growth (%)"], color_1y),
            color_cell(row["3Y CAGR (%)"], color_3y),
        ]

    # Apply the row styles
    styled = df_display.style.apply(row_style, axis=1)

    # Display the table in Streamlit
    st.table(styled)

