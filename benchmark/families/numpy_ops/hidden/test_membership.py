from sa_testlib import case, need


@case("keep_allowed")
def h_keep(mod):
    f = need(mod, "keep_allowed")
    assert f([5, 1, 7, 1, 3], [1, 3, 9]) == [1, 1, 3]
    assert f([5, 6], [1]) == [] and f([], [1, 2]) == []


@case("keep_allowed")
def h_keep_strings(mod):
    assert need(mod, "keep_allowed")(["b", "a", "c"], ["c", "b"]) == ["b", "c"]


@case("keep_allowed")
def h_keep_large(mod):
    vals = list(range(10000))
    out = need(mod, "keep_allowed")(vals, list(range(0, 10000, 7)))
    assert out == list(range(0, 10000, 7))


@case("drop_blocked")
def h_drop(mod):
    f = need(mod, "drop_blocked")
    assert f([5, 1, 7, 1, 3], [1, 3]) == [5, 7]
    assert f([5, 6], []) == [5, 6]


@case("drop_blocked")
def h_drop_all(mod):
    assert need(mod, "drop_blocked")(["x", "y"], ["x", "y", "z"]) == []


@case("any_flagged")
def h_any(mod):
    f = need(mod, "any_flagged")
    assert f([1, 2, 3], [3, 4]) is True
    assert f([1, 2, 3], [9]) is False
    assert f([], [1]) is False


@case("common_ids")
def h_common(mod):
    assert need(mod, "common_ids")([5, 3, 3, 1], [3, 5, 8]) == [3, 5]
    assert need(mod, "common_ids")([1], [2]) == []


@case("unique_counts")
def h_counts(mod):
    assert need(mod, "unique_counts")([3, 1, 3, 3, 2]) == {1: 1, 2: 1, 3: 3}
    assert need(mod, "unique_counts")(["a", "b", "a"]) == {"a": 2, "b": 1}
