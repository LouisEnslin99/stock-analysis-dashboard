import streamlit as st
import yfinance as yf
import plotly.express as px
import time

def show_overview_tab():
    if "selected_ticker" not in st.session_state or not st.session_state["selected_ticker"]:
        st.warning("No ticker selected in session_state. Please select one above.")
        return

    ticker = st.session_state["selected_ticker"]
    
    # Cache the data in session_state to avoid repeated API calls
    cache_key = f"overview_data_{ticker}"
    
    if cache_key in st.session_state:
        # Use cached data
        cached_data = st.session_state[cache_key]
        _render_overview(cached_data)
        return
    
    stock = yf.Ticker(ticker)
    
    # Try multiple methods to get data
    overview_data = {
        'ticker': ticker,
        'company_name': ticker,
        'sector': 'N/A',
        'industry': 'N/A',
        'description': 'No description available.',
        'current_price': None,
        'market_cap': None,
        'history': None,
    }
    
    # Method 1: Try get_info()
    try:
        info = stock.get_info()
        overview_data['company_name'] = info.get("longName") or ticker
        overview_data['sector'] = info.get("sector", "N/A")
        overview_data['industry'] = info.get("industry", "N/A")
        overview_data['description'] = info.get("longBusinessSummary", "No description available.")
        overview_data['current_price'] = info.get("currentPrice") or info.get("regularMarketPrice")
        overview_data['market_cap'] = info.get("marketCap")
    except Exception as e:
        st.warning(f"Limited data available due to API restrictions. Some information may be missing.")
        print(f"get_info() failed for {ticker}: {e}")
    
    # Method 2: Try to get historical data (this is more reliable)
    try:
        time.sleep(0.5)
        history = stock.history(period="1y")  # Start with 1 year instead of max
        if not history.empty:
            overview_data['history'] = history
            # Get current price from history if not available
            if overview_data['current_price'] is None:
                overview_data['current_price'] = history['Close'].iloc[-1]
    except Exception as e:
        print(f"History failed for {ticker}: {e}")
        st.warning("Unable to retrieve historical price data.")
    
    # Method 3: Try basic info from the ticker object
    if overview_data['company_name'] == ticker:
        try:
            # Some basic attributes that might be available
            if hasattr(stock, 'info') and isinstance(stock.info, dict):
                basic_info = stock.info
                overview_data['company_name'] = basic_info.get('longName', ticker)
        except:
            pass
    
    # Cache the data
    st.session_state[cache_key] = overview_data
    
    # Render the overview
    _render_overview(overview_data)


def _render_overview(data):
    """Render the overview tab with the provided data"""
    ticker = data['ticker']
    company_name = data['company_name']
    sector = data['sector']
    industry = data['industry']
    description = data['description']
    current_price = data['current_price']
    market_cap = data['market_cap']
    history = data['history']
    
    st.markdown("<div class='max-width-content'>", unsafe_allow_html=True)
    
    st.subheader(f"{company_name} ({ticker})")
    
    # Display price and market cap if available
    if current_price is not None:
        st.metric("Current Price", f"${current_price:.2f}")
    
    if market_cap is not None:
        st.write(f"**Market Cap:** ${market_cap:,.0f}")
    
    st.write(f"**Sector:** {sector}")
    st.write(f"**Industry:** {industry}")
    
    # Description in an expander
    with st.expander("Show Company Description"):
        st.write(description)
    
    # Show stock price chart if available
    if history is not None and not history.empty:
        try:
            fig = px.line(
                history,
                x=history.index,
                y="Close",
                title=f"{company_name} Stock Price History",
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning("Unable to display chart.")
            print(f"Chart error: {e}")
    else:
        st.info("Historical price data is temporarily unavailable. Please refresh in a moment.")
    
    # Add a button to clear cache and retry
    if st.button("🔄 Refresh Data"):
        cache_key = f"overview_data_{ticker}"
        if cache_key in st.session_state:
            del st.session_state[cache_key]
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)