#!/bin/sh
# Regenerate every table, figure and number of the paper from the run records, then render the .docx.
# Usage (from the repository root): sh paper/make_paper.sh [runs_dir]
# Needs Python with numpy, matplotlib, pillow and PyYAML, and Node.js (run `npm install` in paper/ once).
set -e
RUNS=${1:-runs_main}
HERE=$(dirname "$0")
OUT="$HERE/out"
mkdir -p "$OUT"
python "$HERE/results_gen.py" "$RUNS" "$OUT" test
python "$HERE/fig_timeline.py" "$OUT/fig_timeline.png"
python "$HERE/assemble.py" "$RUNS" "$OUT" "$OUT/content.json"
node "$HERE/build.js" "$OUT/content.json" "$OUT/SkillAdapt_paper.docx"
echo "done: $OUT/SkillAdapt_paper.docx"
