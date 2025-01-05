# finace/analysis_formulas.py

"""
Contains helper functions for analysis metrics:
- 1-year growth
- 5-year CAGR
- margin calculations
- color classification
"""

import math

def compute_growth_1y(value_now, value_prev):
    """
    1-year growth % = ((value_now - value_prev) / |value_prev|) * 100
    If any is None or value_prev=0 => return None
    """
    if value_now is None or value_prev is None or value_prev == 0:
        return None
    return ((value_now - value_prev) / abs(value_prev)) * 100.0

def compute_cagr_3y(value_now, value_3yr):
    """
    5-year CAGR % = ((value_now / |value_5yr|)^(1/5) - 1) * 100
    If any is None or zero => return None
    """
    if value_now is None or value_3yr is None or value_3yr == 0:
        return None
    ratio = abs(value_now) / abs(value_3yr)
    cagr = (ratio ** (1.0 / 3.0) - 1.0) * 100.0
    return cagr

def compute_margin(value_numerator, value_denominator):
    """
    margin % = (value_numerator / |value_denominator|) * 100
    """
    if value_numerator is None or value_denominator is None or value_denominator == 0:
        return None
    return (value_numerator / abs(value_denominator)) * 100.0

def compute_interest_coverage(ebit, interest_expense):
    """
    interest coverage = EBIT / |InterestExpense|
    """
    if ebit is None or interest_expense is None or interest_expense == 0:
        return None
    return ebit / abs(interest_expense)

def classify_metric(value, thresholds: dict):
    """
    Return a color classification ('green', 'yellow', 'red') 
    based on 'thresholds' dict with keys: 'excellent', 'good', 
    and optional 'inverted'.

    Basic logic:
      if not inverted:
         if value >= excellent => 'green'
         elif value >= good => 'yellow'
         else => 'red'
      if inverted:
         if value <= excellent => 'green'
         elif value <= good => 'yellow'
         else => 'red'
    If value is None => 'gray' or 'NA'
    """
    if value is None:
        return "gray"

    inverted = thresholds.get("inverted", False)
    exc = thresholds["excellent"]
    gd = thresholds["good"]

    if not inverted:
        if value >= exc:
            return "green"
        elif value >= gd:
            return "yellow"
        else:
            return "red"
    else:
        # smaller = better
        if value <= exc:
            return "green"
        elif value <= gd:
            return "yellow"
        else:
            return "red"
