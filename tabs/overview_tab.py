# tabs/overview_tab.py
import streamlit as st
import yfinance as yf
import plotly.express as px

def show_overview_tab():
    if "selected_ticker" not in st.session_state or not st.session_state["selected_ticker"]:
        st.warning("No ticker selected in session_state. Please select one above.")
        return

    ticker = st.session_state["selected_ticker"]
    stock = yf.Ticker(ticker)
    info = stock.info

    company_name = info.get("longName") or ticker
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    description = info.get("longBusinessSummary", "No description available.")

    # Start a container with a narrower width for the content
    st.markdown("<div class='max-width-content'>", unsafe_allow_html=True)

    st.subheader(f"{company_name} ({ticker})")
    st.write(f"**Sector:** {sector}")
    st.write(f"**Industry:** {industry}")

    # Description in an expander
    with st.expander("Show Company Description"):
        st.write(description)

    # Show stock price chart in the same container
    history_data = stock.history(period="max")
    if not history_data.empty:
        fig = px.line(
            history_data,
            x=history_data.index,
            y="Close",
            title=f"{company_name} Stock Price History",
        )
        # If you want the chart narrower, set use_container_width=False and let the container handle it
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No historical data found for this ticker.")

    st.markdown("</div>", unsafe_allow_html=True)
