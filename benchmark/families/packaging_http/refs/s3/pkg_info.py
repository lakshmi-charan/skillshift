"""Runtime information about installed distributions and packaged data files."""
import importlib.metadata
import importlib.resources


def installed_version(name):
    """Version string of the installed distribution `name` (case-insensitive), or None if not installed."""
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _resource(package, resource):
    node = importlib.resources.files(package)
    for part in resource.split("/"):
        if part:
            node = node.joinpath(part)
    return node


def read_resource_text(package, resource, encoding="utf-8"):
    """Text of a data file shipped inside `package` (resource path uses '/')."""
    return _resource(package, resource).read_text(encoding=encoding)


def list_resources(package, subdir):
    """Sorted names of the entries in a data directory shipped inside `package`."""
    return sorted(entry.name for entry in _resource(package, subdir).iterdir())
