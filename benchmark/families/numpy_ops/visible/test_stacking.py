import numpy as np

from sa_testlib import case, need


@case("stack_rows")
def test_stack(mod):
    assert need(mod, "stack_rows")([[1, 2], [3, 4]]).shape == (2, 2)


@case("pad_ragged")
def test_pad(mod):
    out = need(mod, "pad_ragged")([[1, 2], [3]])
    assert out.shape == (2, 2) and np.isnan(out[1, 1]) and out.dtype == np.float_


@case("add_bias_column")
def test_bias(mod):
    assert need(mod, "add_bias_column")([[5]]).tolist() == [[1.0, 5.0]]
