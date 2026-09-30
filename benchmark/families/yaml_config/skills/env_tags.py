"""YAML loading with '!env NAME[:default]' substitution (written against PyYAML 5.x)."""
import yaml

_ENV = {}


def _env_constructor(loader, node):
    raw = loader.construct_scalar(node)
    name, sep, default = raw.partition(":")
    if name in _ENV:
        return _ENV[name]
    if sep:
        return default
    raise KeyError(name)


yaml.add_constructor("!env", _env_constructor)


def load_with_env(text, env):
    """Load YAML text; scalars tagged !env NAME are replaced by env[NAME]."""
    _ENV.clear()
    _ENV.update(env)
    data = yaml.load(text)
    return {} if data is None else data
