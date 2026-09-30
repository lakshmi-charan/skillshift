"""Split multi-document YAML streams (written against PyYAML 5.x)."""
import yaml


def load_all_documents(text):
    """Return the non-empty documents of a '---'-separated YAML stream, in order."""
    return [doc for doc in yaml.load_all(text) if doc is not None]
