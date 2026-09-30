def flag_readings(df, column, low, high):
    out = df.copy()
    out["status"] = "ok"
    out.loc[out[column] < low, "status"] = "low"
    out.loc[out[column] > high, "status"] = "high"
    return out
