import ssl

from sa_testlib import case, need

INTERMEDIATE = ("ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:"
                "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:"
                "DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384")


def _ctx(minimum, ciphers):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = minimum
    ctx.set_ciphers(ciphers)
    return ctx


@case("intermediate_dhe")
def test_mozilla_intermediate(mod):
    assert need(mod, "matching_profile")(_ctx(ssl.TLSVersion.TLSv1_2, INTERMEDIATE)) == "intermediate"


@case("modern")
def test_tls13_only(mod):
    assert need(mod, "matching_profile")(_ctx(ssl.TLSVersion.TLSv1_3, INTERMEDIATE)) == "modern"


@case("old_profile")
def test_legacy(mod):
    assert need(mod, "matching_profile")(_ctx(ssl.TLSVersion.TLSv1, INTERMEDIATE + ":AES128-SHA")) == "old"


@case("reject_other")
def test_cbc_not_intermediate(mod):
    assert need(mod, "matching_profile")(_ctx(ssl.TLSVersion.TLSv1_2, INTERMEDIATE + ":AES128-SHA")) is None
