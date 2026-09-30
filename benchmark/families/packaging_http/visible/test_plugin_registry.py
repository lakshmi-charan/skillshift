from sa_testlib import case, need


@case("plugin_names")
def test_console_scripts(mod):
    assert "httpx" in need(mod, "plugin_names")("console_scripts")


@case("load_plugin")
def test_missing(mod):
    try:
        need(mod, "load_plugin")("console_scripts", "definitely-not-a-script")
    except LookupError:
        return
    raise AssertionError("expected LookupError")
