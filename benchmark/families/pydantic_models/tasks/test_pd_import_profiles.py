from sa_testlib import case, need


@case("functional")
def t_import(mod):
    rows = [
        {"user_id": 1, "display_name": "Ann  Lee", "zip_code": "02139"},
        {"user_id": "2", "display_name": "Bob", "bio": "hi", "zip_code": 94105},
        {"user_id": "x", "display_name": "Bad", "zip_code": "1"},
        {"display_name": "No Id", "zip_code": "1"},
        {"user_id": 5, "display_name": "   ", "zip_code": "1"},
        {"user_id": 6, "display_name": "No Zip"},
        {"user_id": 7, "display_name": " Cy ", "bio": None, "zip_code": 1001},
    ]
    assert need(mod, "import_profiles")(rows) == [
        {"user_id": 1, "display_name": "Ann Lee", "bio": None, "zip_code": "02139"},
        {"user_id": 2, "display_name": "Bob", "bio": "hi", "zip_code": "94105"},
        {"user_id": 7, "display_name": "Cy", "bio": None, "zip_code": "1001"},
    ]


@case("functional")
def t_empty(mod):
    assert need(mod, "import_profiles")([]) == []
