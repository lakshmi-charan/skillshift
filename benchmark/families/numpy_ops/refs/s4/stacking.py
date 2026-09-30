"""Assemble feature matrices from per-sample rows."""
import numpy as np


def stack_rows(rows):
    """Stack equal-length 1-D feature rows into a 2-D array, one row per sample."""
    return np.vstack(rows)


def pad_ragged(rows, fill=None):
    """Stack rows of different lengths into a 2-D float array, right-padding with fill (NaN by default)."""
    if fill is None:
        fill = np.nan
    width = max(len(r) for r in rows)
    out = np.full((len(rows), width), fill, dtype=np.float64)
    for i, r in enumerate(rows):
        out[i, :len(r)] = r
    return out


def add_bias_column(X):
    """Prepend a column of ones to a 2-D design matrix."""
    X = np.asarray(X, dtype=float)
    return np.column_stack([np.ones(X.shape[0]), X])


def standardize_columns(X):
    """Scale each column to mean 0 and population std 1; constant columns become 0."""
    X = np.asarray(X, dtype=float)
    sd = X.std(axis=0)
    sd[sd == 0] = 1.0
    return (X - X.mean(axis=0)) / sd


def row_norms(X):
    """Euclidean norm of every row."""
    return np.linalg.norm(np.asarray(X, dtype=float), axis=1)
