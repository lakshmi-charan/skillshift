"""Build verbatim event documents for the stdlib_compat family from the CPython "What's New" sources.

Fetches Doc/whatsnew/3.X.rst at the release tag from raw.githubusercontent.com and cuts the
removal sections (reStructuredText headings are detected programmatically; no text is retyped).

Usage: python benchmark/tools/make_stdlib_docs.py benchmark/families/stdlib_compat/docs
"""
import datetime
import sys
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/python/cpython/{tag}/Doc/whatsnew/{ver}.rst"
LICENSE = ("Python documentation, Copyright Python Software Foundation, "
           "PSF License / Zero-Clause BSD for code examples (https://docs.python.org/3/license.html). "
           "Verbatim excerpt; reStructuredText markup preserved.")

# (doc name, tag, version, top-level section, subsections to drop)
DOCS = [
    ("python-3.12", "v3.12.0", "3.12", "Removed", {"ssl"}),
    ("python-3.13", "v3.13.0", "3.13", "Removed Modules And APIs", set()),
    ("python-3.14", "v3.14.0", "3.14", "Removed", set()),
]
UNDERLINE = set("=-~^*#")


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8")


def headings(lines):
    """Yield (line index of title, underline char, title) for each RST section heading."""
    out = []
    for i in range(1, len(lines)):
        u, t = lines[i], lines[i - 1]
        if (u and len(set(u)) == 1 and u[0] in UNDERLINE and len(u) >= 3 and t.strip()
                and len(u) >= len(t.rstrip()) and not set(t.strip()) <= set(u[0])):
            # skip over-and-under titles (the line above the title is the same underline)
            out.append((i - 1, u[0], t.strip()))
    return out


def cut(text, section, drop):
    lines = text.splitlines()
    hs = headings(lines)
    start = next(k for k, (i, ch, t) in enumerate(hs) if t == section and ch == "=")
    level = hs[start][1]
    end_line = len(lines)
    for i, ch, t in hs[start + 1:]:
        if ch == level:
            end_line = i
            break
    sub = [h for h in hs if hs[start][0] < h[0] < end_line]
    sub_level = sub[0][1] if sub else None
    keep = []
    skip_until = -1
    bounds = [h[0] for h in sub if h[1] == sub_level] + [end_line]
    for idx in range(hs[start][0], end_line):
        if idx < skip_until:
            continue
        for h in sub:
            if h[0] == idx and h[1] == sub_level and h[2] in drop:
                skip_until = next(b for b in bounds if b > idx)
                break
        if idx < skip_until:
            continue
        keep.append(lines[idx])
    return "\n".join(keep).rstrip() + "\n"


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    for name, tag, ver, section, drop in DOCS:
        url = URL.format(tag=tag, ver=ver)
        body = cut(fetch(url), section, drop)
        note = ""
        if drop:
            note = "Subsections omitted from this excerpt: " + ", ".join(sorted(drop)) + ".\n"
        (out / f"{name}.md").write_text(
            f"# What's New In Python {ver} -- section \"{section}\"\n\n"
            f"Source: {url} (verbatim excerpt, fetched {today})\n"
            f"License: {LICENSE}\n{note}\n```rst\n{body}```\n", encoding="utf-8")
        print(name, len(body), "bytes")


if __name__ == "__main__":
    main(sys.argv[1])
