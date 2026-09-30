"""Membership filtering of ID arrays (written against NumPy 1.x)."""
import numpy as np


def keep_allowed(values, allowed):
    """Elements of values that appear in allowed, in their original order (duplicates kept)."""
    a = np.asarray(values)
    return a[np.in1d(a, allowed)].tolist()


def drop_blocked(values, blocked):
    """Elements of values that do not appear in blocked, in their original order."""
    a = np.asarray(values)
    return a[np.in1d(a, blocked, invert=True)].tolist()


def any_flagged(values, flagged):
    """True if at least one element of values is in flagged."""
    return bool(np.sometrue(np.in1d(values, flagged)))


def common_ids(a, b):
    """Sorted unique IDs present in both a and b."""
    return np.intersect1d(a, b).tolist()


def unique_counts(values):
    """Dict mapping each distinct value to its number of occurrences."""
    u, c = np.unique(np.asarray(values), return_counts=True)
    return {k: int(n) for k, n in zip(u.tolist(), c.tolist())}
