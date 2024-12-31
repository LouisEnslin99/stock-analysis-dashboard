# tabs/analysis_tab.py
import streamlit as st
import pandas as pd
from finance.data_fetcher import fetch_financial_statements
from finance.data_processor import process_financial_data, highlight_values
from finance.config import DEFAULT_TICKER, GREEN_THRESHOLD

def show_analysis_tab():
    st.subheader("Financial Analysis")

    ticker = st.text_input("Enter Stock Ticker", value=DEFAULT_TICKER, key="analysis_ticker")
    balance, income, cashflow = fetch_financial_statements(ticker)
    financials = process_financial_data(balance, income, cashflow)

    # Example: highlight 'income' DataFrame based on a threshold
    if "income" in financials:
        styled_income_df = financials["income"].style.applymap(
            lambda x: highlight_values(x, GREEN_THRESHOLD)
        )
        st.write("Income Statement (highlighted):")
        st.dataframe(styled_income_df, use_container_width=True)
    else:
        st.warning("No income data available.")
