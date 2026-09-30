"""Convert JSON payloads from the reporting API to and from DataFrames."""
import io
import json

import pandas as pd


def records_to_frame(text):
    """Parse a JSON array of flat objects (a str) into a DataFrame, one row per object."""
    return pd.read_json(io.StringIO(text), orient="records")


def lines_to_frame(text):
    """Parse newline-delimited JSON (one object per line, a str) into a DataFrame."""
    return pd.read_json(io.StringIO(text), lines=True)


def frame_to_records(df):
    """Serialise a DataFrame to a JSON array of objects; missing values become null."""
    return df.to_json(orient="records")


def flatten_nested(text):
    """Parse a JSON array of possibly nested objects and flatten nested keys as 'outer.inner' columns."""
    return pd.json_normalize(json.loads(text), sep=".")
