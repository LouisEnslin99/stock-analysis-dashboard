# finace/analysis/analysis_utils.py

import pandas as pd
import math

def safe_val(df, row_label, col_label):
    """
    Return float value from df.loc[row_label, col_label] or None if missing.
    """
    if df is None or df.empty:
        return None
    try:
        val = df.loc[row_label, col_label]
        return None if pd.isna(val) else float(val)
    except:
        return None

def format_cell(value, metric_name):
    """
    Format cell values into strings:
      - If it's currency (detect by "€" or "$" in the metric name), no decimals, add comma separation.
      - If it's a percentage (detect by '%' in metric_name or just do 2 decimals).
      - None => 'n/a'.
    """
    if value is None or math.isnan(value):
        return "n/a"
    # Check if metric_name has '€' or '$'
    if '€' in metric_name:
        return f"{int(value):,}€"  # round to integer
    elif '$' in metric_name:
        return f"{int(value):,}$"
    elif '%' in metric_name:
        return f"{value:.2f}%"
    else:
        return f"{value:.2f}"

def color_cell(display_str, color_code):
    """
    Return a CSS style for the background, plus keep white text or such if needed.
    """
    colors = {
        "green":  "background-color: #3CB371; color: #FFFFFF;",
        "yellow": "background-color: #D2B55B; color: #FFFFFF;",
        "red":    "background-color: #CD5C5C; color: #FFFFFF;",
        "gray":   "background-color: #696969; color: #FFFFFF;",
    }
    style = colors.get(color_code, "")
    return style
