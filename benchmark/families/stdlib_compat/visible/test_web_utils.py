from sa_testlib import case, need


@case("content_type")
def test_ct(mod):
    assert need(mod, "parse_content_type")("text/html; charset=utf-8") == ("text/html", {"charset": "utf-8"})


@case("image_type")
def test_png(mod):
    assert need(mod, "image_type")(b"\x89PNG\r\n\x1a\n" + b"\x00" * 24) == "png"


@case("guess_mime")
def test_mime(mod):
    assert need(mod, "guess_mime")("a.json") == "application/json"
