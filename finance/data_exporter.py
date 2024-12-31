# finance/data_exporter.py
import pandas as pd
from datetime import datetime

def export_to_excel(financial_data_dict, filename=None):
    """
    financial_data_dict is assumed to be a dict with keys like 'balance', 'income', 'cashflow'
    each is a DataFrame
    """
    if not filename:
        # Default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"financials_{timestamp}.xlsx"

    with pd.ExcelWriter(filename) as writer:
        for sheet_name, df in financial_data_dict.items():
            df.to_excel(writer, sheet_name=sheet_name)

    return filename
