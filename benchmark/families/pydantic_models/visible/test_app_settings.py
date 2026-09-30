import os

from sa_testlib import case, need


@case("env_values")
def test_env(mod):
    os.environ["APP_DATABASE_URL"] = "sqlite://"
    os.environ["APP_PORT"] = "8081"
    try:
        s = need(mod, "load_settings")()
        assert s.port == 8081 and s.database_url == "sqlite://"
        assert mod.Settings.Config.env_prefix == "APP_"
    finally:
        del os.environ["APP_DATABASE_URL"], os.environ["APP_PORT"]


@case("defaults_and_overrides")
def test_defaults(mod):
    s = need(mod, "load_settings")(database_url="sqlite://")
    assert s.dict() == {"app_name": "orders-api", "debug": False, "port": 8000, "database_url": "sqlite://",
                        "allowed_hosts": ["localhost"]}
