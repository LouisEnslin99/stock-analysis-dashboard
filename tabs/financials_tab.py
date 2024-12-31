# tabs/financials_tab.py
import streamlit as st
from finance.data_fetcher import fetch_financial_statements
from finance.data_processor import process_financial_data
from finance.data_exporter import export_to_excel

def show_financials_tab(selected_ticker):
    """
    Displays financial statements for the selected stock ticker.
    Allows exporting the financial data as an Excel file.
    """

    # Fetch and process financial data for the selected ticker
    st.subheader(f"Financial Statements for {selected_ticker}")
    balance, income, cashflow = fetch_financial_statements(selected_ticker)
    financials = process_financial_data(balance, income, cashflow)

    # Display financial data in expanders
    with st.expander("Balance Sheet"):
        st.dataframe(financials["balance"])
    with st.expander("Income Statement"):
        st.dataframe(financials["income"])
    with st.expander("Cash Flow"):
        st.dataframe(financials["cashflow"])

    # Automatically download the file when the user clicks "Export to Excel"
    filename, excel_data = export_to_excel(financials, selected_ticker)
    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
