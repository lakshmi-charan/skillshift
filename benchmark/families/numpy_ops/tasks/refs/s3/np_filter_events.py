import numpy as np


def filter_events(ids, allowed, blocked):
    a = np.asarray(ids, dtype=np.int64)
    mask = np.isin(a, allowed) & np.isin(a, blocked, invert=True)
    return a[mask].tolist()
