def _key(v):
    return tuple(int(p) for p in v.split("."))


def newest_compatible(versions, minimum):
    ok = [v for v in versions if _key(v) >= _key(minimum)]
    return max(ok, key=_key) if ok else None
