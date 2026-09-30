import numpy as np


def latency_summary(samples_ms):
    a = np.array([np.NaN if v is None else v for v in samples_ms], dtype=np.float_)
    a = a[~np.isnan(a)]
    if a.size == 0:
        raise ValueError("no valid samples")
    p50, p90, p99 = np.percentile(a, [50, 90, 99], interpolation="nearest")
    return {"count": int(a.size), "mean": float(a.mean()), "p50": float(p50), "p90": float(p90), "p99": float(p99)}
