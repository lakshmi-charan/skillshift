"""Tidy-up helpers for tabular data loaded from spreadsheets and CSV exports."""
import re

import pandas as pd


def strip_whitespace(df):
    """Return a copy with leading/trailing whitespace removed from every string cell."""
    return df.map(lambda v: v.strip() if isinstance(v, str) else v)


def text_columns(df):
    """Names of the columns that hold text, in column order."""
    return [c for c in df.columns if df[c].dtype == object or isinstance(df[c].dtype, pd.StringDtype)]


def null_counts(df):
    """Dict mapping each column name to its number of missing values."""
    return {name: int(col.isna().sum()) for name, col in df.items()}


def drop_empty_rows(df):
    """Drop rows where every value is missing and renumber the index from 0."""
    return df.dropna(how="all").reset_index(drop=True)


def normalise_headers(df):
    """Lower-case column names, trim them and replace runs of non-alphanumerics with '_'."""
    return df.rename(columns=lambda c: re.sub(r"[^0-9a-z]+", "_", str(c).strip().lower()).strip("_"))
