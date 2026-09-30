"""Load plugin modules from files and plugin directories."""
import importlib.util
import pkgutil
import sys


def load_module_from_path(name, path):
    """Execute the Python file at `path` as a module called `name` and return it.
    The module is registered in sys.modules under `name`."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def _find_spec(name):
    try:
        return importlib.util.find_spec(name)
    except (ImportError, ValueError):
        return None


def is_importable(name):
    """True if a module called `name` can be imported (without importing it)."""
    return _find_spec(name) is not None


def module_file(name):
    """Filesystem path of the source file of module `name`, or None if it cannot be found
    or has no file (e.g. built-in modules)."""
    spec = _find_spec(name)
    if spec is None or not spec.has_location or not spec.origin:
        return None
    return spec.origin


def list_plugins(directory):
    """Sorted names of the modules and packages found directly inside `directory`."""
    return sorted(info.name for info in pkgutil.iter_modules([str(directory)]))
