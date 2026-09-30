"""Fig. 1: timeline of the 27 dated change events per family (generated from the benchmark files)."""
import sys
from datetime import date
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sa import bench
from content_static import FAM_ORDER, FAM_NAME

BLUE, ORANGE, INK2, GRID = "#2a78d6", "#eb6834", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2})


def main(out):
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    ys = list(range(len(FAM_ORDER)))[::-1]
    for y, f in zip(ys, FAM_ORDER):
        fam = bench.family(f)
        for st in fam["states"][1:]:
            d = date.fromisoformat(str(st["date"]))
            k = st["event"]["kind"]
            ax.plot([d], [y], marker="o" if k == "tool" else "s", ms=6.5,
                    color=BLUE if k == "tool" else ORANGE, mec="white", mew=0.8, zorder=3)
    for x, lab in ((date(2024, 6, 30), "dev | test split (2024-06-30)"),):
        ax.axvline(x, color="#0b0b0b", lw=1.0, ls="--")
        ax.text(x, len(FAM_ORDER) - 0.35, "  " + lab, fontsize=7.5, va="bottom")
    for x, lab in ((date(2024, 6, 1), "cutoff A"), (date(2025, 8, 31), "cutoff B")):
        ax.axvline(x, color=INK2, lw=0.8, ls=":")
        ax.text(x, -0.9, lab, fontsize=7, ha="center", color=INK2)
    ax.set_yticks(ys, [FAM_NAME[f] for f in FAM_ORDER])
    ax.set_ylim(-1.2, len(FAM_ORDER) - 0.1)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="x", color=GRID)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", ls="", color=BLUE, ms=6.5, label="library / runtime release"),
         Line2D([], [], marker="s", ls="", color=ORANGE, ms=6.5, label="policy revision")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.35, -0.1), ncol=2, frameon=False, fontsize=7.5)
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main(sys.argv[1])
