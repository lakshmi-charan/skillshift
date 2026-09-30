import yaml


def load_all_documents(text):
    return [doc for doc in yaml.safe_load_all(text) if doc is not None]
