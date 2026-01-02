import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(page_title="Stock Analysis Dashboard", layout="wide")

# Initialize session state
if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "AAPL"

# Title
st.title("📈 Stock Analysis Dashboard")

# Sidebar for stock selection
st.sidebar.header("Stock Selection")

# Popular stocks
popular_stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "Meta": "META",
    "NVIDIA": "NVDA",
    "Netflix": "NFLX"
}

# Stock selection
selected_stock = st.sidebar.selectbox(
    "Choose a stock:",
    options=list(popular_stocks.keys()),
    index=list(popular_stocks.values()).index(st.session_state["selected_ticker"])
)

# Custom ticker input
custom_ticker = st.sidebar.text_input("Or enter a custom ticker:")

# Time period selection
time_period = st.sidebar.selectbox(
    "Time Period:",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    index=3
)

# Determine which ticker to use
if custom_ticker:
    ticker = custom_ticker.upper()
else:
    ticker = popular_stocks[selected_stock]

# Update session state if ticker changed
if ticker != st.session_state["selected_ticker"]:
    st.session_state["selected_ticker"] = ticker

# Function to fetch stock data
@st.cache_data(ttl=3600)
def get_stock_data(ticker_symbol, period):
    try:
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period=period)
        return df, stock
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None

# Function to calculate technical indicators
def calculate_indicators(df):
    # Simple Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df

# Fetch data
with st.spinner(f"Loading data for {ticker}..."):
    df, stock_info = get_stock_data(ticker, time_period)

if df is not None and not df.empty:
    # Calculate indicators
    df = calculate_indicators(df)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    change = current_price - prev_price
    change_pct = (change / prev_price) * 100
    
    with col1:
        st.metric("Current Price", f"${current_price:.2f}", f"{change:.2f} ({change_pct:.2f}%)")
    
    with col2:
        st.metric("High", f"${df['High'].iloc[-1]:.2f}")
    
    with col3:
        st.metric("Low", f"${df['Low'].iloc[-1]:.2f}")
    
    with col4:
        st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
    
    # Price chart
    st.subheader("Price Chart")
    
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))
    
    # Add moving averages
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(color='blue')))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        height=500,
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Volume chart
    st.subheader("Volume")
    
    fig_volume = go.Figure()
    colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' for i in range(len(df))]
    
    fig_volume.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        marker_color=colors,
        name='Volume'
    ))
    
    fig_volume.update_layout(
        xaxis_title="Date",
        yaxis_title="Volume",
        height=300
    )
    
    st.plotly_chart(fig_volume, use_container_width=True)
    
    # RSI Chart
    st.subheader("Relative Strength Index (RSI)")
    
    fig_rsi = go.Figure()
    
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
    
    fig_rsi.update_layout(
        xaxis_title="Date",
        yaxis_title="RSI",
        height=300,
        yaxis_range=[0, 100]
    )
    
    st.plotly_chart(fig_rsi, use_container_width=True)
    
    # Statistics
    st.subheader("Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Price Statistics**")
        stats_df = pd.DataFrame({
            'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max'],
            'Value': [
                f"${df['Close'].mean():.2f}",
                f"${df['Close'].median():.2f}",
                f"${df['Close'].std():.2f}",
                f"${df['Close'].min():.2f}",
                f"${df['Close'].max():.2f}"
            ]
        })
        st.dataframe(stats_df, hide_index=True)
    
    with col2:
        st.write("**Current Indicators**")
        indicators_df = pd.DataFrame({
            'Indicator': ['SMA 20', 'SMA 50', 'RSI'],
            'Value': [
                f"${df['SMA_20'].iloc[-1]:.2f}" if not pd.isna(df['SMA_20'].iloc[-1]) else "N/A",
                f"${df['SMA_50'].iloc[-1]:.2f}" if not pd.isna(df['SMA_50'].iloc[-1]) else "N/A",
                f"{df['RSI'].iloc[-1]:.2f}" if not pd.isna(df['RSI'].iloc[-1]) else "N/A"
            ]
        })
        st.dataframe(indicators_df, hide_index=True)
    
    # Raw data
    with st.expander("View Raw Data"):
        st.dataframe(df)

else:
    st.error("Unable to fetch stock data. Please check the ticker symbol and try again.")