"""Discover plugins advertised through package entry points (pkg_resources)."""
import pkg_resources


def _working_set(paths):
    return pkg_resources.WorkingSet(paths) if paths is not None else pkg_resources.working_set


def plugin_names(group, paths=None):
    """Sorted names of the entry points in `group`, searching `paths` (default: sys.path)."""
    return sorted({ep.name for ep in _working_set(paths).iter_entry_points(group)})


def discover_plugins(group, paths=None):
    """Load every entry point in `group`; returns {name: loaded object}."""
    return {ep.name: ep.load() for ep in _working_set(paths).iter_entry_points(group)}


def load_plugin(group, name, paths=None):
    """Load the entry point `name` of `group`; LookupError if there is none."""
    for ep in _working_set(paths).iter_entry_points(group, name):
        return ep.load()
    raise LookupError("no plugin %r in group %r" % (name, group))
