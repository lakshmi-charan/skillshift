"""Numerical integration of sampled signals."""
import numpy as np


def area_under_curve(y, x=None, dx=1.0):
    """Trapezoidal integral of samples y over x (or uniform spacing dx when x is None)."""
    return float(np.trapezoid(y, x=x, dx=dx))


def mean_level(y, x):
    """Time-weighted mean of y over the sampled interval: integral / (x[-1] - x[0])."""
    x = np.asarray(x, dtype=float)
    return float(np.trapezoid(y, x) / (x[-1] - x[0]))


def cumulative_area(y, x):
    """Running trapezoidal integral, starting at 0.0, one value per sample."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    steps = np.diff(x) * (y[1:] + y[:-1]) / 2.0
    return [0.0] + [float(v) for v in np.cumsum(steps)]


def polygon_area(xs, ys):
    """Area enclosed by the closed polygon with vertices (xs[i], ys[i]) (shoelace formula)."""
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    return float(abs(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)) / 2.0)


def resample_signal(x, y, new_x):
    """Linear interpolation of the signal (x, y) at new_x."""
    return [float(v) for v in np.interp(new_x, x, y)]
