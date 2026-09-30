import math

import numpy as np

from sa_testlib import case, need


@case("stack_rows")
def h_stack(mod):
    out = need(mod, "stack_rows")([[1, 2, 3], [4, 5, 6]])
    assert out.shape == (2, 3) and out.tolist() == [[1, 2, 3], [4, 5, 6]]


@case("stack_rows")
def h_stack_arrays(mod):
    rows = [np.array([0.5, 1.0]), np.array([2.0, 3.0]), np.array([4.0, 5.0])]
    out = need(mod, "stack_rows")(rows)
    assert out.shape == (3, 2) and out[2, 1] == 5.0


@case("stack_rows")
def h_stack_single(mod):
    assert need(mod, "stack_rows")([[7, 8]]).shape == (1, 2)


@case("pad_ragged")
def h_pad(mod):
    out = need(mod, "pad_ragged")([[1, 2, 3], [4], [5, 6]])
    assert out.shape == (3, 3) and out[0].tolist() == [1.0, 2.0, 3.0]
    assert out[1, 0] == 4.0 and math.isnan(out[1, 1]) and math.isnan(out[2, 2])


@case("pad_ragged")
def h_pad_fill(mod):
    out = need(mod, "pad_ragged")([[1], [2, 3]], fill=0.0)
    assert out.tolist() == [[1.0, 0.0], [2.0, 3.0]]


@case("add_bias_column")
def h_bias(mod):
    out = need(mod, "add_bias_column")([[2, 3], [4, 5]])
    assert out.tolist() == [[1.0, 2.0, 3.0], [1.0, 4.0, 5.0]]


@case("standardize_columns")
def h_std(mod):
    out = need(mod, "standardize_columns")([[1, 5], [3, 5]])
    assert out.tolist() == [[-1.0, 0.0], [1.0, 0.0]]


@case("row_norms")
def h_norms(mod):
    assert need(mod, "row_norms")([[3, 4], [0, 0], [1, 0]]).tolist() == [5.0, 0.0, 1.0]
