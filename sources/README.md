# Local copies of primary sources

Some change documents are cut from files that are awkward to fetch at build time (PDFs, HTML rendered from
repositories). These are the exact inputs used by the scripts in `benchmark/tools/`; every other document is
fetched directly from its source URL by those scripts.

| Folder | Contents | Origin | Terms |
|---|---|---|---|
| `nist/` | Text of NIST SP 800-63B (2017, updated 2020) section 5 and of SP 800-63B-4 (2025): authenticators, Appendix A, change log | `usnistgov/800-63-3` @ 7dee3ca and `usnistgov/800-63-4` @ 4f2487b on GitHub (HTML to text, markup removed only) | Public domain (U.S. Government work) |
| `nistpdf/` | NIST SP 800-131A Rev. 2, FIPS 186-5 and SP 800-52 Rev. 2: original PDFs and their extracted text | nvlpubs.nist.gov | Public domain (U.S. Government work) |
| `owasp/` | `Password_Storage_Cheat_Sheet.md` at seven commits of OWASP/CheatSheetSeries (728bbcd, 422ec84, ba94e5c, f14bc4c, f387056, 02bfdad, c3c1952) | github.com/OWASP/CheatSheetSeries | CC BY-SA 4.0 |
| `mozilla/` | Server-side TLS guideline JSON files (versions 4.0, 5.0, 5.6, 5.7, 5.8, 6.0) and CHANGELOG | github.com/mozilla/ssl-config-generator | MPL-2.0 |

To rebuild the documents of a family, e.g. `python benchmark/tools/make_nist_docs.py benchmark/families/nist_passwords/docs`.
Rebuilding reproduces the shipped documents byte for byte.
