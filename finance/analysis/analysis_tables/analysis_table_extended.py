import streamlit as st
import pandas as pd


def build_extended_analysis_table(stockInfo: dict):
    """
    Builds a simple table showing the following metrics from stockInfo:
    - Valuation Analysis: marketCap, trailingPE, forwardPE, priceToBook, priceToSalesTrailing12Months
    - Performance Tracking: currentPrice, fiftyTwoWeekHigh, fiftyTwoWeekLow, volume

    The values are formatted appropriately:
    - Dollar values are formatted as "$" with commas.
    - Ratios are shown with 2 decimal places.
    """

    # Helper function to format values
    def format_value(metric, value):
        if "($)" in metric or "Price" in metric or "Cap" in metric:
            # Format as dollars
            return f"${value:,.2f}" if value is not None else "N/A"
        elif "P/E" in metric or "Price to" in metric:
            # Format as ratio with 2 decimal places
            return f"{value:.2f}" if value is not None else "N/A"
        elif "Volume" in metric:
            # Format as plain number with commas
            return f"{value:,}" if value is not None else "N/A"
        else:
            # Default to showing raw value
            return value

    # Prepare rows for display
    rows = [
        {"Metric": "Market Cap ($)", "Value": stockInfo.get("marketCap")},
        {"Metric": "Trailing P/E", "Value": stockInfo.get("trailingPE")},
        {"Metric": "Forward P/E", "Value": stockInfo.get("forwardPE")},
        {"Metric": "Price to Book", "Value": stockInfo.get("priceToBook")},
        {"Metric": "Price to Sales (TTM)", "Value": stockInfo.get("priceToSalesTrailing12Months")},
        {"Metric": "Current Price ($)", "Value": stockInfo.get("currentPrice")},
        {"Metric": "52-Week High ($)", "Value": stockInfo.get("fiftyTwoWeekHigh")},
        {"Metric": "52-Week Low ($)", "Value": stockInfo.get("fiftyTwoWeekLow")},
        {"Metric": "Volume", "Value": stockInfo.get("volume")},
    ]

    # Format rows
    formatted_rows = [{"Metric": row["Metric"], "Value": format_value(row["Metric"], row["Value"])} for row in rows]

    # Convert to DataFrame
    df_info = pd.DataFrame(formatted_rows)

    # Streamlit Table with markdown styling for left alignment
    st.markdown(
        """
        <style>
        thead tr th {text-align: left !important;}
        tbody tr td {text-align: left !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Display as a table
    st.table(df_info)
    return df_info
