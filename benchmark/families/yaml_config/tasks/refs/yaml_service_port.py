import yaml


def service_port(config_text):
    data = yaml.safe_load(config_text)
    if not isinstance(data, dict):
        raise ValueError("top level must be a mapping")
    return int(data["service"]["port"])
