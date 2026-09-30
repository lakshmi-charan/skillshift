from sa_testlib import case, need


@case("fold_constants")
def h_fold_basic(mod):
    f = need(mod, "fold_constants")
    assert f("x = 2 * 3 + y") == "x = 6 + y"
    assert f("a = (1 + 2) * (10 - 4)") == "a = 18"
    assert f("f = 1.5 * 2") == "f = 3.0"


@case("fold_constants")
def h_fold_untouched(mod):
    f = need(mod, "fold_constants")
    assert f("s = 'a' + 'b'") == "s = 'a' + 'b'"
    assert f("z = x * 2") == "z = x * 2"
    assert f("d = 6 / 3") == "d = 6 / 3"


@case("fold_constants")
def h_fold_nested_in_call(mod):
    f = need(mod, "fold_constants")
    assert f("print(60 * 60 * 24, n - 1)") == "print(86400, n - 1)"


@case("number_literals")
def h_numbers(mod):
    f = need(mod, "number_literals")
    assert f("x = 1 + 2.5 * y\nz = f(3, 'a', True, None)") == [1, 2.5, 3]


@case("number_literals")
def h_numbers_complex(mod):
    f = need(mod, "number_literals")
    out = f("c = 2j\nd = [10, 20]\ne = 'no numbers here'")
    assert out == [2j, 10, 20]
    assert f("flag = False\nname = 'x'") == []


@case("string_literals")
def h_strings(mod):
    f = need(mod, "string_literals")
    assert f("a = 'x'\nb = b'raw'\nc = g(\"y\", 3)") == ["x", "y"]


@case("string_literals")
def h_strings_docstring(mod):
    f = need(mod, "string_literals")
    assert f("def h():\n    'doc'\n    return 'r'\n") == ["doc", "r"]
    assert f("n = 1 + 2") == []


@case("names_used")
def h_names(mod):
    f = need(mod, "names_used")
    assert f("y = x + z\nprint(y)") == ["print", "x", "y", "z"]
    assert f("a = 1") == []
