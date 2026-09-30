from sa_testlib import case, need

PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 16
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01" + b"\x00" * 16
GIF = b"GIF89a\x01\x00\x01\x00\x80\x00\x00" + b"\x00" * 16
BMP = b"BM" + b"\x00" * 30
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 " + b"\x00" * 16


@case("content_type")
def h_ct_basic(mod):
    f = need(mod, "parse_content_type")
    assert f('text/html; charset="UTF-8"') == ("text/html", {"charset": "UTF-8"})
    assert f("Application/JSON") == ("application/json", {})


@case("content_type")
def h_ct_params(mod):
    f = need(mod, "parse_content_type")
    v, p = f("multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxk")
    assert v == "multipart/form-data" and p == {"boundary": "----WebKitFormBoundary7MA4YWxk"}
    v, p = f("text/plain; Charset=utf-8; format=flowed")
    assert v == "text/plain" and p == {"charset": "utf-8", "format": "flowed"}


@case("content_type")
def h_ct_disposition(mod):
    f = need(mod, "parse_content_type")
    assert f('attachment; filename="report 2022.pdf"') == ("attachment", {"filename": "report 2022.pdf"})
    assert f('form-data; name="file"; filename="a;b.txt"') == ("form-data", {"name": "file", "filename": "a;b.txt"})


@case("charset")
def h_charset(mod):
    f = need(mod, "content_charset")
    assert f("text/html; charset=ISO-8859-1") == "iso-8859-1"
    assert f('text/plain; charset="UTF-8"') == "utf-8"


@case("charset")
def h_charset_default(mod):
    f = need(mod, "content_charset")
    assert f("application/json") == "utf-8"
    assert f("text/csv", default="latin-1") == "latin-1"


@case("image_type")
def h_images(mod):
    f = need(mod, "image_type")
    assert f(PNG) == "png"
    assert f(JPEG) == "jpeg"
    assert f(GIF) == "gif"
    assert f(b"GIF87a" + b"\x00" * 20) == "gif"


@case("image_type")
def h_images_more(mod):
    f = need(mod, "image_type")
    assert f(BMP) == "bmp"
    assert f(WEBP) == "webp"


@case("image_type")
def h_not_image(mod):
    f = need(mod, "image_type")
    assert f(b"hello world, this is plain text") is None
    assert f(b"%PDF-1.7\n" + b"\x00" * 20) is None
    assert f(b"") is None


@case("guess_mime")
def h_mime(mod):
    f = need(mod, "guess_mime")
    assert f("photo.png") == "image/png"
    assert f("data.json") == "application/json"
    assert f("index.html") == "text/html"
    assert f("report.csv") == "text/csv"


@case("guess_mime")
def h_mime_default(mod):
    f = need(mod, "guess_mime")
    assert f("blob.zzqx") == "application/octet-stream"
    assert f("blob.zzqx", default="text/plain") == "text/plain"
