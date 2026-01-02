import streamlit as st
import pandas as pd
import plotly.express as px

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Your existing imports/data fetchers
from finance.data_fetcher import fetch_financial_statements
from finance.data_processor import format_dataframe
from finance.config.config import (
    BALANCE_TOP_5, BALANCE_NEXT_15,
    CASHFLOW_TOP_5, CASHFLOW_NEXT_15,
    INCOME_TOP_5, INCOME_NEXT_15
)


def show_financials_tab(selected_ticker):
    """
    Displays three sections (Income, Balance, Cash Flow) in a wide layout with dark-themed tables.
    Each section has a top-5 table and an expandable 15-metrics table.
    Both tables can update the pinned chart in the sidebar.
    """
    st.subheader(f"Financial Statements for {selected_ticker}")

    # 1) Fetch and format data
    balance_df, income_df, cashflow_df, _ = fetch_financial_statements(selected_ticker)
    balance_df = format_dataframe(balance_df)
    income_df = format_dataframe(income_df)
    cashflow_df = format_dataframe(cashflow_df)

    # 2) Income Statement
    st.markdown("---")
    st.subheader("Income")
    _render_category_interactive(
        dataframe=income_df,
        top_5=INCOME_TOP_5,
        next_15=INCOME_NEXT_15,
        category_key="income"
    )

    # 3) Balance Sheet
    st.markdown("---")
    st.subheader("Balance")
    _render_category_interactive(
        dataframe=balance_df,
        top_5=BALANCE_TOP_5,
        next_15=BALANCE_NEXT_15,
        category_key="balance"
    )

    # 4) Cash Flow
    st.markdown("---")
    st.subheader("Cash Flow")
    _render_category_interactive(
        dataframe=cashflow_df,
        top_5=CASHFLOW_TOP_5,
        next_15=CASHFLOW_NEXT_15,
        category_key="cashflow"
    )

    # 5) Show the chart pinned in the sidebar (always visible)
    _show_chart_in_sidebar()


def _render_category_interactive(dataframe, top_5, next_15, category_key=""):
    """
    Renders two tables:
      1) A table for the top 5 metrics (dark theme, no blank space).
      2) An expander for the next 15 metrics (also dark theme, scrollable).
    Each table calls '_render_aggrid_table()' to handle row selection.
    """
    st.caption("Top 5 Metrics")
    _render_aggrid_table(
        df=dataframe,
        metric_list=top_5,
        grid_height=200,           # short table for top 5
        allow_scroll=True,
        table_key= category_key + str(5)
    )

    with st.expander("View 15 More Metrics"):
        _render_aggrid_table(
            df=dataframe,
            metric_list=next_15,
            grid_height=400,       # taller table for next 15
            allow_scroll=True,
            table_key= category_key + str(15)
        )


def _render_aggrid_table(df, metric_list, grid_height=200, allow_scroll=False, table_key=""):
    """
    Displays an AgGrid table in dark mode, using the entire table width.
    Formats numeric values to have no decimals.
    """

    # 1) Subset the metrics
    subset_df = df.loc[df.index.intersection(metric_list)].copy()

    # Drop rows that are fully N/A
    subset_df.dropna(how="all", inplace=True)
    if subset_df.empty:
        st.warning("No valid data for these metrics.")
        return

    # Convert index -> column "Metric"
    subset_df.reset_index(inplace=True)
    subset_df.rename(columns={"index": "Metric"}, inplace=True)

    # 2) Format numeric values to integers by truncating decimals
    for col in subset_df.columns:
        if col != "Metric":  # Exclude the Metric column
            subset_df[col] = subset_df[col].apply(
                lambda x: int(x) if pd.notnull(x) and isinstance(x, (int, float)) else x
            )


    # 3) Build AgGrid config
    gb = GridOptionsBuilder.from_dataframe(subset_df)
    gb.configure_selection(selection_mode="single", use_checkbox=False)

    # Let columns auto-fill the space
    grid_options = {
        "rowSelection": "single",
        "rowMultiSelectWithClick": False,
        "suppressRowClickSelection": False
    }
    gb.configure_grid_options(**grid_options)

    # Disable pagination for short tables
    gb.configure_pagination(enabled=False)

    final_grid_options = gb.build()

    # 4) Render the grid
    grid_response = AgGrid(
        subset_df,
        data_return_mode='AS_INPUT', 
        gridOptions=final_grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        theme="balham",  # pick a dark theme
        height=grid_height,   # so we see a scrollbar if content overflows
        key=table_key,
        persist_selection=False,
    )

    # 5) Parse selection
    selected_rows = grid_response["selected_rows"]

    if isinstance(selected_rows, list) and selected_rows:
        row_info = _build_row_info(selected_rows[0])  # parse selected row
        st.session_state["selected_financial_row"] = row_info



def _build_row_info(row_series):
    """
    Convert the selected row into:
      { "metric": "<MetricName>", "year_values": { "2022": floatVal, ... } }
    """
    metric_name = row_series["Metric"]
    year_values = {}
    for col_name, val_str in row_series.items():
        if col_name == "Metric":
            continue
        numeric_val = _parse_dollar_string(val_str)
        if numeric_val is not None:
            year_values[col_name] = numeric_val

    return {"metric": metric_name, "year_values": year_values}





def _parse_dollar_string(value_str):
    """Convert '$1,234.56' -> 1234.56. Return None if 'N/A' or unparseable."""
    if not value_str or value_str == "N/A":
        return None
    try:
        cleaned = value_str.replace("$", "").replace(",", "")
        return float(cleaned)
    except ValueError:
        return None


def _show_chart_in_sidebar():
    with st.sidebar:
        st.header("Selected Metric Chart")
        row_info = st.session_state.get("selected_financial_row", None)
        if not row_info:
            st.info("No metric selected yet.")
            return

        metric_name = row_info["metric"]
        year_dict = row_info["year_values"]
        
        # 1) Make DF: Year vs. Value
        df_for_plot = pd.DataFrame(list(year_dict.items()), columns=["Year", "Value"])

        # Attempt numeric sorting by Year
        try:
            df_for_plot["Year"] = df_for_plot["Year"].astype(int)
        except:
            pass
        df_for_plot.sort_values(by="Year", inplace=True)

        # 2) Chart #1: The main line chart of the metric
        fig_line = px.line(
            df_for_plot, 
            x="Year", y="Value",
            markers=True,
            title=f"{metric_name} Over Time"
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # 3) Calculate YoY growth
        #    If there's only 1 data point, we'll skip.
        yoy_data = []
        for i in range(1, len(df_for_plot)):
            prev_val = df_for_plot["Value"].iloc[i-1]
            curr_val = df_for_plot["Value"].iloc[i]
            if prev_val != 0:
                yoy_pct = ((curr_val - prev_val) / prev_val) * 100
            else:
                yoy_pct = None  # or 0, or skip

            yoy_year = df_for_plot["Year"].iloc[i]  # e.g. 2022
            yoy_data.append((yoy_year, yoy_pct))

        if yoy_data:
            yoy_df = pd.DataFrame(yoy_data, columns=["Year", "YoYPercent"])
            
            # 4) Chart #2: A bar chart of YoY % changes
            fig_yoy = px.bar(
                yoy_df,
                x="Year", y="YoYPercent",
                title=f"{metric_name} Year-over-Year Growth (%)",
                labels={"YoYPercent": "Growth Rate (%)"}
            )
            # Optionally format axis
            fig_yoy.update_yaxes(ticksuffix="%")

            st.plotly_chart(fig_yoy, use_container_width=True)
        else:
            st.warning("Not enough data points for YoY growth.")
