import yaml


def build_dsn(config_text, env):
    class L(yaml.SafeLoader):
        pass

    def _env(loader, node):
        name, sep, default = loader.construct_scalar(node).partition(":")
        if name in env:
            return env[name]
        if sep:
            return default
        raise KeyError(name)

    L.add_constructor("!env", _env)
    db = yaml.load(config_text, Loader=L)["database"]
    return "postgresql://%s:%s@%s:%s/%s" % (db["user"], db["password"], db["host"], db["port"], db["name"])
