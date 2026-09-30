"""Small helpers for HTTP uploads: header parsing and file-type detection."""
import mimetypes
from email.message import Message


def _parse_header(header):
    msg = Message()
    msg["content-type"] = header
    params = msg.get_params(header="content-type") or [(header.strip(), "")]
    value = params[0][0]
    return value, {k.lower(): v for k, v in params[1:]}


def parse_content_type(header):
    """Split a Content-Type (or Content-Disposition) header into (lower-cased value, params dict)."""
    value, params = _parse_header(header)
    return value.lower(), params


def content_charset(header, default="utf-8"):
    """Charset named in a Content-Type header, lower-cased, or `default`."""
    _, params = _parse_header(header)
    return params.get("charset", default).lower()


def image_type(data):
    """Image format of the given bytes ('png', 'jpeg', 'gif', 'bmp', 'webp', ...) or None."""
    h = bytes(data[:32])
    if h.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if h[6:10] in (b"JFIF", b"Exif") or h.startswith(b"\xff\xd8\xff\xdb"):
        return "jpeg"
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if h.startswith(b"BM"):
        return "bmp"
    if h.startswith(b"RIFF") and h[8:12] == b"WEBP":
        return "webp"
    if h[:2] in (b"MM", b"II"):
        return "tiff"
    return None


def guess_mime(filename, default="application/octet-stream"):
    """MIME type for a file name based on its extension."""
    mime, _ = mimetypes.guess_type(filename)
    return mime or default
