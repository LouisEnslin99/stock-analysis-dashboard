import pandas as pd
from io import BytesIO
from datetime import datetime

def export_to_excel(financial_data_dict, stock_name):
    """
    Exports financial data to an Excel file and returns it as a downloadable object.
    
    :param financial_data_dict: Dictionary with keys like 'balance', 'income', 'cashflow' (each a DataFrame).
    :param stock_name: The name or ticker of the stock to include in the file name.
    :return: A tuple of the file name and BytesIO object representing the Excel file.
    """
    # Create a default filename with the stock name and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{stock_name}_financials_{timestamp}.xlsx"

    # Create an in-memory bytes buffer to hold the Excel file
    output = BytesIO()

    # Write the data to the Excel file
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for sheet_name, df in financial_data_dict.items():
            df.to_excel(writer, sheet_name=sheet_name)

    # Ensure the buffer is ready for reading
    output.seek(0)

    return filename, output
