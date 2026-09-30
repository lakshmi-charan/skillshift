from sa_testlib import case, need


@case("optional_bio")
def test_minimal(mod):
    p = need(mod, "load_profile")({"user_id": 1, "display_name": "Ann", "zip_code": 12345})
    assert p.bio is None and p.zip_code == "12345"


@case("public_view")
def test_public(mod):
    p = need(mod, "load_profile")({"user_id": 1, "display_name": "Ann", "zip_code": "1"})
    assert need(mod, "public_view")(p) == {"display_name": "Ann", "zip_code": "1", "tags": []}


@case("apply_changes")
def test_changes(mod):
    p = need(mod, "load_profile")({"user_id": 1, "display_name": "Ann", "zip_code": "1"})
    assert need(mod, "apply_changes")(p, {"bio": "hi"}).bio == "hi"
