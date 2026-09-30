"""Result-independent section text. Citations use the numbering of content_static.REFS."""


def P(t):
    return {"type": "p", "text": t}


def H1(t):
    return {"type": "h1", "text": t}


def H2(t):
    return {"type": "h2", "text": t}


def intro(nums):
    return [
        H1("1. Introduction"),
        P("Tool-using AI agents increasingly accumulate reusable procedures: code snippets, workflows and "
          "instructions that worked once and are stored so they can be reused [1], [2], [4], [5]. A skill library "
          "turns one successful trajectory into many cheap future successes. It also turns the library into a "
          "long-lived software artifact, and long-lived software decays. The libraries a skill calls publish "
          "breaking releases, and the rules that govern what the agent may do are revised. A password check written "
          "against the 2017 edition of NIST SP 800-63B, which merely discouraged composition rules and periodic "
          "password changes, violates the 2025 edition, which prohibits both [32], [33]. A Triple-DES encryption "
          "routine that was permitted, though deprecated, in 2023 became disallowed on 1 January 2024 [34], while "
          "decrypting old Triple-DES data remained allowed. A configuration loader written for PyYAML 5 stops working "
          "under PyYAML 6, and the technically easiest repair loads YAML with an unsafe loader that a standing security "
          "rule forbids [40]."),
        P("These examples share a structure that existing continual-learning objectives do not capture. Continual "
          "learning has traditionally treated forgetting as the failure to avoid [25], [26], [27]. When the "
          "environment's rules change, however, some previously correct behaviour must be forgotten: an agent that "
          "faithfully preserves everything it learned will keep performing operations that are no longer authorised. "
          "Preservation of past behaviour is therefore an incomplete objective. A useful adaptation must distinguish "
          "three cases for every component of every stored skill: behaviour that is still valid and must be "
          "**retained** exactly; behaviour that is still required but whose implementation or parameters no longer "
          "work or no longer comply, which must be **repaired**; and behaviour that the current rules prohibit, which "
          "must be **retired** without collateral damage to the rest of the skill."),
        P("Recent work covers parts of this problem. GRASP gates every edit of a bounded skill library on a "
          "regression-aware probe of previously failing and previously passing examples, accepting a candidate only if "
          "it yields a net improvement without new regressions [6]. PolicyBank refines an agent's interpretation of a "
          "fixed but ambiguous policy through feedback [19]. Continual documentation adaptation updates tool "
          "documentation as tools are added, modified or removed [10], and SkillGuard checks the environment "
          "assumptions recorded in skill documents against live conditions [8]. None of these settings contains a "
          "policy that changes over time together with the tools, and none evaluates retirement separately from "
          "accidental loss. The gap matters for regression-gated updating in particular: when a rule changes, the "
          "historical tests that encode the old rule make a correct retirement look like a regression, so a faithful "
          "regression gate rejects exactly the edits that the new rule requires."),
        P("This paper studies continual skill adaptation under real, dated changes to tools and policies. We make "
          "four contributions:"),
        {"type": "list", "ordered": True, "items": [
            "**Problem formulation and metrics.** We define component-level retain/repair/retire labels from "
            "executable validity in each dated state, and outcome metrics that separate accidental loss of still-valid "
            "behaviour from correct retirement of obsolete behaviour, and repair from mere retention.",
            f"**SkillShift, a benchmark of real change events.** Eleven families of reusable skills "
            f"({nums['n_skills']} skills, {nums['n_components']} components, {nums['n_tasks']} downstream tasks) face "
            f"{nums['n_events']} dated events: breaking releases of widely used Python libraries and runtimes [38], [39], "
            "and revisions of the OWASP password-storage guidance [36], NIST SP 800-63B [32], [33], NIST SP 800-131A "
            "[34], FIPS 186-5 [35] and Mozilla's TLS guidelines [37]. Every change document is copied verbatim from its primary source by script, "
            "every behaviour is checked by executing hidden tests against the real library versions, and the split is "
            f"chronological: all {nums['n_test_events']} test events post-date the primary model's knowledge cutoff.",
            "**SkillLedger, a version-indexed evidence method.** Each skill records the grounds of each of its "
            "components (library APIs and verbatim policy sentences) and the runtime and policy under which its "
            "evidence was last validated. On a change it re-executes its evidence, reviews only skills the change can "
            "touch, quarantines evidence whose grounds were superseded, repairs or retires individual components under "
            "a no-regression gate over the remaining evidence, and records retired behaviour as tombstones that are "
            "shown at task time.",
            "**A preregistered empirical comparison** against six baselines requested for this problem (no skills, "
            "a static library, documentation retrieval, version-aware retrieval, complete regeneration and "
            "regression-gated updates) plus a stronger regression-gated variant whose probe tests are first rewritten "
            "from the change documents, with ablations, three independent runs and two further models. We report "
            "where the method helps, where it does not, and what it costs.",
        ]},
    ]


def related():
    return [
        H1("2. Related Work"),
        H2("2.1 Skill libraries and procedural memory"),
        P("Voyager stores executable code skills after self-verification and reuses them for open-ended exploration "
          "[1]. ExpeL distils natural-language insights with add, edit, upvote and downvote operations, removing an "
          "insight when its importance count reaches zero [2]; Reflexion stores episodic self-critiques [3]. Agent "
          "Workflow Memory induces reusable workflows from web trajectories [4], and Memp studies how procedural "
          "memory is built, retrieved and updated, including validation-filtered and reflection-based removal [5]. "
          "GRASP treats self-improvement as a sequence of add, modify or remove edits to a bounded skill library, "
          "each accepted only if (F−F~0~)−(R−R~0~)>0 and R≤R~0~ on a probe of previously failing and "
          "passing items [6]. SkillOps represents skills as typed contracts linked by dependency and compatibility "
          "edges and maintains them with repair and retire actions driven by a health score [7]. The regression tax "
          "study shows that regressions cancel much of the gross gain that skills bring [9]. All of these operate in "
          "environments whose tools and rules do not change over the course of the evaluation."),
        H2("2.2 Tool and API evolution"),
        P("ToolEVO adapts a model to changed APIs through exploration and environment feedback on ToolQA-D [11]. "
          "Continual documentation adaptation (ContDa) rewrites tool documentation as toolsets evolve and reports "
          "stability alongside adaptation [10]. MCPEvol-Bench mutates MCP servers across stages and finds that "
          "additions and modifications hurt agents more than removals [12]; ProEvolve programs graph-structured "
          "environment evolution and observes that memory from a previous version becomes stale or misleading, naming "
          "policy changes as future work [13]. SkillGuard frames skill drift as the violation of environment contracts "
          "extracted from skill documents [8]. For code generation, GitChameleon 2.0 [14], CodeUpdateArena [15], "
          "VersiCode [16], LibEvolutionEval [17] and CodeSync [18] evaluate version-conditioned generation or the "
          "editing of parametric knowledge about API updates. These works concern technical validity only."),
        H2("2.3 Policy-following agents"),
        P("τ-bench evaluates agents that must follow domain policies while using tools [20]. GuardAgent and "
          "ShieldAgent enforce safety policies with knowledge-enabled or verifiable reasoning [21], [22]. PolicyBank "
          "maintains tool-level policy insights and refines the agent's interpretation of an imperfect, fixed policy "
          "specification [19]. In these settings the policy text itself does not change over time, and the tools are "
          "fixed."),
        H2("2.4 Forgetting, unlearning and stale knowledge"),
        P("Continual learning measures forgetting as backward transfer [27] and designs methods to prevent it [25], "
          "[26]. Machine unlearning removes the influence of specific data on a trained model [28], and knowledge "
          "editing changes individual facts in model weights [29], [30]; RippleEdits shows that edited facts often fail "
          "to propagate to their logical consequences [31], an analogue of dependent skills. STALE asks whether agents "
          "recognise that new information invalidates stored memories [23], and AgentCL evaluates plasticity and "
          "stable reuse in language agents [24]. Our setting differs in three ways: the knowledge is a non-parametric, "
          "executable library; its validity changes because of dated external events rather than new observations; "
          "and correct behaviour requires both withdrawing obsolete components and preserving valid ones, measured "
          "separately."),
        H2("2.5 Positioning"),
        P("To our knowledge, no prior work evaluates a reusable skill library under a sequence of real tool and policy "
          "changes, asks for per-component retain/repair/retire decisions, and scores correct retirement separately "
          "from accidental loss. The closest partial overlaps are SkillOps (repair and retire actions, but a static "
          "environment and no policy), SkillGuard (per-skill environment evidence, but no retirement and no policy), "
          "ContDa (tool evolution with a forgetting measure, but documentation rather than skills) and GRASP "
          "(regression-gated editing in a static environment). The question that distinguishes our study is therefore "
          "not whether skills can be edited or checked, but what changes when tool behaviour and policy validity "
          "evolve together over time."),
    ]


def formulation():
    return [
        H1("3. Problem Formulation"),
        P("A **skill** is a module of code with a contract. Its contract lists **components**: independently checkable "
          "behaviours, each stated as a version-neutral requirement (for example, “passwords shorter than the "
          "minimum length required by the current revision are rejected”). A **state** *s* fixes the runtime and "
          "library versions *T(s)* and the policy revisions in force *P(s)*. A **change event** moves a family of "
          "skills from state *s*~k−1~ to *s*~k~ on a documented date, changing *T*, *P* or both, and comes with "
          "its verbatim change document. The agent receives the event and may update its library; it never observes "
          "the hidden tests used for evaluation."),
        P("For each component *c* and state *s*, hidden tests define validity. A component is **valid** in *s* if "
          "its requirement exists in *s* (tests of kind *valid* or *policy* must pass), and **obsolete** if the "
          "rules of *s* prohibit it (an *obsolete* probe passes only if the prohibited behaviour is absent, which "
          "includes refusing with PermissionError). Ground-truth labels for an event are obtained by executing the "
          "correct library of the previous state in the new state: a valid component that still passes is labelled "
          "**retain**, a valid component that fails is labelled **repair**, and an obsolete component whose "
          "behaviour is still present is labelled **retire**. Library changes produce only retain or repair labels, "
          "because in every event of the benchmark a documented replacement exists; policy changes produce all three."),
        P("An adaptation method's outcome is measured by running the hidden tests on its library immediately before "
          "and after adaptation, both in the new state. For valid components this gives four categories: *kept* "
          "(pass→pass), *lost* (pass→fail, an accidental loss caused by the adaptation), *repaired* "
          "(fail→pass) and *unrepaired* (fail→fail). For obsolete components it gives *retired* (behaviour absent "
          "after adaptation) or *persisting*. We report **retention** = kept/(kept+lost), its complement "
          "**accidental loss**, **repair rate** = repaired/(repaired+unrepaired), **retirement rate** = "
          "retired/(retired+persisting) and **library policy violations** (failing standing-policy components). "
          "Retention and retirement are deliberately separate: a method that deletes everything scores perfect "
          "retirement and poor retention, and a method that changes nothing scores the reverse."),
        P("Library tests measure the stored skills; they do not show whether an agent that uses the library behaves "
          "correctly, because the model may reintroduce obsolete behaviour from its own parametric knowledge. Each "
          "family therefore also has downstream tasks, concrete developer requests solved by the agent with its "
          "library in each state. We report **task success** (all hidden task tests pass), **functional success** "
          "(all non-policy tests pass) and **task policy violations** (a policy test fails, for example the agent "
          "performs Triple-DES encryption after 2023 instead of refusing). Adaptation cost is measured in model calls, "
          "tokens, list-price US dollars and wall-clock time."),
    ]


def benchmark(nums, fam_rows, ev_rows):
    return [
        H1("4. The SkillShift Benchmark"),
        H2("4.1 Construction principles"),
        P("Five rules governed construction. (i) *Real, dated events only*: every state transition is an official "
          "library release or policy revision with its published date; no change was invented. (ii) *Verbatim "
          "documentation fetched by script*: the text an agent receives for an event is cut programmatically from the "
          "primary source (release notes and what's-new files in the projects' repositories, the OWASP cheat sheet at "
          "specific commits, Mozilla's guideline JSON files, and the NIST publications), with source URL and fetch date "
          "recorded; one hand-typed excerpt found during development was replaced by its fetched original. (iii) "
          "*Execution in real versions*: every environment is an isolated virtual environment with exact pins, created "
          "with uv using pinned CPython builds (3.9.25 to 3.14.7) and transitive dependencies frozen by date. (iv) "
          "*Realistic epoch-0 code*: the initial skills use the idioms documented at the time (for example "
          "`DataFrame.append` with pandas 1.5, `Engine.execute` with SQLAlchemy 1.4, `yaml.load` without a loader with "
          "PyYAML 5), and each passes all of its initial tests. (v) *Still-valid behaviour is common*: most components "
          "are unaffected by any given event, so that retention is measurable."),
        P("Each family consists of skill modules, the library's own historical tests (visible to agents and written "
          "in the epoch-0 era, including expectations that later become stale), hidden evaluation tests for every "
          "state, reference solutions per state, and downstream tasks with hidden tests and per-state reference "
          "solutions. A validator checks that the epoch-0 code passes all epoch-0 tests and that every state's "
          "reference passes that state's hidden tests; all families validate without problems, both in the "
          "authoring environment and inside the Docker image used for the experiments."),
        {"type": "table", "caption": "Benchmark families. Components are counted once; retain, repair and retire "
         "counts are component-event labels over all events of the family. Events are family-level transitions: "
         "the Python 3.12 release affects two families, so 28 transitions correspond to 27 distinct events.",
         "header": ["Family", "Change", "Skills", "Comp.", "Events", "Tasks", "Retain", "Repair", "Retire", "Python"],
         "widths": [3.0, 1.3, 0.8, 0.8, 0.9, 0.8, 0.9, 0.9, 0.9, 1.4], "rows": fam_rows, "size": 17},
        H2("4.2 Change events"),
        {"type": "figure", "path": nums["fig_timeline"], "px": nums["fig_timeline_px"], "width": 6.3,
         "caption": "The 27 dated change events per family. Circles are library or runtime releases, squares policy "
                    "revisions. The dashed line separates the development and test splits; dotted lines mark the "
                    "knowledge cutoffs of the primary model (A, 1 June 2024) and of the two further models "
                    "(B, 31 August 2025). The Python 3.12 release affects two families."},
        P(f"Table 2 lists the {nums['n_events']} events (Fig. 1 shows them per family). Library events include removals (e.g. `DataFrame.append`, "
          "`np.float_`, `Engine.execute`, `distutils`, `cgi`, `pkg_resources`), signature changes (PyYAML's mandatory "
          "`Loader`), and silent behaviour changes (pandas 3.0 Copy-on-Write makes chained assignment a no-op; "
          "SQLAlchemy 2.0 removes autocommit, so an unmodified delete is rolled back). Policy events include "
          "tightened parameters (OWASP PBKDF2 iterations 310,000→600,000; Argon2id memory 15→19 MiB; NIST "
          "single-factor minimum length 8→15), relaxations that a careful agent must not over-apply, and "
          "prohibitions (NIST SP 800-63B-4's *SHALL NOT* for composition rules and periodic changes, bcrypt for new "
          "hashes only in legacy systems, three-key TDEA encryption and PKCS#1 v1.5 key transport after 2023, DSA "
          "signature generation after FIPS 186-4 was withdrawn, and the removal of Mozilla's Old TLS profile). Two "
          "families are *interaction* families in which both kinds of change affect the same skills. Two events "
          "change nothing that matters (the additive Mozilla 5.7 revision and the deprecation-only cryptography 43.0 "
          "release); they test whether a method leaves valid code alone."),
        {"type": "table", "caption": "Change events in chronological order (dev: on or before 2024-06-30; test: "
         "later). * post-dates the knowledge cutoff of gpt-4.1-mini (2024-06-01); † also post-dates that of the "
         "gpt-5.4 models (2025-08-31). Label counts are component-event labels.",
         "header": ["Date", "Event", "Kind", "Split", "Families", "Retain", "Repair", "Retire"],
         "widths": [1.2, 2.3, 0.8, 0.7, 2.7, 0.8, 0.8, 0.8], "rows": ev_rows, "size": 16, "leftcols": 5},
        H2("4.3 Policies as organisational rules"),
        P("Policy documents are adopted by a deployment, not by nature. Each policy family therefore states a "
          "deployment context that agents see: for example, “the organisation implements every mandatory (SHALL / "
          "SHALL NOT) requirement of the current revision of NIST SP 800-63B; its own earlier rules apply only where "
          "they do not conflict.” The organisation's pre-change choices (for example a letter-and-digit rule and a "
          "365-day expiry, both permitted under the 2017 edition) are specified by us so that the authentic revision "
          "has something to act on; the revisions and their dates are authentic. Where a guideline became effective "
          "later than its publication, we use the effective date: FIPS 186-5 was published on 3 February 2023 but "
          "kept FIPS 186-4 in effect for one year, so DSA signature generation becomes unapproved on 3 February 2024 "
          "[35]."),
        H2("4.4 Chronological split and contamination"),
        P(f"Events on or before 30 June 2024 form the development split ({nums['n_dev_events']} events), used for "
          f"piloting and for all method development; later events form the test split ({nums['n_test_events']} "
          "events), which was run only after the protocol was frozen. Every test event post-dates the knowledge "
          "cutoff of the primary model, and nine also post-date that of the gpt-5.4 models, which limits the extent to "
          "which a model can answer from memorised release notes rather than from the supplied documents."),
    ]


def method():
    algo = {"type": "algo", "title": "Algorithm 1. SkillLedger adaptation of one family at a change event",
            "lines": [
                "**Input:** library L (code, contract, evidence tests), ledger G (grounds, version stamps), event e with "
                "verbatim document D, new state s.",
                "1. For each active skill k: run its evidence tests in s → results r~k~.",
                "2. Review set R ← {k : e is a policy event, or r~k~ has failures, or an API in G~k~ is named in D}.",
                "3. If R = ∅: re-stamp all evidence with s and stop (no model call).",
                "4. One impact call per family: for each k ∈ R and component c, decide retain / repair / retire; for "
                "each test, decide valid / stale (“expected result superseded”). A library event cannot yield retire.",
                "5. For each k ∈ R: if all components are retained and nothing fails, re-stamp and continue.",
                "6.   If every component is retired under a policy event: remove k and write tombstones.",
                "7.   Otherwise quarantine stale evidence (policy event), then request a minimal repair that keeps retained "
                "behaviour, implements retirements (removal or PermissionError) and adds evidence for changed components.",
                "8.   Accept the first attempt that passes all remaining evidence; else the best attempt that improves the "
                "evidence without any regression; else keep the old code, unless it fails to import or (library event) "
                "some of its evidence fails, in which case withhold k.",
                "9.   Write tombstones for retired components; re-stamp accepted evidence with s.",
                "**Task time:** the agent sees active skills and the tombstones (prohibition, source, date).",
            ]}
    return [
        H1("5. SkillLedger"),
        P("SkillLedger is a thin layer over a conventional skill library. It changes what is stored with each skill "
          "and how evidence is used at a change; it does not fine-tune the model."),
        H2("5.1 Version-indexed representation"),
        P("For every skill the ledger stores (a) the contract components; (b) the **grounds** of each component: the "
          "library APIs it relies on, extracted from the code by static analysis, and the sentences of the policy text "
          "or deployment context that require or permit it, quoted verbatim by the model once at setup; (c) for every "
          "evidence test, the component it evidences and whether its expected values derive from an API behaviour, a "
          "policy sentence, both or neither; and (d) a **version stamp**: the runtime, library versions and policy "
          "revision under which the evidence last passed. The stamp is what makes the evidence *version-indexed*: a "
          "passing test is not a timeless fact but a fact about a particular state."),
        H2("5.2 Adaptation"),
        P("Algorithm 1 summarises one adaptation. Steps 1–3 make adaptation selective: for a library event, a skill "
          "whose evidence still passes and whose recorded APIs are not mentioned in the change document is re-stamped "
          "without any model call. Step 4 classifies every component of the remaining skills and every evidence test in "
          "a single call per family, given the change document, the policy text now in force, the ledger and the test "
          "results. Two definitions carry most of the weight. A test is *stale* only if its expected result encodes a "
          "requirement or documented result that no longer holds; a test that fails merely because the code calls a "
          "removed API is still valid evidence. And a library change never makes behaviour unauthorised, so retirement "
          "is available only under policy events."),
        P("The evidence rules in steps 7–8 are where SkillLedger departs from regression gating. Like GRASP, it "
          "never accepts an edit that breaks evidence that still holds. Unlike GRASP, evidence that encodes a "
          "superseded requirement is quarantined rather than treated as a regression anchor, and the repair must add "
          "new evidence for each changed component, grounded in the new text. Under a library event, a test judged "
          "stale is replaced only if the repair supplies a corrected test of the same name; otherwise it stays in force. "
          "A repair that passes all remaining old evidence but fails some of its own new tests is accepted with those "
          "unconfirmed tests dropped and recorded. When no attempt passes everything, the best attempt that improves "
          "the evidence without regressions is kept, and its still-failing tests remain in the suite, so the skill is "
          "reviewed again at the next change."),
        algo,
        H2("5.3 Retirement and tombstones"),
        P("Retiring a component means removing the behaviour or making the corresponding call raise PermissionError; "
          "other behaviour of the same function is kept (for example, Triple-DES decryption of legacy data survives "
          "the retirement of Triple-DES encryption). Deleting a skill is not enough, because the model that uses the "
          "library can reintroduce the behaviour from its own knowledge. Each retirement therefore produces a "
          "**tombstone**: a one-sentence prohibition with its governing source and date, shown in the task prompt "
          "under “retired procedures”. Tombstones are the only part of the method that acts at task time."),
        H2("5.4 Development history"),
        P("The method was revised twice after pilots on development events only, and we report the revisions "
          "because they bear on the interpretation of the results. In the first pilot, SkillLedger repaired fewer "
          "components than the baselines; inspection showed that its impact step marked historical tests stale merely "
          "because they failed after a library change, that it retired skills whose API had been removed, and that "
          "repairs were rejected when the model's own new tests were wrong. The definitions of stale evidence and of "
          "retirement in Section 5.2 and the handling of unconfirmed tests are the resulting revisions. The second "
          "revision replaced “withhold the skill when no attempt passes everything” by the no-regression "
          "partial-repair rule, after the pydantic and SQLAlchemy migrations lost still-valid components that way. "
          "Output-token limits were raised for all methods at the same time. The protocol, code, prompts, benchmark "
          "and configuration were then hashed; the runner refuses to process test events if the hash differs."),
    ]


def setup(nums):
    return [
        H1("6. Experimental Setup"),
        H2("6.1 Methods"),
        P("All methods start from the same epoch-0 library, receive the same deployment context and the same verbatim "
          "change documents, and use the same model. They differ only in what they store and how they update it."),
        {"type": "list", "items": [
            "**No skills:** no library; each task is solved from the task statement and the documentation bundle (the "
            "policy text in force and all change documents so far).",
            "**Static library:** the epoch-0 library, never updated, without documentation.",
            "**Documentation retrieval:** the static library plus the documentation bundle at task time.",
            "**Version-aware retrieval:** at each change, every skill's own tests are executed in the new runtime; a "
            "skill whose tests pass is re-validated for the new version, otherwise it is withheld from retrieval. No "
            "model calls; documentation bundle at task time.",
            "**Complete regeneration:** at each change, every skill of the affected family is rewritten from its "
            "contract, public interface and the documentation bundle, with new tests and one retry.",
            "**Regression-gated (GRASP-style):** for each skill with failing tests (or every skill after a policy "
            "event), two candidate edits are proposed from the change document and test results; a candidate is "
            "accepted only if it fixes previously failing tests without breaking previously passing ones, choosing the "
            "largest net improvement (F−R>0, R≤0), with the historical tests as the probe [6].",
            "**Regression-gated with test refresh:** as above, but each skill's tests are first rewritten by the model "
            "from the change document (every skill, every event), and the gate uses the refreshed tests. This strong "
            "variant was added because a regression gate with stale probes is a natural straw man.",
            "**SkillLedger** (Section 5), and three ablations: without evidence quarantine, without tombstones, and "
            "with every skill reviewed at every event (non-selective).",
        ]},
        P("The four adaptive methods (regeneration, the two gates and SkillLedger) read the change documents while "
          "adapting; at task time they present only the adapted library, plus the tombstones in the case of "
          "SkillLedger. The no-skills and the two retrieval baselines instead place the documentation bundle in the "
          "task prompt. This mirrors how the two families of approaches would be deployed, and it matters for the "
          "interpretation of task-level results (Section 7.6)."),
        H2("6.2 Models, runs and budget"),
        P(f"The primary model is gpt-4.1-mini (knowledge cutoff 1 June 2024), with temperature 0.3 and three "
          f"independent runs of every method and ablation over the full timeline. Robustness checks use gpt-5.4-nano "
          f"(one run, all methods) and gpt-5.4-mini (one run, the four adaptive methods of primary interest); both are "
          f"reasoning models run at low reasoning effort. All model calls, prompts, responses, token counts, list-price "
          f"costs and latencies are logged, and responses are cached so that interrupted runs resume without repeated "
          f"cost. Costs are reported at list prices for the calls each method needs, including calls served from cache "
          f"when an identical prompt had already been issued, so that methods are compared on what they would cost "
          f"alone."),
        H2("6.3 Statistical analysis"),
        P("Outcomes are nested: components within skills within events within families, repeated over runs. We "
          "therefore report 95% cluster-bootstrap intervals, resampling (family, event) clusters with all their "
          "components and runs (2,000 resamples), and paired bootstrap differences between methods on the same "
          "resampled clusters. Primary contrasts and hypotheses were fixed in the protocol before the test split was "
          "run: skill_ledger versus the GRASP-style gate on retirement and task policy violations (H1), accidental loss "
          "versus regeneration and version-aware retrieval and non-inferiority against the refreshed gate with a "
          "5-point margin (H2), repair versus the GRASP-style gate (H3), and adaptation cost (H4). No formal guarantees "
          "are claimed."),
        H2("6.4 Implementation"),
        P("Experiments run in a Docker image (Python 3.12, uv 0.12.21) on a consumer laptop; library environments "
          "are built on demand from the pinned specifications and cached in a volume. Tests run in a sandboxed "
          "subprocess with per-test timeouts and without API keys in the environment. The full artifact contains the "
          "benchmark, the document-fetching scripts, all code, the protocol with its hash, and every raw record from "
          "which the tables and figures are generated."),
    ]
