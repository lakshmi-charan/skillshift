import hashlib

import numpy as np


def array_cache_key(arr):
    arr = np.asarray(arr)
    shape = "x".join(str(d) for d in arr.shape)
    return "%s|%s|%s" % (arr.dtype.str, shape, hashlib.sha256(arr.tostring()).hexdigest())
