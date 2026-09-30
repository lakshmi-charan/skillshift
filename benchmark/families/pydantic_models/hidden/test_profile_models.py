import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _util import raises_value_error  # noqa: E402
from sa_testlib import case, need  # noqa: E402

FULL = {"user_id": 7, "display_name": "Ann Lee", "bio": None, "zip_code": "02139"}


def _with(**kw):
    d = dict(FULL)
    d.update(kw)
    return d


@case("required_fields")
def h_required(mod):
    f = need(mod, "load_profile")
    for key in ("user_id", "display_name", "zip_code"):
        d = dict(FULL)
        del d[key]
        assert raises_value_error(f, d), key
    assert raises_value_error(f, _with(user_id="seven"))


@case("required_fields")
def h_display_name(mod):
    f = need(mod, "load_profile")
    p = f(_with(display_name="  Ann \t  Lee ", user_id="7"))
    assert p.display_name == "Ann Lee" and p.user_id == 7
    assert raises_value_error(f, _with(display_name="   "))


@case("optional_bio")
def h_bio_omitted(mod):
    f = need(mod, "load_profile")
    d = dict(FULL)
    del d["bio"]
    p = f(d)
    assert p.bio is None and p.website is None


@case("optional_bio")
def h_bio_given(mod):
    f = need(mod, "load_profile")
    assert f(_with(bio="Hello")).bio == "Hello"
    d = {"user_id": 1, "display_name": "B", "zip_code": "1", "website": "https://b.example"}
    p = f(d)
    assert p.bio is None and p.website == "https://b.example"


@case("zip_as_string")
def h_zip_int(mod):
    f = need(mod, "load_profile")
    p = f(_with(zip_code=94105))
    assert p.zip_code == "94105" and isinstance(p.zip_code, str)


@case("zip_as_string")
def h_zip_str(mod):
    f = need(mod, "load_profile")
    assert f(_with(zip_code="02139")).zip_code == "02139"
    assert f(_with(zip_code=10001)).zip_code == "10001"


@case("public_view")
def h_public(mod):
    p = need(mod, "load_profile")(_with(tags=["a", "b"]))
    out = need(mod, "public_view")(p)
    assert out == {"display_name": "Ann Lee", "zip_code": "02139", "tags": ["a", "b"]}, out


@case("public_view")
def h_public_with_values(mod):
    p = need(mod, "load_profile")(_with(bio="Hi", website="https://ann.example"))
    out = need(mod, "public_view")(p)
    assert out == {"display_name": "Ann Lee", "bio": "Hi", "website": "https://ann.example",
                   "zip_code": "02139", "tags": []}, out
    assert "user_id" not in out


@case("apply_changes")
def h_changes(mod):
    p = need(mod, "load_profile")(FULL)
    q = need(mod, "apply_changes")(p, {"display_name": "Ann L.", "tags": ["x"]})
    assert q.display_name == "Ann L." and q.tags == ["x"] and q.user_id == 7
    assert p.display_name == "Ann Lee" and p.tags == [], "original must be unchanged"
    assert q is not p


@case("apply_changes")
def h_changes_empty(mod):
    p = need(mod, "load_profile")(_with(bio="b"))
    q = need(mod, "apply_changes")(p, {})
    assert q is not p and (q.user_id, q.display_name, q.bio, q.zip_code) == (7, "Ann Lee", "b", "02139")
