# tabs/overview_tab.py

import streamlit as st
import plotly.express as px
import yfinance as yf

from finance.data_fetcher import search_yahoo_finance

def show_overview_tab():
    """
    If st.session_state["selected_ticker"] is None, show only the search bar.
    Otherwise, display the overview info for the chosen ticker.
    """

    # Safeguard: if "selected_ticker" doesn't exist yet, initialize it
    if "selected_ticker" not in st.session_state:
        st.session_state["selected_ticker"] = None

    # If no ticker chosen yet, show the search input and suggestions
    if st.session_state["selected_ticker"] is None:
        company_query = st.text_input("Type a company name or ticker:", value="")

        if company_query:
            suggestions = search_yahoo_finance(company_query, limit=5)
            if suggestions:
                suggestion_labels = [
                    f"{item.get('symbol','')} — {item.get('shortname') or item.get('longname','')}"
                    for item in suggestions
                ]
                selected_index = st.selectbox(
                    "Select the correct company:",
                    options=range(len(suggestion_labels)),
                    format_func=lambda idx: suggestion_labels[idx],
                )
                chosen_symbol = suggestions[selected_index].get("symbol")
                
                # If user picks a symbol, set it in session_state
                if chosen_symbol:
                    st.session_state["selected_ticker"] = chosen_symbol

        # Nothing else displayed until we have a selected ticker
        return

    # If we DO have a ticker in session state, show the full overview
    ticker = st.session_state["selected_ticker"]
    stock = yf.Ticker(ticker)
    info = stock.info

    company_name = info.get("longName") or ticker
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    description = info.get("longBusinessSummary", "No description available.")

    st.subheader(f"Overview: {company_name} ({ticker})")
    st.write(f"**Sector:** {sector}")
    st.write(f"**Industry:** {industry}")

    # Use an expander for the description
    with st.expander("Show Company Description"):
        st.write(description)

    # Show price history
    history_data = stock.history(period="max")
    if not history_data.empty:
        fig = px.line(
            history_data,
            x=history_data.index,
            y="Close",
            title=f"{company_name} Stock Price History",
        )
        st.plotly_chart(fig)
    else:
        st.warning("No historical data found for this ticker.")
