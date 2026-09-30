"""Compare dotted version strings such as '1.10.2' (release numbers of tools, APIs and packages)."""
from packaging.version import Version


def compare_versions(a, b):
    """Return -1 if a < b, 0 if equal, 1 if a > b."""
    va, vb = Version(a), Version(b)
    if va < vb:
        return -1
    if va > vb:
        return 1
    return 0


def sort_versions(versions, reverse=False):
    """Return the version strings sorted in version order (not string order)."""
    return sorted(versions, key=Version, reverse=reverse)


def latest_version(versions):
    """Return the highest version string, or None for an empty sequence."""
    versions = list(versions)
    if not versions:
        return None
    return max(versions, key=Version)


def meets_minimum(installed, minimum):
    """True if `installed` is at least `minimum`."""
    return Version(installed) >= Version(minimum)
