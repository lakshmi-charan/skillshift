"""Percentile-based reporting (written against NumPy 1.x)."""
import numpy as np


def percentile_report(values, qs=(5, 25, 50, 75, 95)):
    """Dict mapping each percentile in qs to its value, using linear interpolation between order statistics."""
    a = np.asarray(values, dtype=float)
    vals = np.percentile(a, qs, interpolation="linear")
    return {q: float(v) for q, v in zip(qs, vals)}


def lower_median(values):
    """The median taken as an actual sample value: for an even count, the lower of the two middle values."""
    return float(np.quantile(np.asarray(values, dtype=float), 0.5, interpolation="lower"))


def iqr(values):
    """Inter-quartile range Q3 - Q1 (linear interpolation)."""
    q75, q25 = np.percentile(np.asarray(values, dtype=float), [75, 25])
    return float(q75 - q25)


def clip_to_percentiles(values, lo=1, hi=99):
    """Clip values to the [lo, hi] percentile range (linear interpolation); returns a list of floats."""
    a = np.asarray(values, dtype=float)
    lo_v, hi_v = np.percentile(a, [lo, hi])
    return [float(v) for v in np.clip(a, lo_v, hi_v)]
