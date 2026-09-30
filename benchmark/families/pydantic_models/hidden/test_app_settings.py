import contextlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _util import raises_value_error  # noqa: E402
from sa_testlib import case, need  # noqa: E402


@contextlib.contextmanager
def env(**values):
    saved = {k: v for k, v in os.environ.items() if k.upper().startswith("APP_")}
    for k in saved:
        del os.environ[k]
    os.environ.update(values)
    try:
        yield
    finally:
        for k in [k for k in os.environ if k.upper().startswith("APP_")]:
            del os.environ[k]
        os.environ.update(saved)


@case("env_values")
def h_env(mod):
    with env(APP_DATABASE_URL="sqlite:///prod.db", APP_PORT="9000", APP_DEBUG="true", APP_APP_NAME="billing"):
        s = need(mod, "load_settings")()
    assert (s.database_url, s.port, s.debug, s.app_name) == ("sqlite:///prod.db", 9000, True, "billing")


@case("env_values")
def h_env_list_and_bool(mod):
    with env(APP_DATABASE_URL="x", APP_ALLOWED_HOSTS='["a.example", "b.example"]', APP_DEBUG="0"):
        s = need(mod, "load_settings")()
    assert s.allowed_hosts == ["a.example", "b.example"] and s.debug is False


@case("env_values")
def h_env_invalid(mod):
    with env(APP_DATABASE_URL="x", APP_PORT="eighty"):
        assert raises_value_error(need(mod, "load_settings"))


@case("defaults_and_overrides")
def h_defaults(mod):
    with env(APP_DATABASE_URL="postgresql://db/app"):
        s = need(mod, "load_settings")()
    assert (s.app_name, s.debug, s.port, s.allowed_hosts) == ("orders-api", False, 8000, ["localhost"])


@case("defaults_and_overrides")
def h_overrides(mod):
    with env(APP_DATABASE_URL="postgresql://db/app", APP_PORT="9000"):
        s = need(mod, "load_settings")(port=1234, debug=True)
    assert (s.port, s.debug, s.database_url) == (1234, True, "postgresql://db/app")


@case("required_database_url")
def h_required(mod):
    with env(APP_PORT="9000"):
        assert raises_value_error(need(mod, "load_settings"))


@case("required_database_url")
def h_required_via_override(mod):
    with env():
        s = need(mod, "load_settings")(database_url="sqlite://")
    assert s.database_url == "sqlite://"
    with env(DATABASE_URL="sqlite:///unprefixed.db"):
        assert raises_value_error(need(mod, "load_settings")), "only APP_-prefixed variables are read"
