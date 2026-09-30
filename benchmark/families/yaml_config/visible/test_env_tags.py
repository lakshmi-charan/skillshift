from sa_testlib import case, need


@case("env_substitution")
def test_env(mod):
    assert need(mod, "load_with_env")("user: !env DB_USER\n", {"DB_USER": "app"}) == {"user": "app"}


@case("plain_values")
def test_plain(mod):
    assert need(mod, "load_with_env")("port: 5432\n", {}) == {"port": 5432}
