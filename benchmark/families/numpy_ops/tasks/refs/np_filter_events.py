import numpy as np


def filter_events(ids, allowed, blocked):
    a = np.asarray(ids, dtype=np.int64)
    mask = np.in1d(a, allowed) & np.in1d(a, blocked, invert=True)
    return a[mask].tolist()
