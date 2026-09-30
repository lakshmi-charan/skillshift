from sa_testlib import case, need


@case("parse_mapping")
def test_basic(mod):
    assert need(mod, "load_config_text")("db:\n  host: localhost\n  port: 5432\n") == {"db": {"host": "localhost", "port": 5432}}


@case("empty_document")
def test_empty(mod):
    assert need(mod, "load_config_text")("") == {}


@case("reject_non_mapping")
def test_list_rejected(mod):
    try:
        need(mod, "load_config_text")("- a\n- b\n")
    except ValueError:
        return
    raise AssertionError("expected ValueError")
