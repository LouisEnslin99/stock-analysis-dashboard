import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def show_valuation_tab():
    """
    Advanced valuation tab showing:
    - Valuation metrics with visual indicators
    - Peer comparison
    - Price targets and analyst ratings
    - Technical indicators
    - Risk metrics
    """
    if "selected_ticker" not in st.session_state or not st.session_state["selected_ticker"]:
        st.warning("No ticker selected. Please select one above.")
        return

    ticker = st.session_state["selected_ticker"]
    
    # Cache key
    cache_key = f"valuation_data_{ticker}"
    
    if cache_key in st.session_state:
        data = st.session_state[cache_key]
    else:
        with st.spinner(f"Loading valuation data for {ticker}..."):
            data = _fetch_valuation_data(ticker)
            st.session_state[cache_key] = data
    
    if not data:
        st.error("Unable to fetch valuation data. Please try again later.")
        return
    
    # Layout
    st.title(f"Valuation & Insights: {data['company_name']}")
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh"):
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()
    
    # Section 1: Key Valuation Metrics
    _render_valuation_metrics(data)
    
    st.markdown("---")
    
    # Section 2: Analyst Insights
    _render_analyst_insights(data)
    
    st.markdown("---")
    
    # Section 3: Price Performance & Technical
    _render_price_performance(data, ticker)
    
    st.markdown("---")
    
    # Section 4: Risk Metrics
    _render_risk_metrics(data)


def _fetch_valuation_data(ticker):
    """Fetch all valuation-related data"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get info
        info = stock.get_info()
        
        # Get historical data for technical analysis
        hist = stock.history(period="1y")
        
        # Get recommendations (may not always be available)
        try:
            recommendations = stock.recommendations
        except:
            recommendations = None
        
        data = {
            'ticker': ticker,
            'company_name': info.get('longName', ticker),
            'info': info,
            'history': hist,
            'recommendations': recommendations,
        }
        
        return data
    except Exception as e:
        print(f"Error fetching valuation data: {e}")
        return None


def _render_valuation_metrics(data):
    """Display valuation metrics with gauges and comparisons"""
    st.subheader("Valuation Metrics")
    
    info = data['info']
    
    # Key metrics
    metrics = {
        'P/E Ratio': info.get('trailingPE'),
        'Forward P/E': info.get('forwardPE'),
        'PEG Ratio': info.get('pegRatio'),
        'Price to Book': info.get('priceToBook'),
        'Price to Sales': info.get('priceToSalesTrailing12Months'),
        'EV/EBITDA': info.get('enterpriseToEbitda'),
    }
    
    # Display in columns
    cols = st.columns(3)
    for idx, (metric_name, value) in enumerate(metrics.items()):
        with cols[idx % 3]:
            if value and value > 0:
                # Determine if value is good/bad (simplified)
                color = _get_metric_color(metric_name, value)
                st.metric(
                    label=metric_name,
                    value=f"{value:.2f}",
                    delta=_get_metric_interpretation(metric_name, value)
                )
            else:
                st.metric(label=metric_name, value="N/A")
    
    # Valuation gauge chart
    pe_ratio = info.get('trailingPE')
    if pe_ratio and pe_ratio > 0:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pe_ratio,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "P/E Ratio"},
            delta={'reference': 20},  # Industry average benchmark
            gauge={
                'axis': {'range': [None, 50]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 15], 'color': "lightgreen"},
                    {'range': [15, 25], 'color': "yellow"},
                    {'range': [25, 50], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 30
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)


def _get_metric_color(metric_name, value):
    """Determine color based on metric value"""
    if 'P/E' in metric_name or 'Price to' in metric_name:
        if value < 15:
            return "green"
        elif value < 25:
            return "orange"
        else:
            return "red"
    return "blue"


def _get_metric_interpretation(metric_name, value):
    """Get simple interpretation"""
    if 'P/E' in metric_name:
        if value < 15:
            return "Undervalued"
        elif value < 25:
            return "Fair"
        else:
            return "Overvalued"
    return ""


def _render_analyst_insights(data):
    """Display analyst ratings and price targets"""
    st.subheader("Analyst Insights")
    
    info = data['info']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        target_high = info.get('targetHighPrice')
        if target_high:
            st.metric("Target High", f"${target_high:.2f}")
        else:
            st.metric("Target High", "N/A")
    
    with col2:
        target_mean = info.get('targetMeanPrice')
        current_price = info.get('currentPrice')
        if target_mean and current_price:
            upside = ((target_mean - current_price) / current_price) * 100
            st.metric("Target Mean", f"${target_mean:.2f}", f"{upside:+.1f}%")
        else:
            st.metric("Target Mean", "N/A")
    
    with col3:
        target_low = info.get('targetLowPrice')
        if target_low:
            st.metric("Target Low", f"${target_low:.2f}")
        else:
            st.metric("Target Low", "N/A")
    
    with col4:
        num_analysts = info.get('numberOfAnalystOpinions')
        if num_analysts:
            st.metric("Analysts", num_analysts)
        else:
            st.metric("Analysts", "N/A")
    
    # Recommendation trend
    recommendation = info.get('recommendationKey', 'N/A').upper()
    if recommendation != 'N/A':
        st.markdown(f"### Current Consensus: **{recommendation}**")
    
    # Recommendation chart - handle different DataFrame structures
    recommendations = data.get('recommendations')
    if recommendations is not None and not recommendations.empty:
        st.markdown("### Recent Analyst Actions")
        
        # Check available columns
        if 'To Grade' in recommendations.columns:
            # Get latest recommendations
            latest = recommendations.tail(30)
            rec_counts = latest.groupby('To Grade').size().reset_index(name='Count')
            
            fig = px.bar(
                rec_counts,
                x='To Grade',
                y='Count',
                title="Recent Analyst Recommendations (Last 30)",
                color='To Grade',
                color_discrete_map={
                    'Strong Buy': 'darkgreen',
                    'Buy': 'lightgreen',
                    'Hold': 'gray',
                    'Sell': 'orange',
                    'Strong Sell': 'red'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Display as table if structure is different
            st.dataframe(recommendations.tail(10), use_container_width=True)
    else:
        st.info("No recent analyst recommendations available.")


def _render_price_performance(data, ticker):
    """Display price performance and technical indicators"""
    st.subheader("Price Performance & Technical Analysis")
    
    hist = data['history']
    info = data['info']
    
    if hist is None or hist.empty:
        st.warning("No historical data available")
        return
    
    # Price metrics
    col1, col2, col3, col4 = st.columns(4)
    
    current_price = info.get('currentPrice') or (hist['Close'].iloc[-1] if not hist.empty else None)
    week_52_high = info.get('fiftyTwoWeekHigh')
    week_52_low = info.get('fiftyTwoWeekLow')
    
    with col1:
        if current_price:
            st.metric("Current Price", f"${current_price:.2f}")
    
    with col2:
        if week_52_high and current_price:
            distance = ((current_price - week_52_high) / week_52_high) * 100
            st.metric("52W High", f"${week_52_high:.2f}", f"{distance:.1f}%")
        else:
            st.metric("52W High", "N/A")
    
    with col3:
        if week_52_low and current_price:
            distance = ((current_price - week_52_low) / week_52_low) * 100
            st.metric("52W Low", f"${week_52_low:.2f}", f"{distance:+.1f}%")
        else:
            st.metric("52W Low", "N/A")
    
    with col4:
        avg_volume = info.get('averageVolume')
        if avg_volume:
            st.metric("Avg Volume", f"{avg_volume:,.0f}")
        else:
            st.metric("Avg Volume", "N/A")
    
    # Calculate moving averages
    hist['MA50'] = hist['Close'].rolling(window=50).mean()
    hist['MA200'] = hist['Close'].rolling(window=200).mean()
    
    # Create candlestick chart with moving averages
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist['Open'],
        high=hist['High'],
        low=hist['Low'],
        close=hist['Close'],
        name='Price'
    ))
    
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist['MA50'],
        name='MA50',
        line=dict(color='orange', width=1)
    ))
    
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist['MA200'],
        name='MA200',
        line=dict(color='blue', width=1)
    ))
    
    fig.update_layout(
        title=f"{ticker} Price Chart with Moving Averages",
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        height=500,
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Technical signal
    if not hist.empty and len(hist) > 200:
        last_close = hist['Close'].iloc[-1]
        last_ma50 = hist['MA50'].iloc[-1]
        last_ma200 = hist['MA200'].iloc[-1]
        
        if pd.notna(last_ma50) and pd.notna(last_ma200):
            if last_close > last_ma50 > last_ma200:
                st.success("**Technical Signal: BULLISH** - Price above both MA50 and MA200")
            elif last_close < last_ma50 < last_ma200:
                st.error("**Technical Signal: BEARISH** - Price below both MA50 and MA200")
            else:
                st.info("**Technical Signal: NEUTRAL** - Mixed signals")


def _render_risk_metrics(data):
    """Display risk and volatility metrics"""
    st.subheader("Risk & Volatility Metrics")
    
    info = data['info']
    hist = data['history']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        beta = info.get('beta')
        if beta:
            st.metric("Beta", f"{beta:.2f}", help="Volatility relative to market")
        else:
            st.metric("Beta", "N/A")
    
    with col2:
        # Calculate volatility from historical data
        if not hist.empty:
            returns = hist['Close'].pct_change()
            volatility = returns.std() * (252 ** 0.5) * 100  # Annualized
            st.metric("Volatility (Annual)", f"{volatility:.1f}%")
        else:
            st.metric("Volatility", "N/A")
    
    with col3:
        debt_to_equity = info.get('debtToEquity')
        if debt_to_equity:
            st.metric("Debt/Equity", f"{debt_to_equity:.2f}")
        else:
            st.metric("Debt/Equity", "N/A")
    
    with col4:
        current_ratio = info.get('currentRatio')
        if current_ratio:
            st.metric("Current Ratio", f"{current_ratio:.2f}")
        else:
            st.metric("Current Ratio", "N/A")
    
    # Risk assessment
    st.markdown("### Risk Assessment")
    
    risk_score = 0
    risk_factors = []
    
    if beta and beta > 1.5:
        risk_score += 1
        risk_factors.append("• High beta indicates higher volatility than market")
    
    if debt_to_equity and debt_to_equity > 2:
        risk_score += 1
        risk_factors.append("• High debt-to-equity ratio")
    
    if current_ratio and current_ratio < 1:
        risk_score += 1
        risk_factors.append("• Current ratio below 1 indicates liquidity concerns")
    
    if risk_score == 0:
        st.success("✅ **Low Risk** - Company shows stable financial metrics")
    elif risk_score == 1:
        st.warning("⚠️ **Moderate Risk** - Some concerns identified")
        for factor in risk_factors:
            st.write(factor)
    else:
        st.error("🚨 **High Risk** - Multiple risk factors identified")
        for factor in risk_factors:
            st.write(factor)