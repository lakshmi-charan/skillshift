"""Load application configuration from YAML (written against PyYAML 5.x)."""
import yaml


def load_config_text(text):
    """Parse YAML text and return the top-level mapping as a dict."""
    data = yaml.load(text)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("configuration must be a mapping at the top level")
    return data


def load_config_file(path):
    """Read a UTF-8 YAML file and return its top-level mapping."""
    with open(path, encoding="utf-8") as fh:
        return load_config_text(fh.read())
