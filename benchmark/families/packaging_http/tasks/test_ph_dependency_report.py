import importlib.metadata

from sa_testlib import case, need


@case("functional")
def t_report(mod):
    f = need(mod, "dependency_report")
    out = f(["httpx", "Marshmallow", "setuptools", "sa-not-installed-dist"])
    assert out == {"httpx": importlib.metadata.version("httpx"),
                   "Marshmallow": importlib.metadata.version("marshmallow"),
                   "setuptools": importlib.metadata.version("setuptools"),
                   "sa-not-installed-dist": None}
