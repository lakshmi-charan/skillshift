"""Paper figures (static PNG, 300 dpi) generated only from saved summaries.

Encoding: the proposed method in blue, the strongest baseline (regression_refresh) in orange, all other methods
in neutral gray; every figure also carries method names on the axis, so identity never depends on color alone."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#9b9a95"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
                     "legend.frameon": False, "savefig.facecolor": "white", "axes.facecolor": "white"})

LABEL = {"no_skills": "No skills", "static": "Static library", "doc_retrieval": "Doc retrieval",
         "version_aware": "Version-aware retrieval", "regenerate": "Full regeneration",
         "regression_gated": "Regression-gated (GRASP-style)", "regression_refresh": "Regression-gated + test refresh",
         "skill_ledger": "SkillLedger (ours)", "ledger_no_quarantine": "Ours w/o evidence quarantine",
         "ledger_no_tombstones": "Ours w/o tombstones", "ledger_nonselective": "Ours, non-selective review"}


def color(m):
    return BLUE if m == "skill_ledger" or m.startswith("ledger_") and False else (
        BLUE if m == "skill_ledger" else ORANGE if m == "regression_refresh" else GRAY)


def dot_panels(summary, methods, metrics, titles, path, xlabel="Rate", width=7.2):
    """One panel per metric; one row per method; dot = estimate, whisker = 95% cluster-bootstrap CI."""
    n = len(metrics)
    fig, axes = plt.subplots(1, n, figsize=(width, 0.34 * len(methods) + 1.1), sharey=True)
    axes = np.atleast_1d(axes)
    ys = np.arange(len(methods))[::-1]
    for ax, met, title in zip(axes, metrics, titles):
        for y, m in zip(ys, methods):
            v = summary.get(m, {}).get(met)
            if not v or not v.get("n"):
                ax.text(0.02, y, "n/a", va="center", fontsize=7.5, color=INK2)
                continue
            c = color(m)
            ax.plot([v["lo"], v["hi"]], [y, y], color=c, lw=2, solid_capstyle="round")
            ax.plot([v["mean"]], [y], "o", ms=6.5, color=c, mec="white", mew=1.5, zorder=3)
        ax.set_xlim(-0.03, 1.03)
        import textwrap
        ax.set_title("\n".join(textwrap.wrap(title, 22)), fontsize=9, color=INK)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(ys, [LABEL.get(m, m) for m in methods], fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def cost_scatter(summary, methods, metric, path, ylabel):
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    pts = []
    for m in methods:
        r = summary.get(m, {})
        v = r.get(metric)
        if not v or not v.get("n"):
            continue
        x = 1000 * r.get("adapt_cost_per_event", 0.0)
        c = color(m)
        ax.plot([x, x], [v["lo"], v["hi"]], color=c, lw=1.5, alpha=0.8)
        ax.plot([x], [v["mean"]], "o", ms=7, color=c, mec="white", mew=1.5, zorder=3)
        pts.append([x, v["mean"], LABEL.get(m, m), c])
    merged = []   # identical points share one label
    for p in pts:
        for q in merged:
            if abs(q[0] - p[0]) < 0.3 and abs(q[1] - p[1]) < 0.01:
                q[2] += " / " + p[2]
                break
        else:
            merged.append(list(p))
    merged.sort(key=lambda p: p[1])
    placed = []
    xr = max(p[0] for p in merged) or 1
    for x, y, lab, c in merged:
        ly = y
        for px, py in placed:
            if abs(px - x) < 0.35 * xr and abs(py - ly) < 0.045:
                ly = py + 0.045
        placed.append((x, ly))
        ax.annotate(lab, (x, y), xytext=(x + 0.02 * xr, ly), textcoords="data", fontsize=7, va="center",
                    color=INK if c != GRAY else INK2)
    ax.set_xlabel("Adaptation cost per change event (USD x 1000, list prices)")
    ax.set_ylabel(ylabel)
    ax.set_ylim(-0.03, 1.08)
    ax.set_xlim(-0.05 * xr, 1.45 * xr)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def outcome_stack(comp_rows, methods, path, split="test"):
    """Composition of component outcomes after adaptation (share of labelled components), per method."""
    cats = [("kept", "Kept (still valid)", "#9fc4ee"), ("repaired", "Repaired", BLUE),
            ("retired", "Correctly retired", "#1baf7a"), ("lost", "Lost (accidental)", ORANGE),
            ("unrepaired", "Not repaired", "#c9c8c2"), ("persisting", "Obsolete persists", "#e34948")]
    fig, ax = plt.subplots(figsize=(7.2, 0.36 * len(methods) + 1.3))
    ys = np.arange(len(methods))[::-1]
    for y, m in zip(ys, methods):
        rows = [r for r in comp_rows if r["method"] == m and r["split"] == split]
        n = len(rows) or 1
        left = 0.0
        for key, lab, col in cats:
            w = sum(1 for r in rows if r["cat"] == key) / n
            if w > 0:
                ax.barh(y, w - 0.002, left=left, height=0.62, color=col)
            left += w
    from matplotlib.patches import Patch
    handles = [Patch(color=col, label=lab) for _, lab, col in cats]
    ax.set_yticks(ys, [LABEL.get(m, m) for m in methods], fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_xlabel(f"Share of component-event outcomes ({split} split)")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=handles, ncol=3, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, -0.22))
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
