"""Verbatim docs for legacy_crypto.

NIST PDFs downloaded by the operator from nvlpubs.nist.gov (sha256 recorded below) and converted with
`pdftotext -layout`; the excerpts are cut by line markers and whitespace is normalised (no rewording).
  NIST.SP.800-131Ar2.pdf  5c81a1095e0eee35ce0e627b8cc672c1c2239367b0de9bb53d7271c9ab9d7d27
  NIST.FIPS.186-5.pdf     fbb9c7c2ba442f03c57b63b43c888311903c9d0f29f89b06efdebd9b619140c5
cryptography changelog: raw.githubusercontent.com/pyca/cryptography/main/CHANGELOG.rst (43.0.0 section)."""
import re
import sys
import urllib.request
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "sources" / "nistpdf"
NOISE = ("This publication is available free of charge", "NIST SP 800-131A REV. 2", "ALGORITHMS AND KEY LENGTHS",
         "FIPS 186-5                   ", "DIGITAL SIGNATURE STANDARD (DSS)")


def clean(lines):
    out = []
    for l in lines:
        if any(n in l for n in NOISE) or re.fullmatch(r"\s*\d+\s*", l):
            continue
        out.append(re.sub(r"\s{2,}", "  ", l.strip()))
    txt = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def cut(text, start, end):
    i = text.index(start)
    j = text.index(end, i)
    return clean(text[i:j].splitlines())


def main(out):
    out = Path(out)
    sp = (SRC / "NIST.SP.800-131Ar2.txt").read_text(encoding="utf-8")
    fi = (SRC / "NIST.FIPS.186-5.txt").read_text(encoding="utf-8")
    t1 = cut(sp, "Table 1: Approval Status of Symmetric Algorithms", "SKIPJACK encryption and decryption:")
    t5 = cut(sp, "Table 5: Approval Status for the RSA-based Key Agreement", "7       Key Wrapping")
    hdr131 = ("NIST SP 800-131A Rev. 2, Transitioning the Use of Cryptographic Algorithms and Key Lengths (March 2019), "
              "https://doi.org/10.6028/NIST.SP.800-131Ar2 . Public domain. Verbatim excerpts (text extracted from the "
              "PDF; whitespace normalised).")
    fips_intro = cut(fi, "The Digital Signature Algorithm (DSA) is no longer specified", "This standard includes requirements")
    fips_s4 = cut(fi, "4      The Digital Signature Algorithm (DSA)\nPrior versions", "5.     The RSA Digital Signature")
    fips_sched = cut(fi, "12. Implementation Schedule:", "13. Specifications:")
    fips_dates = "Published: February 3, 2023\nEffective: February 3, 2023 (see the Implementation Schedule)"
    hdr186 = ("FIPS 186-5, Digital Signature Standard (DSS), https://doi.org/10.6028/NIST.FIPS.186-5 . Public domain. "
              "Verbatim excerpts (text extracted from the PDF; whitespace normalised).")
    policy = (f"# Cryptographic rules in force for this deployment\n\n## {hdr131}\n\n{t1}\n\n{t5}\n\n## {hdr186}\n\n"
              f"{fips_dates}\n\n{fips_intro}\n\n{fips_s4}\n\n{fips_sched}\n")
    (out / "policy-nist.md").write_text(policy, encoding="utf-8")
    (out / "sp800-131a-r2-2024.md").write_text(
        "# Transition dates of NIST SP 800-131A Rev. 2 reached: December 31, 2023 has passed\n\n"
        f"Source: {hdr131}\n\n{t1}\n\n{t5}\n", encoding="utf-8")
    (out / "fips-186-4-withdrawn.md").write_text(
        "# One year after publication of FIPS 186-5 (February 3, 2023): FIPS 186-4 is withdrawn\n\n"
        f"Source: {hdr186}\n\n{fips_dates}\n\n{fips_sched}\n\n{fips_intro}\n\n{fips_s4}\n", encoding="utf-8")
    url = "https://raw.githubusercontent.com/pyca/cryptography/main/CHANGELOG.rst"
    cl = urllib.request.urlopen(url, timeout=60).read().decode("utf-8")
    i = cl.index("43.0.0 - 2024-07-20")
    j = cl.index("42.0.8 - ", i)
    (out / "cryptography-43.0.md").write_text(
        f"# cryptography 43.0.0 release notes\n\nSource: {url} (verbatim section)\n\n```rst\n{cl[i:j].rstrip()}\n```\n",
        encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
