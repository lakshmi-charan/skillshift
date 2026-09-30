import io

import pandas as pd


def monthly_revenue(json_text):
    df = pd.read_json(io.StringIO(json_text), orient="records")
    s = df["amount"].astype(float)
    s.index = pd.to_datetime(df["date"])
    totals = s.sort_index().resample("ME").sum()
    return {ts.strftime("%Y-%m"): float(v) for ts, v in totals.items()}
