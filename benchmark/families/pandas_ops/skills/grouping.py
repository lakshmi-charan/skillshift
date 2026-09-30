"""Group-wise aggregation helpers (written against pandas 1.5)."""


def group_totals(df, key, value):
    """Dict mapping each group key to the sum of `value` in that group."""
    return {k: v for k, v in df.groupby(key)[value].sum().items()}


def group_means(df, key):
    """DataFrame of per-group means of the numeric columns, indexed by the group key."""
    return df.groupby(key).mean()


def top_n_per_group(df, key, value, n):
    """The n rows with the largest `value` in each group, largest first within the result order."""
    return df.sort_values(value, ascending=False).groupby(key).head(n).reset_index(drop=True)


def share_of_total(df, key, value):
    """Series (aligned to df) with each row's fraction of its group's total `value`."""
    return df[value] / df.groupby(key)[value].transform("sum")


def pivot_summary(df, index, columns, values):
    """Pivot table of sums with missing combinations filled with 0."""
    return df.pivot_table(index=index, columns=columns, values=values, aggfunc="sum", fill_value=0)
