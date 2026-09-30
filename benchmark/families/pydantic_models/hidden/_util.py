"""Helpers for the pydantic_models hidden tests (no pydantic API used here)."""


def raises_value_error(fn, *args, **kwargs):
    """True if fn(...) raises ValueError (pydantic's ValidationError is a ValueError subclass)."""
    try:
        fn(*args, **kwargs)
    except ValueError:
        return True
    return False


class Obj:
    """Minimal stand-in for an ORM row object: exposes the given attributes (and nothing dict-like)."""

    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)
