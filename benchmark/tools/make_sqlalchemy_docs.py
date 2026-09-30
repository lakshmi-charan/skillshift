"""Build verbatim event documents for the sqlalchemy_ops family from the SQLAlchemy repository.

Fetches the reStructuredText migration guides / changelog at the release tags from
raw.githubusercontent.com and cuts the relevant sections programmatically (no text is typed by hand).

    python3 benchmark/tools/make_sqlalchemy_docs.py benchmark/families/sqlalchemy_ops/docs
"""
import datetime
import re
import sys
import urllib.request
from pathlib import Path

RAW = "https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/{tag}/doc/build/changelog/{name}"
LICENSE = "SQLAlchemy documentation, MIT License (https://github.com/sqlalchemy/sqlalchemy). Verbatim excerpt."
UNDERLINE = re.compile(r"^([=\-~^\"+*])\1{3,}$")


def fetch(tag, name):
    url = RAW.format(tag=tag, name=name)
    with urllib.request.urlopen(url, timeout=60) as r:
        return url, r.read().decode("utf-8")


def headings(lines):
    """[(index_of_title_line, title, underline_char)] for every rst section heading."""
    out = []
    for i in range(1, len(lines)):
        prev = lines[i - 1]
        if UNDERLINE.match(lines[i]) and prev.strip() and not UNDERLINE.match(prev):
            # skip over-and-under titles' top rule
            out.append((i - 1, prev.strip(), lines[i][0]))
    return out


def section(text, title, drop=(), drop_discussion=False):
    """Verbatim text of the section `title` up to the next heading of the same or a higher level.
    Subsections whose titles are listed in `drop` are omitted (cut at their heading, resumed at the next
    heading of their level or higher)."""
    lines = text.splitlines()
    hs = headings(lines)
    order = []
    for _, _, ch in hs:
        if ch not in order:
            order.append(ch)
    rank = {ch: order.index(ch) for ch in order}
    starts = [k for k, h in enumerate(hs) if h[1] == title]
    if not starts:
        raise SystemExit(f"section not found: {title!r}")
    k0 = starts[0]
    r0 = rank[hs[k0][2]]
    end = len(lines)
    for i, t, ch in hs[k0 + 1:]:
        if rank[ch] <= r0:
            end = i
            break
    keep = [True] * len(lines)
    for k, (i, t, ch) in enumerate(hs):
        if t in drop and hs[k0][0] < i < end:
            stop = end
            for j, _, ch2 in hs[k + 1:]:
                if rank[ch2] <= rank[ch]:
                    stop = min(j, end)
                    break
            for x in range(i, stop):
                keep[x] = False
    if drop_discussion:
        # omit each "**Discussion**" block (rationale prose) up to the next heading
        heads = {i for i, _, _ in hs}
        inside = False
        for x in range(hs[k0][0], end):
            if lines[x].strip() == "**Discussion**":
                inside = True
            elif x in heads:
                inside = False
            if inside:
                keep[x] = False
    body = [ln for x, ln in enumerate(lines[hs[k0][0]:end], start=hs[k0][0]) if keep[x]]
    # trailing ".. _label:" anchors belong to the next section
    while body and (not body[-1].strip() or body[-1].startswith(".. _")):
        body.pop()
    return "\n".join(body) + "\n"


def changelog_entries(text, version, tickets):
    """Verbatim `.. change::` blocks of `version` whose :tickets: include any of `tickets`."""
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip() == f":version: {version}")
    head = [lines[start - 1], lines[start]]
    j = start + 1
    while j < len(lines) and not lines[j].strip().startswith(".. change::"):
        head.append(lines[j])
        j += 1
    stop = next((i for i in range(j, len(lines)) if lines[i].startswith(".. changelog::")), len(lines))
    blocks, cur = [], None
    for ln in lines[j:stop]:
        if ln.strip().startswith(".. change::"):
            if cur:
                blocks.append(cur)
            cur = [ln]
        elif cur is not None:
            cur.append(ln)
    if cur:
        blocks.append(cur)
    chosen = []
    for b in blocks:
        tk = next((ln for ln in b if ":tickets:" in ln), "")
        nums = set(re.findall(r"\d+", tk))
        if nums & set(tickets):
            while b and not b[-1].strip():
                b.pop()
            chosen.append("\n".join(b))
    missing = [t for t in tickets if not any(re.search(rf":tickets:.*\b{t}\b", c) for c in chosen)]
    if missing:
        raise SystemExit(f"changelog tickets not found: {missing}")
    return "\n".join(ln for ln in head if ln.strip()) + "\n\n" + "\n\n".join(chosen) + "\n"


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()

    # ---- SQLAlchemy 2.0 (2023-01-26): migration guide at the rel_2_0_0 tag
    url20, mig20 = fetch("rel_2_0_0", "migration_20.rst")
    parts = [
        section(mig20, 'Library-level (but not driver level) "Autocommit" removed from both Core and ORM',
                drop=("Driver-level autocommit remains available",), drop_discussion=True),
        section(mig20, '"Implicit" and "Connectionless" execution, "bound metadata" removed',
                drop=("Many Choices becomes One Choice",), drop_discussion=True),
        section(mig20, "execute() method more strict, execution options are more prominent", drop_discussion=True),
        section(mig20, "Result rows act like named tuples", drop_discussion=True),
        section(mig20, "select() no longer accepts varied constructor arguments, columns are passed positionally",
                drop_discussion=True),
        section(mig20, "ORM Query  - Joining / loading on relationships uses attributes, not strings",
                drop_discussion=True),
        section(mig20, 'Session "subtransaction" behavior removed', drop_discussion=True),
    ]
    # the 2.0 guide defers the details of the Row API change to the 1.4 notes (same tag)
    url14, mig14 = fetch("rel_2_0_0", "migration_14.rst")
    row14 = section(mig14, 'RowProxy is no longer a "proxy"; is now called Row and behaves like an enhanced named tuple',
                    drop=("Proxying behavior goes away, was also unnecessary in modern usage",))
    doc = (f"# SQLAlchemy 2.0 - Major Migration Guide (selected sections)\n\n"
           f"Sources (verbatim excerpts, fetched {today}):\n- {url20}\n- {url14} "
           f"(section referenced by the 2.0 guide for the Row API; last part of this document)\n"
           f"License: {LICENSE}\n\n"
           f"Sections are cut programmatically; the rationale (\"**Discussion**\") paragraphs are omitted.\n\n```rst\n" + "\n\n".join(parts) + "```\n\n"
           f"## From \"What's New in SQLAlchemy 1.4?\" (migration_14.rst)\n\n```rst\n{row14}```\n")
    (out / "sqlalchemy-2.0.md").write_text(doc, encoding="utf-8")

    # ---- SQLAlchemy 2.1 (2026-09-24): changelog + migration notes at the rel_2_1_0 tag
    urlc, cl21 = fetch("rel_2_1_0", "changelog_21.rst")
    urlm, mig21 = fetch("rel_2_1_0", "migration_21.rst")
    entries = changelog_entries(cl21, "2.1.0b1", ["10236", "12218", "12441", "9647"])
    fb = section(mig21, "``filter_by()`` now searches across all FROM clause entities")
    doc = (f"# SQLAlchemy 2.1 - selected changelog entries and migration notes\n\n"
           f"Sources (verbatim excerpts, fetched {today}):\n- {urlc}\n- {urlm}\nLicense: {LICENSE}\n\n"
           f"## From the 2.1 changelog ({urlc.rsplit('/', 1)[-1]})\n\n```rst\n{entries}```\n\n"
           f"## From \"What's New in SQLAlchemy 2.1?\" ({urlm.rsplit('/', 1)[-1]})\n\n```rst\n{fb}```\n")
    (out / "sqlalchemy-2.1.md").write_text(doc, encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "benchmark/families/sqlalchemy_ops/docs")
