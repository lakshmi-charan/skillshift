import yaml


def load_config_text(text):
    data = yaml.safe_load(text)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("configuration must be a mapping at the top level")
    return data


def load_config_file(path):
    with open(path, encoding="utf-8") as fh:
        return load_config_text(fh.read())
