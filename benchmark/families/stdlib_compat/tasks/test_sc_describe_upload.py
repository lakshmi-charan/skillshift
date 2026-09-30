from sa_testlib import case, need

PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 16
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01" + b"\x00" * 16
GIF = b"GIF89a\x01\x00\x01\x00\x80\x00\x00" + b"\x00" * 16


@case("functional")
def t_image(mod):
    f = need(mod, "describe_upload")
    assert f("image/png", PNG) == {"mime": "image/png", "charset": None, "image": "png"}
    assert f("Image/JPEG", JPEG) == {"mime": "image/jpeg", "charset": None, "image": "jpeg"}
    assert f("application/octet-stream", GIF)["image"] == "gif"


@case("functional")
def t_text(mod):
    f = need(mod, "describe_upload")
    assert f('text/plain; charset="UTF-8"', b"hello") == {"mime": "text/plain", "charset": "utf-8", "image": None}
    assert f("application/json;charset=ISO-8859-1", b"{}") == {"mime": "application/json", "charset": "iso-8859-1", "image": None}
