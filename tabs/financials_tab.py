from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import streamlit as st
import pandas as pd
import plotly.express as px

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
    Display financial statements with dynamically fetched data.
    Shows the most recent periods available from yfinance.
    """
    if not selected_ticker:
        st.warning("No ticker selected.")
        return

    with st.spinner(f"Loading financial data for {selected_ticker}..."):
        balance_sheet, income_stmt, cash_flow, info = fetch_financial_statements(selected_ticker)

    # Header section with clean styling
    st.markdown(f"<h1 style='font-size: 2.2rem; font-weight: 600; margin-bottom: 0.5rem;'>Financial Statements</h1>", unsafe_allow_html=True)
    
    # Show data period information with subtle styling
    if not balance_sheet.empty:
        latest_date = balance_sheet.columns[0]
        oldest_date = balance_sheet.columns[-1]
        st.markdown(
            f"<p style='color: #888; font-size: 0.95rem; margin-top: 0;'>"
            f"Data period: {oldest_date.strftime('%b %Y')} — {latest_date.strftime('%b %Y')}</p>",
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Format the data
    balance_formatted = format_dataframe(balance_sheet)
    income_formatted = format_dataframe(income_stmt)
    cashflow_formatted = format_dataframe(cash_flow)

    # Create tabs with cleaner styling
    tab1, tab2, tab3 = st.tabs(["Balance Sheet", "Income Statement", "Cash Flow"])

    with tab1:
        st.markdown("<h3 style='font-weight: 500; margin-bottom: 1.5rem;'>Balance Sheet</h3>", unsafe_allow_html=True)
        _render_financial_category(
            dataframe=balance_formatted,
            top_5=BALANCE_TOP_5,
            next_15=BALANCE_NEXT_15,
            category_key="balance"
        )

    with tab2:
        st.markdown("<h3 style='font-weight: 500; margin-bottom: 1.5rem;'>Income Statement</h3>", unsafe_allow_html=True)
        _render_financial_category(
            dataframe=income_formatted,
            top_5=INCOME_TOP_5,
            next_15=INCOME_NEXT_15,
            category_key="income"
        )

    with tab3:
        st.markdown("<h3 style='font-weight: 500; margin-bottom: 1.5rem;'>Cash Flow Statement</h3>", unsafe_allow_html=True)
        _render_financial_category(
            dataframe=cashflow_formatted,
            top_5=CASHFLOW_TOP_5,
            next_15=CASHFLOW_NEXT_15,
            category_key="cashflow"
        )


def _render_financial_category(dataframe, top_5, next_15, category_key):
    """
    Render top 5 metrics directly, then an expander for the next 15 metrics.
    """
    # Display top 5 metrics with subtle section label
    st.markdown("<p style='color: #666; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;'>Key Metrics</p>", unsafe_allow_html=True)
    _render_aggrid_table(
        df=dataframe,
        metric_list=top_5,
        grid_height=220,
        allow_scroll=True,
        table_key=category_key + str(5)
    )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Expander with cleaner label
    with st.expander("Additional Metrics", expanded=False):
        _render_aggrid_table(
            df=dataframe,
            metric_list=next_15,
            grid_height=450,
            allow_scroll=True,
            table_key=category_key + str(15)
        )


def _render_aggrid_table(df, metric_list, grid_height=200, allow_scroll=False, table_key=""):
    """
    Displays an AgGrid table with modern, clean styling.
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

    # 2) Build AgGrid config with modern styling
    gb = GridOptionsBuilder.from_dataframe(subset_df)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    
    # Configure columns
    gb.configure_column(
        "Metric",
        headerName="Metric",
        pinned="left",
        width=250,
        cellStyle={'fontWeight': '500'}
    )
    
    # Style numeric columns
    for col in subset_df.columns:
        if col != "Metric":
            gb.configure_column(
                col,
                type=["numericColumn"],
                precision=2,
                cellStyle={'textAlign': 'right'}
            )

    grid_options = {
        "rowSelection": "single",
        "suppressHorizontalScroll": False,
        "domLayout": "normal" if allow_scroll else "autoHeight",
        "rowHeight": 42,
        "headerHeight": 45,
    }
    
    gb.configure_grid_options(**grid_options)
    built_options = gb.build()

    # 3) Custom theme with cleaner colors
    custom_css = {
        ".ag-root": {
            "border": "1px solid #e0e0e0",
            "border-radius": "8px",
            "overflow": "hidden"
        },
        ".ag-header": {
            "background-color": "#f8f9fa",
            "border-bottom": "2px solid #e0e0e0",
            "font-weight": "600",
            "font-size": "0.9rem"
        },
        ".ag-row": {
            "border-bottom": "1px solid #f0f0f0"
        },
        ".ag-row-hover": {
            "background-color": "#f5f7fa !important"
        },
        ".ag-row-selected": {
            "background-color": "#e8f4f8 !important"
        },
        ".ag-cell": {
            "font-size": "0.9rem",
            "padding": "8px 12px"
        }
    }

    # 4) Render AgGrid
    grid_response = AgGrid(
        subset_df,
        gridOptions=built_options,
        height=grid_height,
        theme="streamlit",
        custom_css=custom_css,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        key=table_key,
        fit_columns_on_grid_load=True
    )

    # 5) Handle row selection
    selected_rows = grid_response.get("selected_rows", None)
    if selected_rows is not None and len(selected_rows) > 0:
        selected_row = selected_rows[0]
        _handle_row_selection(selected_row, subset_df)


def _handle_row_selection(selected_row, dataframe):
    """
    Store the selected row's metric + year-value pairs in session_state.
    """
    metric_name = selected_row.get("Metric", None)
    if not metric_name:
        return

    year_cols = [c for c in dataframe.columns if c != "Metric"]
    year_dict = {}
    
    for col in year_cols:
        val = selected_row.get(col, "N/A")
        year_dict[col] = val

    st.session_state["selected_financial_row"] = {
        "metric": metric_name,
        "year_values": year_dict
    }

    # Show chart immediately
    _show_chart_inline(metric_name, year_dict)


def _show_chart_inline(metric_name, year_dict):
    """
    Display a clean chart inline after selection.
    """
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='font-weight: 500; margin-bottom: 1rem;'>{metric_name} Over Time</h4>", unsafe_allow_html=True)
    
    # Create DataFrame for plotting
    df_for_plot = pd.DataFrame(list(year_dict.items()), columns=["Period", "Value"])
    
    # Parse dollar values
    df_for_plot["Value_Numeric"] = df_for_plot["Value"].apply(_parse_dollar_string)
    df_for_plot = df_for_plot.dropna(subset=["Value_Numeric"])
    
    if df_for_plot.empty:
        st.info("No numeric data available to chart.")
        return
    
    # Try to sort by period
    try:
        df_for_plot["Period"] = pd.to_datetime(df_for_plot["Period"])
        df_for_plot = df_for_plot.sort_values("Period")
    except:
        pass
    
    # Create clean line chart
    fig = px.line(
        df_for_plot,
        x="Period",
        y="Value_Numeric",
        markers=True,
        template="plotly_white"
    )
    
    fig.update_traces(
        line=dict(color="#2563eb", width=2.5),
        marker=dict(size=8, color="#2563eb")
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#f0f0f0"
        ),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#f0f0f0"
        ),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _parse_dollar_string(value_str):
    """Convert '$1,234.56' -> 1234.56. Return None if 'N/A' or unparseable."""
    if not value_str or value_str == "N/A":
        return None
    try:
        cleaned = value_str.replace("$", "").replace(",", "").replace("€", "")
        return float(cleaned)
    except ValueError:
        return None