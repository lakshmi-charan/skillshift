from email.message import Message


def describe_upload(content_type, data):
    msg = Message()
    msg["content-type"] = content_type
    params = msg.get_params(header="content-type") or [(content_type, "")]
    extra = {k.lower(): v for k, v in params[1:]}
    h = bytes(data[:16])
    image = None
    if h.startswith(b"\x89PNG\r\n\x1a\n"):
        image = "png"
    elif h[6:10] in (b"JFIF", b"Exif") or h.startswith(b"\xff\xd8\xff"):
        image = "jpeg"
    elif h[:6] in (b"GIF87a", b"GIF89a"):
        image = "gif"
    charset = extra.get("charset")
    return {"mime": params[0][0].strip().lower(), "charset": charset.lower() if charset else None, "image": image}
