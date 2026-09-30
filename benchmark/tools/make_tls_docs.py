"""Build verbatim documents and the machine-readable policy module for the tls_config family.

Sources (fetched over HTTPS; nothing is typed or paraphrased):
  * Mozilla Server Side TLS guidelines, github.com/mozilla/ssl-config-generator, docs/guidelines/ at commit
    99178dc (2026-05-28): <version>.json and CHANGELOG.md. License MPL-2.0.
  * CPython 3.12.0 "What's New" (Doc/whatsnew/3.12.rst at tag v3.12.0): ssl-related items of "Removed".

Outputs (relative to benchmark/families/tls_config):
  docs/mozilla-guidelines-<v>.md  policy text in force (verbatim JSON) for 5.6, 5.7, 6.0
  docs/mozilla-tls-5.7.md         event doc: new JSON + CHANGELOG section + difflib diff of the JSON
  docs/mozilla-tls-6.0.md         event doc: new JSON + CHANGELOG sections (6.0.0, 5.8.0) + difflib diff
  docs/python-3.12.md             event doc: verbatim ssl-related "Removed" items of What's New in 3.12
  hidden/_policy.py               profile data transcribed programmatically from the JSON files

Usage: python3 benchmark/tools/make_tls_docs.py [--local sources/mozilla]
With --local, files are also compared byte-for-byte against a previously downloaded copy."""
import datetime
import difflib
import json
import pprint
import re
import sys
import urllib.request
from pathlib import Path

COMMIT = "99178dc"
MOZ = "https://raw.githubusercontent.com/mozilla/ssl-config-generator/%s/docs/guidelines/{f}" % COMMIT
CPY = "https://raw.githubusercontent.com/python/cpython/v3.12.0/Doc/whatsnew/3.12.rst"
MOZ_LICENSE = ("Mozilla ssl-config-generator (https://github.com/mozilla/ssl-config-generator), MPL-2.0. "
               "Verbatim copy; formatting preserved.")
CPY_LICENSE = "CPython documentation, PSF License / Zero-Clause BSD for code. Verbatim excerpt."
FAM = Path(__file__).resolve().parent.parent / "families" / "tls_config"
STATE_VERSION = {"s0": "5.6", "s1": "5.7", "s2": "5.7", "s3": "6.0"}
TODAY = datetime.date.today().isoformat()


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8")


def changelog_section(text, heading):
    """Verbatim text of the '## [<heading>] ...' section up to the next '## [' heading."""
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("## [%s]" % heading))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## [")), len(lines))
    return "\n".join(lines[start:end]).rstrip() + "\n"


def rst_subsection(lines, name, start, stop):
    """Verbatim lines of the rst subsection titled `name` (underlined with '-') within [start, stop)."""
    def is_title(k):
        return (lines[k] and not lines[k][0].isspace() and len(lines[k + 1]) >= 3
                and set(lines[k + 1]) <= {"-", "="} and len(set(lines[k + 1])) == 1)

    for i in range(start, stop - 1):
        if lines[i] == name and is_title(i):
            j = i + 2
            while j < stop and not is_title(j):
                j += 1
            return "\n".join(lines[i:j]).rstrip() + "\n"
    raise KeyError(name)


def header(title, sources, lic):
    src = "\n".join("Source: %s" % s for s in sources)
    return "# %s\n\n%s\nFetched: %s\nLicense: %s\n\n" % (title, src, TODAY, lic)


def main(argv):
    local = None
    if "--local" in argv:
        local = Path(argv[argv.index("--local") + 1])
    files = {v: fetch(MOZ.format(f="%s.json" % v)) for v in ("5.6", "5.7", "6.0")}
    changelog = fetch(MOZ.format(f="CHANGELOG.md"))
    if local is not None:
        for v, txt in files.items():
            assert (local / ("%s.json" % v)).read_text(encoding="utf-8") == txt, v
        assert (local / "CHANGELOG.md").read_text(encoding="utf-8") == changelog
    docs = FAM / "docs"
    docs.mkdir(parents=True, exist_ok=True)

    # policy text in force
    for v, txt in files.items():
        (docs / ("mozilla-guidelines-%s.md" % v)).write_text(
            header("Mozilla Server Side TLS guidelines, version %s (machine-readable)" % v,
                   [MOZ.format(f="%s.json" % v)], MOZ_LICENSE)
            + "This is the JSON document from which Mozilla's SSL Configuration Generator builds its server "
              "configurations (profiles: %s).\n\n```json\n%s```\n"
            % (", ".join(json.loads(txt)["configurations"]), txt), encoding="utf-8")

    # policy events
    for old, new, sections in (("5.6", "5.7", ["5.7"]), ("5.7", "6.0", ["6.0.0", "5.8.0"])):
        diff = "\n".join(difflib.unified_diff(files[old].splitlines(), files[new].splitlines(),
                                              fromfile="%s.json" % old, tofile="%s.json" % new,
                                              lineterm="", n=1))
        cl = "\n".join(changelog_section(changelog, s) for s in sections)
        body = (header("Mozilla Server Side TLS guidelines %s" % new,
                       [MOZ.format(f="%s.json" % new), MOZ.format(f="CHANGELOG.md")], MOZ_LICENSE)
                + "## CHANGELOG.md (verbatim section%s)\n\n```markdown\n%s```\n\n"
                % ("s" if len(sections) > 1 else "", cl)
                + "## Machine-generated diff of the guideline JSON (%s.json -> %s.json, difflib)\n\n"
                  "```diff\n%s\n```\n\n" % (old, new, diff)
                + "## %s.json (verbatim)\n\n```json\n%s```\n" % (new, files[new]))
        (docs / ("mozilla-tls-%s.md" % new)).write_text(body, encoding="utf-8")

    # python 3.12: ssl-related items of the "Removed" section
    rst = fetch(CPY).splitlines()
    r0 = next(i for i in range(len(rst) - 1) if rst[i] == "Removed" and set(rst[i + 1]) == {"="})
    r1 = next(i for i in range(r0 + 2, len(rst) - 1) if rst[i + 1] and set(rst[i + 1]) == {"="}
              and len(rst[i + 1]) >= 5)
    parts = [rst_subsection(rst, n, r0, r1) for n in ("ssl", "ftplib", "Others")]
    # drop a trailing rst cross-reference label that belongs to the next section
    parts[-1] = re.sub(r"\n\.\. _[^\n]*:\n$", "\n", parts[-1])
    (docs / "python-3.12.md").write_text(
        header("What's New In Python 3.12: ssl-related removals", [CPY], CPY_LICENSE)
        + "Verbatim excerpt of the \"Removed\" section (subsections ssl, ftplib and Others).\n\n"
          "```rst\nRemoved\n=======\n\n" + "\n".join(parts) + "```\n", encoding="utf-8")

    # machine-readable policy for the hidden tests
    data = {}
    for v, txt in files.items():
        conf = json.loads(txt)["configurations"]
        data[v] = {name: {"tls_versions": p["tls_versions"], "openssl": p["ciphers"]["openssl"],
                          "ciphersuites": p["ciphersuites"], "hsts_min_age": p["hsts_min_age"],
                          "server_preferred_order": p["server_preferred_order"]}
                   for name, p in conf.items()}
    (FAM / "hidden").mkdir(parents=True, exist_ok=True)
    (FAM / "hidden" / "_policy.py").write_text(POLICY_TEMPLATE % (
        COMMIT, pprint.pformat(data, width=110, sort_dicts=False), repr(STATE_VERSION)), encoding="utf-8")


POLICY_TEMPLATE = '''"""Machine-readable Mozilla Server Side TLS profiles used by the hidden tests.
GENERATED by benchmark/tools/make_tls_docs.py from docs/guidelines/<v>.json of mozilla/ssl-config-generator
at commit %s. Do not edit by hand."""
GUIDELINES = %s
STATE_VERSION = %s
ALL = list(STATE_VERSION)
_ORDER = ["SSLv3", "TLSv1", "TLSv1.1", "TLSv1.2", "TLSv1.3"]


def profiles(state):
    """{profile name: profile dict} in force in `state`."""
    return GUIDELINES[STATE_VERSION[state]]


def profile(state, name):
    """Profile dict, or None if the profile does not exist in the guidelines in force."""
    return profiles(state).get(name)


def min_version(prof):
    return min(prof["tls_versions"], key=_ORDER.index)


def states(pred):
    """States whose in-force guidelines satisfy pred(profiles_dict)."""
    return [s for s in ALL if pred(profiles(s))]
'''

if __name__ == "__main__":
    main(sys.argv[1:])
