"""Build verbatim event documentation for the pandas_ops family.

Fetches the official "What's new" pages from the pandas GitHub repository at the release tags and cuts
the sections relevant to the family (removals/deprecations). Usage:
    python3 benchmark/tools/make_pandas_docs.py benchmark/families/pandas_ops/docs
"""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _docslice import fetch, between, span, render  # noqa: E402

V200 = "https://raw.githubusercontent.com/pandas-dev/pandas/v2.0.0/doc/source/whatsnew/v2.0.0.rst"
V300 = "https://raw.githubusercontent.com/pandas-dev/pandas/v3.0.0/doc/source/whatsnew/v3.0.0.rst"


def pandas_20(fetched):
    L = fetch(V200).splitlines()
    head = span(L, "What's new in 2.0.0", "-----")
    rem0 = L.index("Removal of prior version deprecations/changes")
    removals = span(L, "Removal of prior version deprecations/changes", "Removed deprecated :meth:`Index.is_all_dates`")
    numeric = span(L, "Enforced deprecation disallowing passing ``numeric_only=True`` to :class:`Series` reductions",
                   "Changed default of ``numeric_only`` to ``False`` in :class:`.Resampler` methods", rem0)
    return render("pandas 2.0.0: What's new (removal of prior version deprecations)", V200, fetched,
                  [head, removals, numeric])


def pandas_30(fetched):
    L = fetch(V300).splitlines()
    head = span(L, "What's new in 3.0.0", "-----")
    strings = between(L, "Dedicated string data type by default", "Consistent copy/view behaviour with Copy-on-Write")
    cow = between(L, "Consistent copy/view behaviour with Copy-on-Write", "Initial support for ``pd.col()`` syntax to create expressions")
    cow = [l for l in cow if not l.startswith(".. _whatsnew_300.enhancements")]
    rem0 = L.index("Removal of prior version deprecations/changes")
    aliases = span(L, "Removal of prior version deprecations/changes", "Other Removals", rem0)
    other = span(L, "Other Removals", "no longer accept raw string or byte representation of the data", rem0)
    freq = span(L, "Enforced deprecation of string ``A`` denoting frequency in :class:`.YearEnd`",
                "Enforced deprecation of strings ``T``, ``L``, ``U``, and ``N`` denoting units in :class:`Timedelta`", rem0)
    applymap = span(L, "Removed :meth:`DateOffset.is_anchored`", "Removed ``DataFrame.swapaxes`` and ``Series.swapaxes``", rem0)
    return render("pandas 3.0.0: What's new (string dtype, Copy-on-Write, removals)", V300, fetched,
                  [head, strings, cow, aliases[:-1], other, freq, applymap])


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    fetched = datetime.date.today().isoformat()
    (out / "pandas-2.0.md").write_text(pandas_20(fetched), encoding="utf-8")
    (out / "pandas-3.0.md").write_text(pandas_30(fetched), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
