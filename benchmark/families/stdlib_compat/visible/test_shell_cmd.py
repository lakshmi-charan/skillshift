from sa_testlib import case, need


@case("quote_arg")
def test_quote_space(mod):
    assert need(mod, "quote_arg")("hello world") == "'hello world'"


@case("join_command")
def test_join(mod):
    assert need(mod, "join_command")(["echo", "a b"]) == "echo 'a b'"


@case("split_command")
def test_split(mod):
    assert need(mod, "split_command")("echo 'a b'") == ["echo", "a b"]
