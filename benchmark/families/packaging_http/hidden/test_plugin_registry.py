import os
import sys
import tempfile

from sa_testlib import case, need

_DIRS = {}


def _plugin_dir(tag):
    """A directory with an installed-looking distribution that advertises entry points."""
    if tag in _DIRS:
        return _DIRS[tag]
    d = tempfile.mkdtemp(prefix="sa_plugins_")
    mod = "sa_fmt_plugins_%s" % tag
    with open(os.path.join(d, mod + ".py"), "w") as fh:
        fh.write("def to_upper(s):\n    return s.upper()\n\ndef to_lower(s):\n    return s.lower()\n\n"
                 "class Reverse:\n    def __call__(self, s):\n        return s[::-1]\n")
    info = os.path.join(d, "sa_fmt_plugins_%s-1.2.0.dist-info" % tag)
    os.makedirs(info)
    with open(os.path.join(info, "METADATA"), "w") as fh:
        fh.write("Metadata-Version: 2.1\nName: sa-fmt-plugins-%s\nVersion: 1.2.0\n" % tag)
    with open(os.path.join(info, "entry_points.txt"), "w") as fh:
        fh.write("[sa.formatters]\nupper = %s:to_upper\nlower = %s:to_lower\nreverse = %s:Reverse\n\n"
                 "[sa.exporters]\nplain = %s:to_lower\n" % (mod, mod, mod, mod))
    sys.path.append(d)
    _DIRS[tag] = d
    return d


@case("plugin_names")
def h_names(mod):
    f = need(mod, "plugin_names")
    d = _plugin_dir("n")
    assert f("sa.formatters", paths=[d]) == ["lower", "reverse", "upper"]
    assert f("sa.exporters", paths=[d]) == ["plain"]
    assert f("sa.nothing_here", paths=[d]) == []


@case("plugin_names")
def h_names_default_path(mod):
    f = need(mod, "plugin_names")
    assert "httpx" in f("console_scripts")


@case("discover_plugins")
def h_discover(mod):
    f = need(mod, "discover_plugins")
    d = _plugin_dir("d")
    plugins = f("sa.formatters", paths=[d])
    assert sorted(plugins) == ["lower", "reverse", "upper"]
    assert plugins["upper"]("abc") == "ABC" and plugins["lower"]("AbC") == "abc"
    assert plugins["reverse"]()("abc") == "cba"


@case("discover_plugins")
def h_discover_empty(mod):
    f = need(mod, "discover_plugins")
    d = _plugin_dir("e")
    assert f("sa.unknown_group", paths=[d]) == {}


@case("load_plugin")
def h_load_one(mod):
    f = need(mod, "load_plugin")
    d = _plugin_dir("l")
    assert f("sa.exporters", "plain", paths=[d])("XY") == "xy"


@case("load_plugin")
def h_load_missing(mod):
    f = need(mod, "load_plugin")
    d = _plugin_dir("m")
    try:
        f("sa.formatters", "sparkle", paths=[d])
    except LookupError:
        return
    raise AssertionError("expected LookupError")
