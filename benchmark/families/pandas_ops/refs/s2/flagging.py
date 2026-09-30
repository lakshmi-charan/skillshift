"""Rule-based flagging and capping of numeric columns."""


def flag_above(df, column, threshold, flag_col="flag"):
    """Return a copy with a boolean `flag_col` that is True where df[column] > threshold."""
    out = df.copy()
    out[flag_col] = False
    out.loc[out[column] > threshold, flag_col] = True
    return out


def cap_values(df, column, cap):
    """Return a copy in which values of `column` above `cap` are replaced by `cap`."""
    out = df.copy()
    out.loc[out[column] > cap, column] = cap
    return out


def mark_missing(df, column, marker_col="missing"):
    """Return a copy with a boolean `marker_col` that is True where df[column] is missing."""
    out = df.copy()
    out[marker_col] = out[column].isna()
    return out


def flag_count(df, flag_col="flag"):
    """Number of rows whose flag is True."""
    return int(df[flag_col].sum())
