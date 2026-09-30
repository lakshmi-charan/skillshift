import yaml


def load_with_env(text, env):
    class _Loader(yaml.SafeLoader):
        pass

    def _env(loader, node):
        raw = loader.construct_scalar(node)
        name, sep, default = raw.partition(":")
        if name in env:
            return env[name]
        if sep:
            return default
        raise KeyError(name)

    _Loader.add_constructor("!env", _env)
    data = yaml.load(text, Loader=_Loader)
    return {} if data is None else data
