from sa_testlib import case, need


@case("installed_version")
def test_httpx_version(mod):
    import httpx
    assert need(mod, "installed_version")("httpx") == httpx.__version__


@case("missing_distribution")
def test_missing(mod):
    assert need(mod, "installed_version")("no-such-dist-xyz") is None
