# tabs/financials_tab.py
import streamlit as st
import pandas as pd
from finance.data_fetcher import fetch_financial_statements
from finance.data_processor import process_financial_data
from finance.data_exporter import export_to_excel
from finance.config import DEFAULT_TICKER

def show_financials_tab():
    st.subheader("Financial Statements Over the Years")

    ticker = st.text_input("Enter Stock Ticker", value=DEFAULT_TICKER, key="financials_ticker")
    balance, income, cashflow = fetch_financial_statements(ticker)
    financials = process_financial_data(balance, income, cashflow)

    # Display them as tables in Streamlit
    with st.expander("Balance Sheet"):
        st.dataframe(financials["balance"])
    with st.expander("Income Statement"):
        st.dataframe(financials["income"])
    with st.expander("Cash Flow"):
        st.dataframe(financials["cashflow"])

    # Button to export to Excel
    if st.button("Export to Excel"):
        filepath = export_to_excel(financials)
        st.success(f"Data exported to: {filepath}")
