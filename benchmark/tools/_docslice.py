"""Helpers for cutting verbatim excerpts out of release-note sources (shared by make_*_docs.py)."""
import urllib.request

OMIT = "[... lines omitted from this excerpt ...]"


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8")


def find(lines, pred, start=0):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            return i
    raise ValueError("marker not found")


def between(lines, start_text, end_text, start=0, include_end=False):
    """Lines from the first line equal to start_text up to the next line equal to end_text
    (exclusive unless include_end)."""
    i = find(lines, lambda l: l.rstrip() == start_text, start)
    j = find(lines, lambda l: l.rstrip() == end_text, i + 1)
    return lines[i: j + (1 if include_end else 0)]


def span(lines, first_contains, last_contains, start=0):
    """Contiguous lines from the first line containing first_contains through the next line
    containing last_contains (both inclusive)."""
    i = find(lines, lambda l: first_contains in l, start)
    j = find(lines, lambda l: last_contains in l, i)
    return lines[i: j + 1]


def render(title, url, fetched, parts, lang="rst"):
    out = [f"# {title}", "", f"Source: {url} (verbatim excerpt, fetched {fetched})", ""]
    for k, p in enumerate(parts):
        p = list(p)
        while p and (not p[-1].strip() or p[-1].startswith(".. _")):
            p.pop()  # drop trailing blank lines / rst anchors of the next section
        if k:
            out += ["", OMIT, ""]
        out += [f"```{lang}"] + [l.rstrip("\n") for l in p] + ["```"]
    return "\n".join(out) + "\n"
