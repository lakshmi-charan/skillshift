"""Build verbatim event documents for the packaging_http family from the projects' own changelogs.

Fetches the raw changelog files from raw.githubusercontent.com and cuts the release sections for the
versions each event introduces (section boundaries are detected programmatically; nothing is retyped).

Usage: python benchmark/tools/make_packaging_docs.py benchmark/families/packaging_http/docs
"""
import datetime
import re
import sys
import urllib.request
from pathlib import Path

HTTPX = "https://raw.githubusercontent.com/encode/httpx/master/CHANGELOG.md"
MARSHMALLOW = "https://raw.githubusercontent.com/marshmallow-code/marshmallow/dev/CHANGELOG.rst"
SETUPTOOLS = "https://raw.githubusercontent.com/pypa/setuptools/main/NEWS.rst"


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8")


def md_sections(text, versions):
    """Markdown '## <version> (...)' sections."""
    lines = text.splitlines()
    heads = [i for i, l in enumerate(lines) if l.startswith("## ")]
    out = []
    for k, i in enumerate(heads):
        m = re.match(r"## (\S+)", lines[i])
        if m and m.group(1) in versions:
            end = heads[k + 1] if k + 1 < len(heads) else len(lines)
            out.append("\n".join(lines[i:end]).rstrip())
    return out


def rst_sections(text, versions, underline):
    """reStructuredText release sections: a title line starting with a version (optionally prefixed
    by 'v'), followed by an underline made of `underline` characters."""
    lines = text.splitlines()
    heads = [i for i in range(len(lines) - 1)
             if lines[i + 1] and set(lines[i + 1]) == {underline} and len(lines[i + 1]) >= len(lines[i].strip()) > 0
             and re.match(r"v?\d+\.\d+", lines[i])]
    out = []
    for k, i in enumerate(heads):
        ver = re.match(r"v?(\d+(?:\.\d+)+)", lines[i]).group(1)
        if ver in versions:
            end = heads[k + 1] if k + 1 < len(heads) else len(lines)
            out.append("\n".join(lines[i:end]).rstrip())
    return out


def write(out, name, title, url, lang, sections, note=""):
    today = datetime.date.today().isoformat()
    body = "\n\n".join(sections) + "\n"
    (out / f"{name}.md").write_text(
        f"# {title}\n\nSource: {url} (verbatim excerpt, fetched {today})\n{note}\n```{lang}\n{body}```\n",
        encoding="utf-8")
    print(name, len(body), "bytes")


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    write(out, "httpx-0.28", "httpx changelog: 0.28.0 and 0.28.1", HTTPX, "markdown",
          md_sections(fetch(HTTPX), {"0.28.0", "0.28.1"}),
          "License: BSD-3-Clause (https://github.com/encode/httpx/blob/master/LICENSE.md).\n")
    write(out, "marshmallow-4.0", "marshmallow changelog: 4.0.0 and 4.0.1", MARSHMALLOW, "rst",
          rst_sections(fetch(MARSHMALLOW), {"4.0.0", "4.0.1"}, "-"),
          "License: MIT (https://github.com/marshmallow-code/marshmallow/blob/dev/LICENSE).\n"
          "The upgrading guide referenced as :ref:`upgrading_4_0` is not included.\n")
    write(out, "setuptools-82", "setuptools changelog (NEWS.rst): v82.0.0 and v82.0.1", SETUPTOOLS, "rst",
          rst_sections(fetch(SETUPTOOLS), {"82.0.0", "82.0.1"}, "="),
          "License: MIT (https://github.com/pypa/setuptools/blob/main/LICENSE).\n"
          "v82.0.0 was published to PyPI on 2026-02-08 (https://pypi.org/pypi/setuptools/82.0.0/json).\n")


if __name__ == "__main__":
    main(sys.argv[1])
