# finance/data_fetcher.py
import yfinance as yf
import requests

def fetch_stock_data(ticker: str):
    stock = yf.Ticker(ticker)
    history = stock.history(period="max")
    return history

def fetch_financial_statements(ticker: str):
    stock = yf.Ticker(ticker)
    balance_sheet = stock.balance_sheet
    income_stmt = stock.financials
    cash_flow = stock.cashflow
    info = stock.info
    return balance_sheet, income_stmt, cash_flow, info


def search_yahoo_finance(query: str, limit: int = 5):
    """
    Search Yahoo Finance for companies that match a given query string using the
    query2.finance.yahoo.com API endpoint. Returns a list of possible matches.
    Each item may contain keys like 'symbol', 'shortname', 'longname', etc.
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
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        # The "quotes" key in the JSON contains the suggestions
        quotes = data.get("quotes", [])
        return quotes
    except Exception as e:
        print(f"Error searching Yahoo Finance for '{query}': {e}")
        return []
