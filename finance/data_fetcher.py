# finance/data_fetcher.py
import yfinance as yf
import requests
import time
from functools import wraps

def rate_limit(delay=0.5):
    """Decorator to add delay between API calls to avoid rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator


@rate_limit(delay=0.5)
def fetch_stock_data(ticker: str):
    """Fetch historical stock price data"""
    stock = yf.Ticker(ticker)
    history = stock.history(period="max")
    return history


@rate_limit(delay=0.5)
def fetch_financial_statements(ticker: str):
    """
    Fetch financial statements for a given ticker.
    Returns: balance_sheet, income_stmt, cash_flow, info
    
    Note: Uses get_info() method instead of info property to avoid rate limiting.
    """
    stock = yf.Ticker(ticker)
    balance_sheet = stock.balance_sheet
    income_stmt = stock.financials
    cash_flow = stock.cashflow
    
    # Use get_info() method instead of info property
    try:
        info = stock.get_info()
    except Exception as e:
        print(f"Warning: Could not fetch detailed info for {ticker}: {e}")
        # Fallback to fast_info if available
        try:
            fast = stock.fast_info
            info = {
                'symbol': ticker,
                'currentPrice': getattr(fast, 'last_price', None),
                'marketCap': getattr(fast, 'market_cap', None),
            }
        except:
            info = {'symbol': ticker}
    
    return balance_sheet, income_stmt, cash_flow, info


def search_yahoo_finance(query: str, limit: int = 5):
    """
    Search Yahoo Finance for companies that match a given query string using the
    query2.finance.yahoo.com API endpoint. Returns a list of possible matches.
    Each item may contain keys like 'symbol', 'shortname', 'longname', etc.
    
    Note: This function may be rate-limited. Consider implementing caching if needed.
    """
    if not query.strip():
        return []
    
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {
        "q": query,
        "lang": "en-US",
        "region": "US",
        "quotesCount": limit,
        "newsCount": 0,
        # Additional parameters that might help:
        "enableFuzzyQuery": False,
        "quotesQueryId": "tss_match_phrase",
        "multiQuoteQueryId": "multi_quote_single_token",
        "enableCb": False,
        "enableNavLinks": False,
        "enableEnhancedTrivialQuery": False,
    }
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/88.0.4324.96 Safari/537.36"
        )
    }

    try:
        # Add a small delay to avoid rate limiting
        time.sleep(0.3)
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        # The "quotes" key in the JSON contains the suggestions
        quotes = data.get("quotes", [])
        return quotes
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"Rate limited when searching for '{query}'. Please wait a moment.")
        else:
            print(f"HTTP error searching Yahoo Finance for '{query}': {e}")
        return []
    except Exception as e:
        print(f"Error searching Yahoo Finance for '{query}': {e}")
        return []


def get_stock_info_safe(ticker: str):
    """
    Safely fetch stock info with fallback to fast_info.
    Returns a dictionary with available info.
    """
    stock = yf.Ticker(ticker)
    
    try:
        # Try get_info() first (method, not property)
        info = stock.get_info()
        return info
    except Exception as e:
        print(f"Could not fetch full info for {ticker}: {e}")
        
        # Fallback to fast_info
        try:
            fast = stock.fast_info
            return {
                'symbol': ticker,
                'currentPrice': getattr(fast, 'last_price', None),
                'marketCap': getattr(fast, 'market_cap', None),
                'currency': getattr(fast, 'currency', 'USD'),
            }
        except Exception as e2:
            print(f"Could not fetch fast_info for {ticker}: {e2}")
            return {'symbol': ticker}