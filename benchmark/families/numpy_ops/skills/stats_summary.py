"""Descriptive statistics for numeric samples (written against NumPy 1.x)."""
import numpy as np


def describe(values):
    """Dict with count, mean, std (population, ddof=0), min and max of the sample, as Python numbers."""
    a = np.asarray(values, dtype=np.float_)
    if a.size == 0:
        raise ValueError("empty sample")
    return {"count": int(a.size), "mean": float(a.mean()), "std": float(a.std()),
            "min": float(a.min()), "max": float(a.max())}


def geometric_mean(values):
    """Geometric mean of strictly positive values; ValueError for an empty sample or non-positive values."""
    a = np.asarray(values, dtype=np.float_)
    if a.size == 0 or not np.alltrue(a > 0):
        raise ValueError("geometric mean needs a non-empty sample of positive values")
    return float(np.product(a) ** (1.0 / a.size))


def cumulative_growth(rates):
    """Growth factors compounded period by period: rates [0.1, -0.5] -> [1.1, 0.55]."""
    return [float(v) for v in np.cumproduct(1.0 + np.asarray(rates, dtype=np.float_))]


def nan_mean(values):
    """Mean ignoring missing entries (None or NaN); NaN when there is no valid value."""
    a = np.array([np.NaN if v is None else v for v in values], dtype=np.float_)
    if a.size == 0 or np.isnan(a).all():
        return float(np.NaN)
    return float(np.nanmean(a))


def zscores(values):
    """Standard scores (x - mean) / std with population std; all zeros for a constant sample."""
    a = np.asarray(values, dtype=float)
    sd = a.std()
    if sd == 0:
        return [0.0] * a.size
    return [float(v) for v in (a - a.mean()) / sd]
