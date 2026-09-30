"""Build verbatim docs for nist_passwords from local copies of the official NIST repositories.

Sources (cloned from GitHub by the harness operator; text extracted from HTML without rewording):
  usnistgov/800-63-3 @ 7dee3ca (branch nist-pages)  sp800-63b/sec5_authenticators.md   (SP 800-63B, June 2017, updates 2020-03-02)
  usnistgov/800-63-4 @ 4f2487b (branch main)        sp800-63b/authenticators/index.html, changelog/index.html (SP 800-63B-4, final 2025-07-31)
The HTML-to-text step keeps words, list items and headings; only markup is removed."""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "sources" / "nist"


def between(text, start, end):
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j].strip()


def main(out):
    out = Path(out)
    r3 = (SRC / "nist-800-63b-rev3_sec5_authenticators.md").read_text(encoding="utf-8")
    sec = between(r3, "#### <a name=\"memsecretver\"></a> 5.1.1.2 Memorized Secret Verifiers", "### <a name=\"lookupsecrets\"></a>") \
        if "### <a name=\"lookupsecrets\"></a>" in r3 else between(r3, "5.1.1.2 Memorized Secret Verifiers", "#### <a name")
    thr_i = r3.index("the verifier SHALL limit consecutive failed authentication attempts on a single account to no more than 100.")
    para_start = r3.rfind("\n\n", 0, thr_i) + 2
    para_end = r3.index("\n\n", thr_i)
    head = ("# NIST SP 800-63B Digital Identity Guidelines: Authentication and Lifecycle Management "
            "(June 2017, includes updates as of 2020-03-02)\n\n"
            "Source: https://pages.nist.gov/800-63-3/sp800-63b.html (repository usnistgov/800-63-3, commit 7dee3ca, "
            "file sp800-63b/sec5_authenticators.md). Public domain (U.S. Government work). Verbatim excerpt.\n\n")
    (out / "nist-800-63b-rev3.md").write_text(head + sec + "\n\n#### 5.2.2 Rate Limiting (Throttling) [excerpt]\n\n"
                                               + r3[para_start:para_end] + "\n", encoding="utf-8")
    r4 = (SRC / "nist-800-63b-4_authenticators.txt").read_text(encoding="utf-8")
    pw = between(r4, "Password Verifiers", "Look-Up Secrets")
    thr_i = r4.index("the verifier SHALL limit consecutive failed authentication attempts using a specific authenticator")
    p0 = r4.rfind("\n\n", 0, thr_i) + 2
    p1 = r4.index("\n\n", thr_i)
    cl = (SRC / "nist-800-63b-4_changelog.txt").read_text(encoding="utf-8")
    cl = cl[cl.index("This appendix provides an overview"):]
    cl = cl[: cl.index("Section 3.2.11:")].strip()
    head4 = ("# NIST SP 800-63B-4 Digital Identity Guidelines: Authentication and Authenticator Management "
             "(final, published 2025-07-31)\n\n"
             "Source: https://doi.org/10.6028/NIST.SP.800-63b-4 ; HTML edition https://pages.nist.gov/800-63-4/ "
             "(repository usnistgov/800-63-4, commit 4f2487b). Public domain (U.S. Government work). "
             "Verbatim excerpts; markup removed.\n\n")
    (out / "nist-800-63b-4.md").write_text(
        head4 + "## Change Log (Appendix, excerpt)\n\n" + cl + "\n\n## 3.1.1.2 " + pw
        + "\n\n## 3.2.2 Rate Limiting (Throttling) [excerpt]\n\n" + r4[p0:p1].strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
