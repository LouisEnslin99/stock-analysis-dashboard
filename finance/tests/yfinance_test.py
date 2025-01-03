import yfinance as yf
import pandas as pd

# Helper function to calculate historical P/E (Price/Earnings) ratio
def calculate_historical_pe(historical_prices, earnings):
    """
    Calculate historical P/E ratio using historical prices and earnings.
    """
    if historical_prices.empty or earnings.empty:
        return pd.DataFrame()
    
    pe_data = pd.DataFrame()
    pe_data['Price'] = historical_prices['Close']
    pe_data['Earnings'] = earnings.get('Earnings', pd.Series(index=historical_prices.index))
    pe_data['P/E'] = pe_data['Price'] / pe_data['Earnings']
    return pe_data

# Main function to explore all possible methods of yfinance.Ticker
def explore_ticker_methods():
    ticker = "BYw6.DE"
    stock = yf.Ticker(ticker)

    print("\n--- Exploring yfinance.Ticker Methods for", ticker, "---")

    stock = yf.Ticker("AAPL")

    print("Balance Sheet Labels:")
    print(stock.get_balance_sheet().index)

    print("\nIncome Statement Labels:")
    print(stock.get_financials().index)

    print("\nCash Flow Labels:")
    print(stock.get_cashflow().index)



    history_metadata = stock.get_history_metadata()

    # 1. get_actions
    print("\n--- Actions (Dividends and Splits) ---")
    try:
        actions = stock.actions
        print(actions.head())
    except Exception as e:
        print("Error fetching actions:", e)

    # 2. get_analyst_price_targets
    print("\n--- Analyst Price Targets ---")
    try:
        analyst_price_targets = stock.get_analyst_price_targets()
        print(analyst_price_targets.head())
    except Exception as e:
        print("Error fetching analyst price targets:", e)

    # 3. get_balance_sheet
    print("\n--- Balance Sheet ---")
    try:
        balance_sheet = stock.balance_sheet
        print(balance_sheet.head())
    except Exception as e:
        print("Error fetching balance sheet:", e)

    # 4. get_calendar
    print("\n--- Calendar ---")
    try:
        calendar = stock.calendar
        print(calendar)
    except Exception as e:
        print("Error fetching calendar:", e)

    # 5. get_cashflow
    print("\n--- Cash Flow ---")
    try:
        cashflow = stock.cashflow
        print(cashflow.head())
    except Exception as e:
        print("Error fetching cash flow:", e)

    # 6. get_dividends
    print("\n--- Dividends ---")
    try:
        dividends = stock.dividends
        print(dividends.head())
    except Exception as e:
        print("Error fetching dividends:", e)

    # 7. get_earnings
    print("\n--- Earnings ---")
    try:
        earnings = stock.earnings
        print(earnings.head())
    except Exception as e:
        print("Error fetching earnings:", e)

    # 8. get_earnings_dates
    print("\n--- Earnings Dates ---")
    try:
        earnings_dates = stock.earnings_dates
        print(earnings_dates.head())
    except Exception as e:
        print("Error fetching earnings dates:", e)

    # 10. get_eps_trend
    print("\n--- EPS Trend ---")
    try:
        eps_trend = stock.get_eps_trend()
        print(eps_trend.head())
    except Exception as e:
        print("Error fetching EPS trend:", e)

    # 11. get_eps_revisions
    print("\n--- EPS Revisions ---")
    try:
        eps_revisions = stock.get_eps_revisions()
        print(eps_revisions.head())
    except Exception as e:
        print("Error fetching EPS revisions:", e)

    # 12. get_financials
    print("\n--- Financials ---")
    try:
        financials = stock.financials
        print(financials.head())
    except Exception as e:
        print("Error fetching financials:", e)

    # 13. get_info
    print("\n--- Fundamentals ---")
    try:
        fundamentals = stock.info
        print(fundamentals)
    except Exception as e:
        print("Error fetching fundamentals:", e)

    # 14. get_institutional_holders
    print("\n--- Institutional Holders ---")
    try:
        institutional_holders = stock.institutional_holders
        print(institutional_holders.head())
    except Exception as e:
        print("Error fetching institutional holders:", e)

    # 15. get_major_holders
    print("\n--- Major Holders ---")
    try:
        major_holders = stock.major_holders
        print(major_holders)
    except Exception as e:
        print("Error fetching major holders:", e)

    # 16. get_mutualfund_holders
    print("\n--- Mutual Fund Holders ---")
    try:
        mutualfund_holders = stock.mutualfund_holders
        print(mutualfund_holders.head())
    except Exception as e:
        print("Error fetching mutual fund holders:", e)

    # 17. get_history_metadata
    print("\n--- History Metadata ---")
    try:
        history_metadata = stock.history_metadata
        print(history_metadata)
    except Exception as e:
        print("Error fetching history metadata:", e)

    # 18. get_income_stmt
    print("\n--- Income Statement ---")
    try:
        income_stmt = stock.financials
        print(income_stmt.head())
    except Exception as e:
        print("Error fetching income statement:", e)

    # 19. get_recommendations
    print("\n--- Recommendations ---")
    try:
        recommendations = stock.recommendations
        print(recommendations.head())
    except Exception as e:
        print("Error fetching recommendations:", e)

# Run the function
if __name__ == "__main__":
    explore_ticker_methods()
