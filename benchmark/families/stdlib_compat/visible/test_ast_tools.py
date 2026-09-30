from sa_testlib import case, need


@case("fold_constants")
def test_fold(mod):
    assert need(mod, "fold_constants")("TIMEOUT = 60 * 5") == "TIMEOUT = 300"


@case("number_literals")
def test_numbers(mod):
    assert need(mod, "number_literals")("x = 1 + 2") == [1, 2]


@case("names_used")
def test_names(mod):
    assert need(mod, "names_used")("print(a)") == ["a", "print"]
