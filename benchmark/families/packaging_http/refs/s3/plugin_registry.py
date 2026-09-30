"""Discover plugins advertised through package entry points (importlib.metadata)."""
import importlib.metadata


def _entry_points(group, paths):
    seen = {}
    dists = importlib.metadata.distributions(path=list(paths)) if paths is not None \
        else importlib.metadata.distributions()
    for dist in dists:
        for ep in dist.entry_points:
            if ep.group == group and ep.name not in seen:
                seen[ep.name] = ep
    return seen


def plugin_names(group, paths=None):
    """Sorted names of the entry points in `group`, searching `paths` (default: sys.path)."""
    return sorted(_entry_points(group, paths))


def discover_plugins(group, paths=None):
    """Load every entry point in `group`; returns {name: loaded object}."""
    return {name: ep.load() for name, ep in _entry_points(group, paths).items()}


def load_plugin(group, name, paths=None):
    """Load the entry point `name` of `group`; LookupError if there is none."""
    ep = _entry_points(group, paths).get(name)
    if ep is None:
        raise LookupError("no plugin %r in group %r" % (name, group))
    return ep.load()
