"""Build verbatim policy documents for the password_storage family from OWASP CheatSheetSeries commits.
Fetches cheatsheets/Password_Storage_Cheat_Sheet.md at each commit from raw.githubusercontent.com."""
import difflib
import sys
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/OWASP/CheatSheetSeries/{c}/cheatsheets/Password_Storage_Cheat_Sheet.md"
STATES = [("s0", "728bbcd", "2021-03-17"), ("s1", "422ec84", "2022-06-10"), ("s2", "f14bc4c", "2023-01-24"),
          ("s3", "f387056", "2024-12-09"), ("s4", "02bfdad", "2026-03-26"), ("s5", "c3c1952", "2026-05-12")]
LICENSE = ("OWASP Cheat Sheet Series, CC BY-SA 4.0 (https://github.com/OWASP/CheatSheetSeries). "
           "Verbatim excerpt; formatting preserved.")


def fetch(c):
    with urllib.request.urlopen(URL.format(c=c), timeout=60) as r:
        return r.read().decode("utf-8")


def main(out):
    out = Path(out)
    texts = {sid: fetch(c) for sid, c, _ in STATES}
    sid0, c0, d0 = STATES[0]
    (out / f"owasp-{d0}-full.md").write_text(
        f"# OWASP Password Storage Cheat Sheet as of {d0} (commit {c0})\n\nSource: {URL.format(c=c0)}\n"
        f"License: {LICENSE}\n\n---\n\n" + texts[sid0], encoding="utf-8")
    for (pa, ca, da), (pb, cb, db) in zip(STATES, STATES[1:]):
        diff = difflib.unified_diff(texts[pa].splitlines(), texts[pb].splitlines(),
                                    fromfile=f"{ca} ({da})", tofile=f"{cb} ({db})", lineterm="", n=2)
        body = "\n".join(diff)
        (out / f"owasp-{db}-diff.md").write_text(
            f"# OWASP Password Storage Cheat Sheet revision of {db} (commit {cb})\n\n"
            f"Source: {URL.format(c=cb)}\nLicense: {LICENSE}\n\n"
            f"Unified diff against the previous revision ({ca}, {da}):\n\n```diff\n{body}\n```\n\n"
            f"Updated summary section (verbatim, {cb}):\n\n" + "\n".join(texts[pb].splitlines()[:24]) + "\n",
            encoding="utf-8")
        (out / f"owasp-{db}-full.md").write_text(
            f"# OWASP Password Storage Cheat Sheet as of {db} (commit {cb})\n\nSource: {URL.format(c=cb)}\n"
            f"License: {LICENSE}\n\n---\n\n" + texts[pb], encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
