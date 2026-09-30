"""Calendar-period roll-ups of dated transactions."""
import pandas as pd


def _series(df, date_col, value_col):
    s = df[value_col].astype(float)
    s.index = pd.to_datetime(df[date_col])
    return s.sort_index()


def monthly_totals(df, date_col="date", value_col="amount"):
    """Sum per calendar month, indexed by month-end timestamp; months without rows are 0."""
    return _series(df, date_col, value_col).resample("ME").sum()


def quarterly_totals(df, date_col="date", value_col="amount"):
    """Sum per calendar quarter, indexed by quarter-end timestamp."""
    return _series(df, date_col, value_col).resample("QE").sum()


def yearly_totals(df, date_col="date", value_col="amount"):
    """Sum per calendar year, indexed by year-end timestamp."""
    return _series(df, date_col, value_col).resample("YE").sum()


def daily_average(df, date_col="date", value_col="amount"):
    """Mean value per calendar day for days that have rows (days without rows are dropped)."""
    return _series(df, date_col, value_col).resample("D").mean().dropna()


def month_label_totals(df, date_col="date", value_col="amount"):
    """Dict mapping 'YYYY-MM' labels to the month's total (only months that have rows)."""
    s = _series(df, date_col, value_col)
    g = s.groupby(s.index.to_period("M")).sum()
    return {str(p): float(v) for p, v in g.items()}
