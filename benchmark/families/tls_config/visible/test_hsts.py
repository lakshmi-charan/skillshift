from sa_testlib import case, need


@case("max_age")
def test_two_years(mod):
    assert need(mod, "hsts_header")() == "max-age=63072000; includeSubDomains"


@case("directives")
def test_preload(mod):
    assert need(mod, "hsts_header")(True, True) == "max-age=63072000; includeSubDomains; preload"
