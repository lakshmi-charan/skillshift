"""Serialise configuration dicts to YAML."""
import yaml


def dump_config(config):
    """Return block-style YAML text for a configuration dict, preserving key order."""
    return yaml.safe_dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)
