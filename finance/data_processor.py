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

def format_dataframe(df):
    """
    Formats a DataFrame for display, ensuring proper formatting for dates, monetary values,
    and handling missing values.

    :param df: The DataFrame to format.
    :return: A formatted DataFrame.
    """
    # Replace missing values with "N/A"
    df = df.fillna("N/A")

    # Format monetary values
    def format_money(value):
        if isinstance(value, (int, float)):
            return f"${value:,.2f}"  # Format as $1,000,000.00
        return value  # Leave non-numeric values unchanged

    formatted_df = df.applymap(format_money)

    # Convert column headers to YYYY-MM if they are datetime-like
    def format_column_name(col):
        try:
            # Attempt to parse and reformat as YYYY-MM
            return pd.to_datetime(col).strftime("%Y-%m")
        except (ValueError, TypeError):
            # Return the column as-is if not a valid date
            return col

    formatted_df.columns = [format_column_name(col) for col in formatted_df.columns]

    return formatted_df