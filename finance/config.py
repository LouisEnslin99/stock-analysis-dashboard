# finance/config.py

###### General config #######
DEFAULT_TICKER = "AAPL"
GREEN_THRESHOLD = 1000000  # Example threshold for highlighting

###### Financials tab #######
# These lists must match the exact row labels you see in the DataFrame index.

### Balance Sheet ###
BALANCE_TOP_5 = [
    "Total Assets",
    "Total Liabilities Net Minority Interest",
    "Common Stock Equity",
    "Working Capital",
    "Cash Cash Equivalents And Short Term Investments"
]

BALANCE_NEXT_15 = [
    "Net Debt",
    "Total Debt",
    "Tangible Book Value",
    "Net Tangible Assets",
    "Current Liabilities",
    "Total Equity Gross Minority Interest",
    "Stockholders Equity",
    "Invested Capital",
    "Capital Lease Obligations",
    "Long Term Debt",
    "Accounts Payable",
    "Other Non Current Liabilities",
    "Inventory",
    "Accumulated Depreciation",
    "Net PPE"
]

### Cash Flow ###
CASHFLOW_TOP_5 = [
    "Free Cash Flow",
    "Operating Cash Flow",
    "Capital Expenditure",
    "Financing Cash Flow",
    "End Cash Position"
]

CASHFLOW_NEXT_15 = [
    "Repurchase Of Capital Stock",
    "Repayment Of Debt",
    "Issuance Of Debt",
    "Changes In Cash",
    "Investing Cash Flow",
    "Change In Working Capital",
    "Common Stock Dividend Paid",
    "Net Issuance Payments Of Debt",
    "Net Income From Continuing Operations",
    "Interest Paid Supplemental Data",         # Replaces "InterestPaidCFF"
    "Income Tax Paid Supplemental Data",       # Replaces "TaxesRefundPaid"
    "Net Other Investing Changes",
    "Net Investment Purchase And Sale",
    "Purchase Of Investment",                  # or "Sale Of Investment" if you prefer
    "Net Other Financing Charges"              # optional replacement for "EffectOfExchangeRateChanges"
]

### Income ###
INCOME_TOP_5 = [
    "Total Revenue",
    "Gross Profit",
    "Operating Income",
    "Net Income",
    "EBITDA"
]

INCOME_NEXT_15 = [
    "Cost Of Revenue",
    "Operating Expense",
    "Selling General And Administration",
    "Reconciled Depreciation",  # if you need Depreciation data in the Income statement
    "Pretax Income",
    "Tax Provision",
    "Normalized Income",
    "Diluted EPS",
    "Net Income From Continuing Operation Net Minority Interest",
    "EBIT",
    "Interest Expense",
    "Total Expenses",
    "Other Non Operating Income Expenses",      # e.g., if you need "Other Non Operating" line
    "Tax Effect Of Unusual Items",             # or remove if not needed
    "Net Income Including Noncontrolling Interests"  # or "Net Income Common Stockholders"
]
