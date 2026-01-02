"""
Financials Tab Module

This module handles the display of financial data in the Streamlit dashboard.
It includes functions for rendering interactive financial tables using AgGrid.
"""

import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode


def show_financials_tab(financials_data: dict, selected_ticker: str):
    """
    Display the financials tab with interactive tables for different financial categories.

    Args:
        financials_data: Dictionary containing financial data for different categories
        selected_ticker: The currently selected stock ticker symbol
    """
    st.header("Financial Statements")

    if not financials_data or all(v is None or (isinstance(v, pd.DataFrame) and v.empty) 
                                   for v in financials_data.values()):
        st.warning("No financial data available for this stock.")
        return

    # Create tabs for different financial categories
    tabs = st.tabs([
        "Income Statement",
        "Balance Sheet",
        "Cash Flow",
        "Valuation Metrics",
        "Growth Metrics"
    ])

    with tabs[0]:
        _render_category_interactive(
            financials_data.get('income_statement'),
            "Income Statement",
            "income_statement",
            selected_ticker
        )

    with tabs[1]:
        _render_category_interactive(
            financials_data.get('balance_sheet'),
            "Balance Sheet",
            "balance_sheet",
            selected_ticker
        )

    with tabs[2]:
        _render_category_interactive(
            financials_data.get('cash_flow'),
            "Cash Flow Statement",
            "cash_flow",
            selected_ticker
        )

    with tabs[3]:
        _render_category_interactive(
            financials_data.get('valuation_metrics'),
            "Valuation Metrics",
            "valuation_metrics",
            selected_ticker
        )

    with tabs[4]:
        _render_category_interactive(
            financials_data.get('growth_metrics'),
            "Growth Metrics",
            "growth_metrics",
            selected_ticker
        )


def _render_category_interactive(data: pd.DataFrame, title: str, table_key: str, selected_ticker: str):
    """
    Render a financial category with an interactive AgGrid table.

    Args:
        data: DataFrame containing the financial data
        title: Title to display for this category
        table_key: Unique key for this table
        selected_ticker: The currently selected stock ticker symbol
    """
    st.subheader(title)

    if data is None or data.empty:
        st.info(f"No {title.lower()} data available.")
        return

    # Display the data in an interactive AgGrid table
    _render_aggrid_table(data, table_key, selected_ticker)


def _render_aggrid_table(df: pd.DataFrame, table_key: str, selected_ticker: str):
    """
    Render an interactive AgGrid table with financial data.

    Args:
        df: DataFrame to display
        table_key: Unique key for this table
        selected_ticker: The currently selected stock ticker symbol
    """
    # Configure grid options
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # Make the first column (metric names) pinned and wider
    gb.configure_column(
        df.columns[0],
        pinned='left',
        width=250,
        headerName=df.columns[0]
    )
    
    # Configure other columns
    for col in df.columns[1:]:
        gb.configure_column(
            col,
            type=["numericColumn"],
            width=150,
            headerName=col
        )
    
    # General grid options
    gb.configure_grid_options(
        domLayout='normal',
        enableRangeSelection=True,
        enableCellTextSelection=True,
        ensureDomOrder=True
    )
    
    gb.configure_pagination(enabled=False)
    gb.configure_side_bar()
    
    grid_options = gb.build()

    # Render the grid with ticker-based key to ensure recreation on ticker change
    AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.NO_UPDATE,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=False,
        height=min(400, 35 * len(df) + 50),
        allow_unsafe_jscode=True,
        key=selected_ticker + "_" + table_key,
        theme='streamlit'
    )
