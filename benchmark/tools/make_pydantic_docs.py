"""Build the verbatim event document for the pydantic_models family from the pydantic repository.

Fetches docs/migration.md at the v2.0 release tag from raw.githubusercontent.com and cuts the
relevant sections programmatically (no text is typed by hand).

    python3 benchmark/tools/make_pydantic_docs.py benchmark/families/pydantic_models/docs
"""
import datetime
import sys
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/pydantic/pydantic/v2.0/docs/migration.md"
LICENSE = "Pydantic documentation, MIT License (https://github.com/pydantic/pydantic). Verbatim excerpt."

# headings of the kept sections (each kept with its subsections), in document order
SECTIONS = [
    "### Changes to `pydantic.BaseModel`",
    "### Changes to `pydantic.Field`",
    "### Changes to config",
    "### Changes to validators",
    "#### Required, optional, and nullable fields",
    "### Introduction of `TypeAdapter`",
    "### Defining custom types",
    "### `BaseSettings` has moved to `pydantic-settings`",
]
# subsections of the kept sections that are omitted (not relevant to the deployment)
DROP = [
    "#### `@validate_arguments` has been renamed to `@validate_call`",
]


def fetch():
    with urllib.request.urlopen(URL, timeout=60) as r:
        return r.read().decode("utf-8")


def _level(line):
    if not line.startswith("#"):
        return None
    n = len(line) - len(line.lstrip("#"))
    return n if line[n:n + 1] == " " else None


def section(lines, heading):
    """Lines of the markdown section starting at `heading` up to the next heading of the same or higher
    level (fenced code blocks are skipped when looking for headings)."""
    fenced = False
    heads = []
    for i, ln in enumerate(lines):
        if ln.startswith("```"):
            fenced = not fenced
            continue
        if not fenced and _level(ln):
            heads.append((i, _level(ln), ln.rstrip()))
    idx = [k for k, h in enumerate(heads) if h[2] == heading]
    if not idx:
        raise SystemExit(f"heading not found: {heading!r}")
    k = idx[0]
    start, lvl = heads[k][0], heads[k][1]
    end = next((i for i, l, _ in heads[k + 1:] if l <= lvl), len(lines))
    keep = list(range(start, end))
    for d in DROP:
        for j, (i, l, t) in enumerate(heads):
            if t == d and start < i < end:
                stop = next((i2 for i2, l2, _ in heads[j + 1:] if l2 <= l), end)
                keep = [x for x in keep if not (i <= x < min(stop, end))]
    body = [lines[x] for x in keep]
    while body and not body[-1].strip():
        body.pop()
    return "\n".join(body)


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    lines = fetch().splitlines()
    parts = [section(lines, h) for h in SECTIONS]
    today = datetime.date.today().isoformat()
    doc = (f"# Pydantic V2 Migration Guide (selected sections)\n\n"
           f"Source: {URL} (verbatim excerpt, fetched {today})\nLicense: {LICENSE}\n\n"
           f"Pydantic 2.0 was released on 2023-06-30. Sections are cut programmatically from the guide's "
           f"\"Migration guide\" chapter; headings keep their original levels.\n\n---\n\n"
           + "\n\n".join(parts) + "\n")
    (out / "pydantic-2.0.md").write_text(doc, encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "benchmark/families/pydantic_models/docs")
