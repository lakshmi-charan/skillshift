"""Build verbatim event documentation for the numpy_ops family.

Fetches the official release notes (doc/source/release/<version>-notes.rst) and, for 2.0, the NumPy 2.0
migration guide from the numpy GitHub repository at the release tags, and cuts the sections that list
removals / expired deprecations. Usage:
    python3 benchmark/tools/make_numpy_docs.py benchmark/families/numpy_ops/docs
"""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _docslice import fetch, between, span, render  # noqa: E402

NOTES = "https://raw.githubusercontent.com/numpy/numpy/v{v}/doc/source/release/{v}-notes.rst"
MIGRATION = "https://raw.githubusercontent.com/numpy/numpy/v2.0.0/doc/source/numpy_2_0_migration_guide.rst"


def title(L, v):
    return span(L, f"NumPy {v} Release Notes", f"NumPy {v} Release Notes")


def numpy_20(fetched):
    url = NOTES.format(v="2.0.0")
    L = fetch(url).splitlines()
    removals = between(L, "NumPy 2.0 Python API removals", "``__array_prepare__`` is removed")
    deprec = span(L, "* ``np.trapz`` has been deprecated.", "* Alias ``np.row_stack`` has been deprecated.")
    M = fetch(MIGRATION).splitlines()
    main_ns = between(M, "Main namespace", "Finally, a set of internal enums has been removed. As they weren't used in")
    methods = between(M, "ndarray and scalar methods", "numpy.strings namespace")
    a = render("NumPy 2.0.0 release notes: Python API removals", url, fetched,
               [title(L, "2.0.0"), removals, deprec])
    b = render("NumPy 2.0 migration guide: changes to namespaces", MIGRATION, fetched, [main_ns, methods])
    return a + "\n---\n\n" + b


def expired(v, fetched, end_heading):
    url = NOTES.format(v=v)
    L = fetch(url).splitlines()
    sec = between(L, "Expired deprecations", end_heading)
    return render(f"NumPy {v} release notes: expired deprecations", url, fetched, [title(L, v), sec])


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    fetched = datetime.date.today().isoformat()
    (out / "numpy-2.0.md").write_text(numpy_20(fetched), encoding="utf-8")
    (out / "numpy-2.3.md").write_text(expired("2.3.0", fetched, "C API changes"), encoding="utf-8")
    (out / "numpy-2.4.md").write_text(expired("2.4.0", fetched, "Compatibility notes"), encoding="utf-8")
    (out / "numpy-2.5.md").write_text(expired("2.5.0", fetched, "Compatibility notes"), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
