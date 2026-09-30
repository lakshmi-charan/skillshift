"""Array (de)serialisation for caches and message queues (written against NumPy 1.x)."""
import hashlib
import io

import numpy as np


def to_bytes(arr):
    """Raw C-order bytes of the array's data (no header)."""
    return np.asarray(arr).tostring()


def from_bytes(buf, dtype="float64", shape=None):
    """Rebuild an array from raw bytes produced by to_bytes, optionally reshaped."""
    a = np.fromstring(buf, dtype=dtype)
    return a if shape is None else a.reshape(shape)


def digest(arr):
    """SHA-256 hex digest of the array's raw C-order bytes (used as a cache key)."""
    return hashlib.sha256(np.asarray(arr).tostring()).hexdigest()


def dump_npy(arr):
    """Serialise an array (dtype and shape included) to .npy-format bytes."""
    buf = io.BytesIO()
    np.save(buf, np.asarray(arr), allow_pickle=False)
    return buf.getvalue()


def load_npy(data):
    """Inverse of dump_npy."""
    return np.load(io.BytesIO(data), allow_pickle=False)
