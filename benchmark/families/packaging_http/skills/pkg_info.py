"""Runtime information about installed distributions and packaged data files (pkg_resources)."""
import pkg_resources


def installed_version(name):
    """Version string of the installed distribution `name` (case-insensitive), or None if not installed."""
    try:
        return pkg_resources.get_distribution(name).version
    except pkg_resources.DistributionNotFound:
        return None


def read_resource_text(package, resource, encoding="utf-8"):
    """Text of a data file shipped inside `package` (resource path uses '/')."""
    return pkg_resources.resource_string(package, resource).decode(encoding)


def list_resources(package, subdir):
    """Sorted names of the entries in a data directory shipped inside `package`."""
    return sorted(pkg_resources.resource_listdir(package, subdir))
