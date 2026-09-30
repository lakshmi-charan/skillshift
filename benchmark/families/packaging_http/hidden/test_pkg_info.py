import importlib.metadata
import os
import sys
import tempfile

from sa_testlib import case, need


def _make_pkg(root, name):
    pkg = os.path.join(root, name)
    os.makedirs(os.path.join(pkg, "templates", "email"))
    with open(os.path.join(pkg, "__init__.py"), "w") as fh:
        fh.write("")
    with open(os.path.join(pkg, "defaults.json"), "w", encoding="utf-8") as fh:
        fh.write('{"greeting": "héllo"}\n')
    for n in ("welcome.txt", "reset.txt"):
        with open(os.path.join(pkg, "templates", n), "w", encoding="utf-8") as fh:
            fh.write("template " + n)
    with open(os.path.join(pkg, "templates", "email", "footer.txt"), "w", encoding="latin-1") as fh:
        fh.write("Grüße")
    sys.path.insert(0, root)


@case("installed_version")
def h_version(mod):
    f = need(mod, "installed_version")
    for dist in ("httpx", "marshmallow", "setuptools"):
        assert f(dist) == importlib.metadata.version(dist), dist


@case("installed_version")
def h_version_case(mod):
    f = need(mod, "installed_version")
    assert f("HTTPX") == importlib.metadata.version("httpx")
    assert f("Marshmallow") == importlib.metadata.version("marshmallow")


@case("missing_distribution")
def h_missing(mod):
    f = need(mod, "installed_version")
    assert f("sa-definitely-not-installed-pkg") is None
    assert f("requests_sa_missing") is None


@case("resource_text")
def h_resource_text(mod):
    f = need(mod, "read_resource_text")
    with tempfile.TemporaryDirectory() as d:
        _make_pkg(d, "sa_res_pkg_a")
        try:
            assert f("sa_res_pkg_a", "defaults.json") == '{"greeting": "héllo"}\n'
            assert f("sa_res_pkg_a", "templates/welcome.txt") == "template welcome.txt"
            assert f("sa_res_pkg_a", "templates/email/footer.txt", encoding="latin-1") == "Grüße"
        finally:
            sys.path.remove(d)


@case("resource_listing")
def h_listing(mod):
    f = need(mod, "list_resources")
    with tempfile.TemporaryDirectory() as d:
        _make_pkg(d, "sa_res_pkg_b")
        try:
            assert f("sa_res_pkg_b", "templates") == ["email", "reset.txt", "welcome.txt"]
            assert f("sa_res_pkg_b", "templates/email") == ["footer.txt"]
        finally:
            sys.path.remove(d)
