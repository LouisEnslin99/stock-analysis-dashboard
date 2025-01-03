import streamlit as st
import pandas as pd
import plotly.express as px

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from finance.data_fetcher import fetch_financial_statements
from finance.data_processor import format_dataframe
from finance.config import (
    BALANCE_TOP_5, BALANCE_NEXT_15,
    CASHFLOW_TOP_5, CASHFLOW_NEXT_15,
    INCOME_TOP_5, INCOME_NEXT_15
)

def show_financials_tab(selected_ticker):
    """
    Displays financial statements for the selected stock ticker, side-by-side:
      - Left: an AgGrid table with row selection
      - Right: a chart that displays the selected row
    """
    st.subheader(f"Financial Statements for {selected_ticker}")

    # 1) Fetch data
    balance_df, income_df, cashflow_df = fetch_financial_statements(selected_ticker)

    # 2) Format the data (fill N/A, etc.)
    balance_df = format_dataframe(balance_df)
    income_df = format_dataframe(income_df)
    cashflow_df = format_dataframe(cashflow_df)

    # 3) Combine data into one DataFrame for demonstration
    combined_df = _combine_dataframes_for_display(
        {
            "Income": income_df,
            "Balance": balance_df,
            "Cashflow": cashflow_df,
        }
    )

    # 4) Split layout: table on the left, chart on the right
    col_left, col_right = st.columns([1, 1.5], gap="large")

    with col_left:
        st.write("### Select a row to plot →")

        # Build AgGrid options
        gb = GridOptionsBuilder.from_dataframe(combined_df)
        gb.configure_selection(
            use_checkbox=False,
            selection_mode="single"
        )
        gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=10)
        grid_options = gb.build()

        # Render AgGrid
        grid_response = AgGrid(
            combined_df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=True,
            theme="balham",
        )

    with col_right:
        st.write("### Selected Metric Chart")

        selected_rows = grid_response["selected_rows"]
        # According to your debug info, 'selected_rows' is a DataFrame. Let's handle that safely.
        if isinstance(selected_rows, pd.DataFrame):
            # If there's at least 1 row selected
            if not selected_rows.empty:
                # Pull the first selected row
                row_series = selected_rows.iloc[0]  # row_series is a Series
                metric_name = row_series["Metric"]
                category = row_series["Category"]

                # Build the data for plotting
                data_for_plot = _row_to_plot_data(row_series)
                fig = px.bar(data_for_plot, x="Year", y="Value",
                             title=f"{category} – {metric_name}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No row selected yet. Please select a row in the table.")
        else:
            # If selected_rows is not a DataFrame, handle it differently (list, etc.)
            st.warning("selected_rows is not a DataFrame, check your AgGrid config.")


def _row_to_plot_data(row_series):
    """
    Convert a Pandas Series (one row) into a DataFrame with columns [Year, Value].
    We skip 'Metric' and 'Category' columns, focusing on the year columns.
    """
    year_value_pairs = []
    for col_name, val_str in row_series.items():
        if col_name in ["Metric", "Category"]:
            continue
        numeric_val = _parse_dollar_string(val_str)
        if numeric_val is not None:
            year_value_pairs.append((col_name, numeric_val))

    df = pd.DataFrame(year_value_pairs, columns=["Year", "Value"])
    return df


def _parse_dollar_string(value_str):
    """
    Convert '$1,234.56' -> float(1234.56).
    Return None if it's 'N/A' or unparseable.
    """
    if not value_str or value_str == "N/A":
        return None
    try:
        cleaned = value_str.replace("$", "").replace(",", "")
        return float(cleaned)
    except ValueError:
        return None


def _combine_dataframes_for_display(dfs_dict):
    """
    Combine multiple dataframes (Income, Balance, Cashflow) into one wide DataFrame.
    Each DF should have row labels as metrics. We'll reset_index and add a 'Category' column.
    """
    frames = []
    for category, df in dfs_dict.items():
        temp = df.copy().reset_index()
        temp.rename(columns={"index": "Metric"}, inplace=True)
        temp["Category"] = category
        frames.append(temp)

    combined = pd.concat(frames, axis=0, ignore_index=True)

    # Ensure 'Category' and 'Metric' are leftmost
    cols = list(combined.columns)
    if "Category" in cols:
        cols.remove("Category")
        cols.insert(0, "Category")
    if "Metric" in cols:
        cols.remove("Metric")
        cols.insert(1, "Metric")
    combined = combined[cols]

    return combined
