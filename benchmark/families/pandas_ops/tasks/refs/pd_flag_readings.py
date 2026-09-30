def flag_readings(df, column, low, high):
    out = df.copy()
    out["status"] = "ok"
    out["status"][out[column] < low] = "low"
    out["status"][out[column] > high] = "high"
    return out
