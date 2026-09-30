# Study protocol (frozen before any test-split event is run)

## Question
When tools and operating policies change, can an agent keep still-valid skills, repair broken ones, and retire
behaviour that is no longer permitted, and does version-indexed evidence help compared with regression-gated
updating and other baselines?

## Hypotheses (test split; primary contrast skill_ledger vs regression_gated, key secondary vs regression_refresh)
H1 (retirement): after policy changes, obsolete behaviour persists less often with skill_ledger than with
   regression_gated (library obsolete persistence; downstream task policy violations).
H2 (retention): skill_ledger's accidental-loss rate is lower than regenerate's and version_aware's. Against
   regression_refresh we test non-inferiority with a 5-point margin (the development pilot suggests it may fail).
H3 (repair): after tool changes, skill_ledger's repair rate is at least that of regression_gated.
H4 (cost): skill_ledger's adaptation cost per event is lower than regenerate's and regression_refresh's.
Evidence against the contribution: regression_refresh matching skill_ledger on H1 and task policy violations at
equal or lower cost; or no difference between skill_ledger and its no-quarantine / no-tombstone ablations.

## Design
* Benchmark: 11 families, 27 real dated events: 11 development (on or before 2024-06-30), 16 test.
  All test events post-date the knowledge cutoff of gpt-4.1-mini (2024-06-01); 9 also post-date that of the
  gpt-5.4 models (2025-08-31).
* Ground truth: executable hidden tests per state; retain/repair/retire labels from running the previous state's
  reference code in the new state. Agents never see hidden tests, reference code or labels.
* Methods: no_skills, static, doc_retrieval, version_aware, regenerate, regression_gated, regression_refresh,
  skill_ledger; ablations ledger_no_quarantine, ledger_no_tombstones, ledger_nonselective.
  All methods receive the same deployment context and the same verbatim change documents.
* Models and runs: gpt-4.1-mini, 3 independent runs, all methods and ablations (primary analysis);
  gpt-5.4-nano, 1 run, all methods; gpt-5.4-mini, 1 run, regenerate / regression_gated / regression_refresh /
  skill_ledger. Temperature 0.3 (reasoning models: provider default sampling, reasoning effort "low").
* Metrics: retention / accidental loss / repair / retirement / obsolete persistence / policy violations (library);
  task success / functional success / policy violations (downstream); adaptation calls, tokens, USD, seconds.
* Uncertainty: 95% cluster-bootstrap intervals over (family, event) clusters; paired bootstrap differences for
  method contrasts. No formal guarantees are claimed.

## Development history (development-split events only; recorded for transparency)
Pilot 1 (all methods): skill_ledger repaired less than baselines. Diagnosed causes: (a) the impact step marked
historical tests stale merely because they failed after a library change; (b) it retired skills whose API was
removed; (c) repairs were rejected when the model's own new tests were wrong. Revisions: precise definition of stale
evidence; library changes cannot trigger retirement; unconfirmed new tests may be dropped if all retained old
evidence passes. Pilot 2: added the legacy_crypto family (first development retirement cases). Remaining loss from
discarding partially repaired skills; revision: accept the best attempt that improves on the retained evidence
without regressions. Pilot 3 confirmed the revision. Output-token limits were raised for all methods alike.
Code, prompts, benchmark, configuration and this protocol are hashed in runs_main/protocol_freeze.json before the
first test-split run; the main runner refuses to run test events if the hash differs.

## Amendment A1 (post hoc; added 2026-09-30 after all frozen test runs had finished and been analysed)
Frozen protocol hash: f67be527958fab36b048d802d31e51aea9e15623f1e4d5bf98ccbdb0bd78c00f (488 files). All frozen
results stay the primary results and are reported unchanged.
Observation: the frozen skill_ledger treats an impact response that is not valid JSON as an empty decision set, so
every component is retained (fail-open). Malformed responses (typically one missing closing brace) occurred in
5/84 impact calls for gpt-4.1-mini, 1/28 for gpt-5.4-nano and 9/28 for gpt-5.4-mini; for gpt-5.4-mini this
alone removed every legacy_crypto retirement.
Variant: skill_ledger_robust = skill_ledger + a structural repair of the impact response (close unbalanced
brackets, drop trailing commas) + one re-ask if it still cannot be parsed. It shares skill_ledger's response cache
(same cache salt), so every call with an unchanged prompt returns the identical recorded response; trajectories
diverge only after a recovered parse. Run with `run.py main --posthoc --methods skill_ledger_robust`, which refuses
any other method and logs the amended hash to runs_main/posthoc_runs.json. It is reported separately and labelled
post hoc; it is not used to test H1-H4.
