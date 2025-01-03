import streamlit as st
from finance.data_fetcher import fetch_financial_statements
from finance.data_processor import process_financial_data
from finance.config import (
    BALANCE_TOP_5, BALANCE_NEXT_15,
    CASHFLOW_TOP_5, CASHFLOW_NEXT_15,
    INCOME_TOP_5, INCOME_NEXT_15
)
import pandas as pd


def show_financials_tab(selected_ticker):
    """
    Displays financial statements for the selected stock ticker,
    focusing on the top metrics and expandable additional metrics.
    """
    st.subheader(f"Financial Statements for {selected_ticker}")

    # Fetch and process financial data
    balance, income, cashflow = fetch_financial_statements(selected_ticker)
    financials = {
        "Balance": balance,
        "Income": income,
        "Cashflow": cashflow
    }

    # Render each category
    render_category("Income", income, INCOME_TOP_5, INCOME_NEXT_15)
    render_category("Balance", balance, BALANCE_TOP_5, BALANCE_NEXT_15)
    render_category("Cash Flow", cashflow, CASHFLOW_TOP_5, CASHFLOW_NEXT_15)


def render_category(title, dataframe, top_5_metrics, next_15_metrics):
    """
    Renders a financial category with top metrics and expandable additional metrics.

    :param title: Title of the financial category (e.g., "Income Statement").
    :param dataframe: Pandas DataFrame containing the financial data.
    :param top_5_metrics: List of top 5 metric names to display prominently.
    :param next_15_metrics: List of next 15 metric names to display in an expander.
    """
    st.write(f"### {title}")

    # Ensure the index is set to match the metric names
    if not isinstance(dataframe.index, pd.Index):
        dataframe = dataframe.set_index(dataframe.columns[0])  # Set the first column as index if needed

    # Format the DataFrame for better readability
    formatted_df = format_dataframe(dataframe)

    # Handle missing metrics gracefully
    top_5_df = extract_metrics(formatted_df, top_5_metrics)
    next_15_df = extract_metrics(formatted_df, next_15_metrics)

    # Display top 5 metrics
    st.table(top_5_df)

    # Display next 15 metrics in an expandable section
    with st.expander(f"View More Details for {title}"):
        st.table(next_15_df)


def extract_metrics(dataframe, metrics):
    """
    Extracts specified metrics from a DataFrame. If a metric is missing,
    it adds a row with "N/A" values.

    :param dataframe: The DataFrame to extract metrics from.
    :param metrics: List of metrics to extract.
    :return: A DataFrame with the specified metrics.
    """
    # Ensure all metrics are in the DataFrame
    missing_metrics = [metric for metric in metrics if metric not in dataframe.index]
    if missing_metrics:
        for metric in missing_metrics:
            dataframe.loc[metric] = ["N/A"] * len(dataframe.columns)

    return dataframe.loc[metrics]


def format_dataframe(df):
    """
    Formats a DataFrame for display, ensuring proper formatting for dates, monetary values,
    and handling missing values.

    :param df: The DataFrame to format.
    :return: A formatted DataFrame.
    """
    # Replace missing values with "N/A"
    df = df.fillna("N/A")

    # Format monetary values
    def format_money(value):
        if isinstance(value, (int, float)):
            return f"${value:,.2f}"  # Format as $1,000,000.00
        return value  # Leave non-numeric values unchanged

    formatted_df = df.applymap(format_money)

    # Convert column headers to YYYY-MM if they are datetime-like
    def format_column_name(col):
        try:
            # Attempt to parse and reformat as YYYY-MM
            return pd.to_datetime(col).strftime("%Y-%m")
        except (ValueError, TypeError):
            # Return the column as-is if not a valid date
            return col

    formatted_df.columns = [format_column_name(col) for col in formatted_df.columns]

    return formatted_df



def is_valid_date(value):
    """
    Checks if a string is a valid date.
    """
    try:
        pd.to_datetime(value)
        return True
    except Exception:
        return False
