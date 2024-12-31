# finance/data_processor.py
import pandas as pd

def process_financial_data(balance, income, cashflow):
    # Example transformation, pivoting, or cleaning
    # Return a dictionary of DataFrames, for example
    return {
        "balance": balance,
        "income": income,
        "cashflow": cashflow,
    }

def highlight_values(val, threshold):
    """
    Return a CSS style based on the threshold for use in e.g. DataFrame.style
    """
    color = "green" if val > threshold else "red"
    return f"color: {color}"
