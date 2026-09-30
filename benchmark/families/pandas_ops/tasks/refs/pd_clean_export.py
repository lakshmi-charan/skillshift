import io
import re

import pandas as pd


def clean_export(csv_text):
    df = pd.read_csv(io.StringIO(csv_text))
    df = df.rename(columns=lambda c: re.sub(r"[^0-9a-z]+", "_", str(c).strip().lower()).strip("_"))
    df = df.applymap(lambda v: v.strip() if isinstance(v, str) else v)
    return df.dropna(how="all").reset_index(drop=True)
