# SkillShift: continual skill adaptation under real tool and policy changes

Code, benchmark, frozen protocol and raw results for the paper

> **Continual Skill Adaptation for AI Agents Under Changing Tools and Policies: Selective Retention, Repair, and Retirement**
> Lakshmi Charan Lingisetty, 2026.

AI agents increasingly store reusable *skills*: small code modules that worked once and are reused later. When the
libraries those skills call publish breaking releases, or the rules the agent must follow are revised, the library
has to change. A correct update keeps still-valid behaviour (**retention**), fixes behaviour that broke
(**repair**) and removes behaviour that the new rules prohibit (**retirement**). This repository contains:

- **SkillShift**, a benchmark of 11 skill families (60 skills, 236 components, 40 downstream tasks) exposed to
  **27 real, dated change events**: breaking releases of Python libraries and runtimes, and revisions of OWASP,
  NIST and Mozilla security guidance. Every change document is copied verbatim from its primary source by script,
  every behaviour is checked by executing hidden tests in pinned environments, and the split is chronological.
- **SkillLedger**, a method that stores version-stamped evidence for each skill component, quarantines evidence whose
  grounds were superseded, and repairs or retires individual components under a no-regression gate.
- **Seven baselines** (no skills, static library, documentation retrieval, version-aware retrieval, full
  regeneration, a GRASP-style regression gate, and a regression gate with refreshed tests), three ablations and a
  post-hoc variant.
- The **frozen study protocol**, all **run records** of the main study, and the scripts that regenerate every number,
  table and figure of the paper.

## Main results

Test split (16 events after the primary model's knowledge cutoff), gpt-4.1-mini, three runs; rates in %.

| Method | Retention | Repair | Retirement | Task success | Task policy violations | Cost / event (USD) |
|---|---:|---:|---:|---:|---:|---:|
| No skills | – | – | – | 67.8 | 48.1 | 0.0000 |
| Static library | 100.0 | 0.0 | 0.0 | 22.2 | 94.4 | 0.0000 |
| Documentation retrieval | 100.0 | 0.0 | 0.0 | 52.8 | 59.3 | 0.0000 |
| Version-aware retrieval | 80.7 | 0.0 | 0.0 | 70.6 | 61.1 | 0.0000 |
| Full regeneration | 91.2 | 30.8 | 77.8 | 65.6 | 44.4 | 0.0317 |
| Regression-gated (GRASP-style) | 100.0 | 38.7 | 0.0 | 52.8 | 94.4 | 0.0110 |
| Regression-gated + test refresh | 99.5 | 49.8 | 47.2 | 60.0 | 61.1 | 0.0239 |
| **SkillLedger** | 82.9 | 42.8 | 61.1 | 64.4 | 55.6 | 0.0218 |

In short:

- A regression gate anchored on historical tests never retired prohibited behaviour, with any of the three models.
- SkillLedger retired more of it after policy changes and reduced downstream policy violations.
- A gate whose tests are first refreshed from the change documents matched SkillLedger on retirement at equal cost,
  and kept still-valid behaviour better.
- SkillLedger's clear advantage is repair after policy changes.
- Its losses came from withholding skills whose own historical tests kept failing, often because the tests
  called removed APIs.

Confidence intervals, the preregistered hypothesis tests, two further models (gpt-5.4-nano, gpt-5.4-mini) and all
negative findings are in the paper. The numbers above come from `paper/results/results.json`.

## Repository layout

```
.
├── benchmark/
│   ├── families/<family>/   family.yaml (states, dated events, deployment context), skills/, visible/ (historical
│   │                        tests), hidden/ (evaluation tests per state), refs/ (reference solutions per state),
│   │                        tasks/ (downstream tasks), docs/ (verbatim change documents)
│   ├── tools/               scripts that fetch or cut every change document from its primary source
│   └── AUTHORING.md         how a family is built and validated
├── sa/                      experiment harness
│   ├── envs.py              isolated environments per state (uv, pinned CPython and packages)
│   ├── execute.py           sandboxed test execution (child_runner.py: dependency-free test runner)
│   ├── bench.py             benchmark access, validation, executable ground-truth labels
│   ├── methods.py           all methods, ablations and the post-hoc variant
│   ├── prompts.py           every prompt
│   ├── llm.py               model client: response cache, cost ledger, hard budget cap
│   ├── runner.py            runs one (model, method, run, family) through its dated states
│   ├── analysis.py          metrics and cluster-bootstrap intervals
│   └── figures.py           figure styles
├── run.py                   command-line entry point (check, validate, labels, pilot, freeze, main, analyze)
├── config.yaml              models, prices, budget cap, families, methods
├── PROTOCOL.md              study protocol and hypotheses, frozen before the test split, plus Amendment A1
├── runs_main/               run records of the main study (see "Run records")
├── analysis/
│   ├── audit_responses.py   audit of structured-output parse failures in the recorded responses
│   ├── verify_digest.py     checks this code against the protocol digests recorded during the study
│   ├── rebuild_cache.py     rebuilds the response cache from the logged calls (raw records archive)
│   ├── frozen_manifest.json, asrun_manifest.json   per-file hashes of the code as frozen and as run
│   └── frozen_code/         the frozen versions of the files changed by Amendment A1
├── paper/                   scripts that regenerate the paper's numbers, tables, figures and .docx
│   ├── results/             results.json (every metric, interval and contrast) and evidence_index.json
│   └── figures/             the paper's figures
├── sources/                 local copies of primary sources used by benchmark/tools (see sources/README.md)
├── tests/                   offline end-to-end tests with a scripted model (no API calls)
├── Dockerfile, requirements.txt, .env.example
└── LICENSE, CITATION.cff
```

## Quick start: reproduce the paper's numbers (no API key needed)

Requires Python 3.10+ and, for the .docx, Node.js 18+.

```sh
pip install -r requirements.txt
python paper/results_gen.py runs_main paper/out test   # every metric, interval and contrast -> paper/out/results.json
python analysis/verify_digest.py                        # published code vs. the digests recorded during the study
cd paper && npm install && cd ..
sh paper/make_paper.sh runs_main                        # tables, figures and paper/out/SkillAdapt_paper.docx
```

## Full reproduction (new model calls)

The experiments run in Docker; library versions are installed on demand into a cache volume.

```sh
docker build -t skilladapt .
docker volume create sa-cache
cp .env.example .env            # then put your API key in .env (never commit it)
```

All stages are resumable, responses are cached, and `config.yaml` sets a hard spending cap
(`max_total_cost_usd`). The main study cost about US$28.50 at list prices.

```sh
R="docker run --rm -v $PWD:/work -v sa-cache:/cache skilladapt python run.py"
$R check          # environment and key check
$R validate       # every family's reference solutions pass their hidden tests in the pinned environments
$R labels         # executable ground-truth retain / repair / retire labels
$R pilot          # development split only
$R freeze         # protocol digest; test-split events refuse to run if code, benchmark, config or protocol change
$R main --model gpt-4.1-mini --runs 0,1,2 --ablations
$R main --model gpt-5.4-nano --runs 0
$R main --model gpt-5.4-mini --runs 0 --methods regenerate,regression_gated,regression_refresh,skill_ledger
# post-hoc Amendment A1 (PROTOCOL.md): only the post-hoc variant may run under --posthoc
$R main --posthoc --model gpt-4.1-mini --runs 0,1,2 --methods skill_ledger_robust
$R main --posthoc --model gpt-5.4-nano --runs 0 --methods skill_ledger_robust
$R main --posthoc --model gpt-5.4-mini --runs 0 --methods skill_ledger_robust
```

With the raw records archive (see "Run records") extracted and the cache rebuilt, the same commands replay every
model response and make no API calls. `python tests/test_pipeline.py` runs every method end to end with a scripted
model.

## Run records

`runs_main/` holds, for every model, method, run and family, `records.json` (hidden-test outcomes of every component
before and after each adaptation, downstream task solutions and their outcomes, adaptation calls, tokens, cost and
time), `usage.json` (per-call accounting), `done.json`, and for the post-hoc variant `parse_log.json`. Top-level files:

| File | Contents |
|---|---|
| `labels.json` | ground-truth retain / repair / retire labels per component and event |
| `protocol_freeze.json` | digest taken before the first test-split event |
| `posthoc_runs.json` | digest and log of the post-hoc Amendment A1 runs |
| `cost_ledger.json` | spend by model and stage |
| `response_audit.json` | parse failures of structured model output (paper, Table 9) |

**Raw records archive.** The prompts and responses of every model call (`calls.jsonl`, 12,612 calls) and the
library snapshot after every state (`library_<state>.json`) are too large for the repository and are published as a
separate archive, `skillshift_raw_records.zip` (43.8 MB; SHA-256
`781ca809e8cf1aec754447a1df7c4bc8854738d881ce34aef9621c90422dcacf`), attached to
[release v1.0](https://github.com/lakshmi-charan/skillshift/releases/tag/v1.0). To use it:

```sh
curl -LO https://github.com/lakshmi-charan/skillshift/releases/download/v1.0/skillshift_raw_records.zip
unzip skillshift_raw_records.zip          # at the repository root; fills in runs_main/
python analysis/rebuild_cache.py          # rebuilds the response cache from the logged calls
```

With the cache rebuilt, every `run.py main ...` command above replays the study from the recorded responses without
any API call.

## Protocol integrity

The protocol, hypotheses, code, prompts, benchmark and configuration were hashed before any test-split event was run
(`runs_main/protocol_freeze.json`), and the runner refuses to process test events if the digest differs. One
amendment was made afterwards and is labelled as post hoc everywhere (Amendment A1 in `PROTOCOL.md`). For
publication, four lines that set default local paths in three document-fetching scripts and in
`benchmark/AUTHORING.md` were changed to point to the bundled `sources/` folder; these files are not used by any
experiment. `python analysis/verify_digest.py` compares every file with the versions that were frozen and run, and
lists exactly these differences.

## Adding a family

See `benchmark/AUTHORING.md`. A family needs dated states with pinned environments, verbatim change documents
produced by a script, historical tests, hidden tests per state, reference solutions per state and downstream tasks.
`python -m sa.cli_bench validate <family>` must pass before a family is used.

## Citation

If you use SkillShift or SkillLedger, please cite the paper (see `CITATION.cff`).

## Licence

Code, tests and run records: MIT (see `LICENSE`). Third-party excerpts in `sources/` and `benchmark/families/*/docs/`
remain under their original terms (NIST: public domain; OWASP Cheat Sheet Series: CC BY-SA 4.0; Mozilla TLS
guidelines: MPL-2.0; project release notes: their projects' licences).
