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

    # print("\n--- Exploring yfinance.Ticker Methods for", ticker, "---")

    stock = yf.Ticker("AMZN")

    # print("Balance Sheet Labels:")
    # print(stock.balance_sheet.index)

    print("\nIncome Statement Labels:")
    print(stock.financials.index)

    # print("\nCash Flow Labels:")
    # print(stock.cashflow.index)

    print(stock.income_stmt.head(100))
    print(stock.income_stmt.columns[0])
    print(stock.income_stmt.columns[3])


# Run the function
if __name__ == "__main__":
    explore_ticker_methods()
