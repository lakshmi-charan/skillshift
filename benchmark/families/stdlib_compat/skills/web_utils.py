"""Small helpers for HTTP uploads: header parsing and file-type detection."""
import cgi
import imghdr
import mimetypes


def parse_content_type(header):
    """Split a Content-Type (or Content-Disposition) header into (lower-cased value, params dict)."""
    value, params = cgi.parse_header(header)
    return value.lower(), params


def content_charset(header, default="utf-8"):
    """Charset named in a Content-Type header, lower-cased, or `default`."""
    _, params = cgi.parse_header(header)
    return params.get("charset", default).lower()


def image_type(data):
    """Image format of the given bytes ('png', 'jpeg', 'gif', 'bmp', 'webp', ...) or None."""
    return imghdr.what(None, h=data)


def guess_mime(filename, default="application/octet-stream"):
    """MIME type for a file name based on its extension."""
    mime, _ = mimetypes.guess_type(filename)
    return mime or default
