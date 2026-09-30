"""Load plugin modules from files and plugin directories."""
import imp
import pkgutil


def load_module_from_path(name, path):
    """Execute the Python file at `path` as a module called `name` and return it.
    The module is registered in sys.modules under `name`."""
    return imp.load_source(name, path)


def is_importable(name):
    """True if a module called `name` can be imported (without importing it)."""
    try:
        return pkgutil.find_loader(name) is not None
    except ImportError:
        return False


def module_file(name):
    """Filesystem path of the source file of module `name`, or None if it cannot be found
    or has no file (e.g. built-in modules)."""
    try:
        loader = pkgutil.get_loader(name)
    except ImportError:
        return None
    if loader is None:
        return None
    get_filename = getattr(loader, "get_filename", None)
    if get_filename is None:
        return None
    return get_filename(name)


def list_plugins(directory):
    """Sorted names of the modules and packages found directly inside `directory`."""
    return sorted(info.name for info in pkgutil.iter_modules([str(directory)]))
