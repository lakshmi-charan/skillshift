"""Static (result-independent) parts of the paper. Benchmark tables are generated from the benchmark files."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from sa import bench  # noqa: E402

TITLE = ("Continual Skill Adaptation for AI Agents Under Changing Tools and Policies: "
         "Selective Retention, Repair, and Retirement")
AUTHORS = ["Lakshmi Charan Lingisetty",
           "[Affiliation: Department / Lab (optional), Institution or “Independent Researcher”, City, Country]",
           "lingisettycharan123@gmail.com"]

FAM_ORDER = ["yaml_config", "sqlalchemy_ops", "pandas_ops", "numpy_ops", "pydantic_models", "stdlib_compat",
             "packaging_http", "password_storage", "nist_passwords", "tls_config", "legacy_crypto"]
FAM_NAME = {"yaml_config": "YAML configuration", "sqlalchemy_ops": "SQL access (SQLAlchemy)",
            "pandas_ops": "Data frames (pandas)", "numpy_ops": "Numerics (NumPy)", "pydantic_models": "Data models (pydantic)",
            "stdlib_compat": "Python standard library", "packaging_http": "HTTP, schemas, packaging",
            "password_storage": "Password storage (OWASP)", "nist_passwords": "Password verification (NIST SP 800-63B)",
            "tls_config": "TLS configuration (Mozilla + CPython)", "legacy_crypto": "Legacy cryptography (NIST + pyca)"}
DOMAIN = {"tool": "Tool", "policy": "Policy", "interaction": "Tool + policy"}


def labels(path):
    return json.loads(Path(path).read_text())


def family_table(label_rows):
    rows = []
    tot = Counter()
    for f in FAM_ORDER:
        fam = bench.family(f)
        n_sk = len(fam["skills"])
        n_comp = sum(len(s["components"]) for s in fam["skills"])
        n_ev = len(fam["states"]) - 1
        c = Counter(r["label"] for r in label_rows if r["family"] == f)
        n_task = len(bench.tasks(f))
        pys = sorted({str(s["env"]["python"]) for s in fam["states"]})
        rows.append([FAM_NAME[f], DOMAIN[fam["domain"]], n_sk, n_comp, n_ev, n_task, c["retain"], c["repair"],
                     c["retire"], ", ".join(pys)])
        for k, v in (("sk", n_sk), ("comp", n_comp), ("ev", n_ev), ("task", n_task), ("retain", c["retain"]),
                     ("repair", c["repair"]), ("retire", c["retire"])):
            tot[k] += v
    rows.append(["**Total**", "", tot["sk"], tot["comp"], tot["ev"], tot["task"], tot["retain"], tot["repair"],
                 tot["retire"], ""])
    return rows, tot


def event_table(label_rows, cutoff_a="2024-06-01", cutoff_b="2025-08-31"):
    ev = defaultdict(lambda: {"fams": set(), "c": Counter()})
    meta = {}
    for f in FAM_ORDER:
        for st in bench.family(f)["states"][1:]:
            e = st["event"]
            meta[e["id"]] = (st["date"], e["kind"], e["title"])
            ev[e["id"]]["fams"].add(FAM_NAME[f].split(" (")[0])
    for r in label_rows:
        ev[r["event"]]["c"][r["label"]] += 1
    rows = []
    for eid, (date, kind, title) in sorted(meta.items(), key=lambda kv: (kv[1][0], kv[0])):
        c = ev[eid]["c"]
        split = "dev" if date <= "2024-06-30" else "test"
        post = "†" if date > cutoff_b else ("*" if date > cutoff_a else "")
        rows.append([date, eid + post, kind, split, "; ".join(sorted(ev[eid]["fams"])), c["retain"], c["repair"],
                     c["retire"]])
    return rows


REFS = [
    # 1-9 skills / memory / self-improvement
    'G. Wang, Y. Xie, Y. Jiang, A. Mandlekar, C. Xiao, Y. Zhu, et al., "Voyager: An open-ended embodied agent with large language models," *Transactions on Machine Learning Research*, 2024. arXiv:2305.16291.',
    'A. Zhao, D. Huang, Q. Xu, M. Lin, Y.-J. Liu, and G. Huang, "ExpeL: LLM agents are experiential learners," in *Proc. AAAI Conf. Artificial Intelligence*, 2024. arXiv:2308.10144.',
    'N. Shinn, F. Cassano, A. Gopinath, K. Narasimhan, and S. Yao, "Reflexion: Language agents with verbal reinforcement learning," in *Advances in Neural Information Processing Systems 36*, 2023.',
    'Z. Z. Wang, J. Mao, D. Fried, and G. Neubig, "Agent workflow memory," in *Proc. Int. Conf. Machine Learning (ICML)*, 2025. arXiv:2409.07429.',
    'R. Fang, Y. Liang, X. Wang, J. Wu, S. Qiao, P. Xie, et al., "Memp: Exploring agent procedural memory," in *Findings of the Association for Computational Linguistics: ACL 2026*, pp. 17490–17502, 2026. arXiv:2508.06433.',
    'J. Moll, J.-P. Corbeil, J. Pan, M. Hadamitzky, D. Rueckert, L. Adams, et al., "GRASP: Gated regression-aware skill proposer for self-improving LLM agents," arXiv:2605.29668, 2026.',
    'H. Pu, X. Song, and L. Zhao, "SkillOps: Managing LLM agent skill libraries as self-maintaining software ecosystems," arXiv:2605.13716, 2026.',
    'L. Fan, Y. Tian, Z. Li, and Z. Lu, "Skill drift is contract violation: Proactive maintenance for LLM agent skill libraries," arXiv:2605.10990, 2026.',
    'D. Tank and B. Nama, "The regression tax: Decomposing why skills help—and hurt—LLM agents," arXiv:2607.22520, 2026.',
    # 10-18 tool/API evolution
    'B. Wu, E. Meij, and E. Yilmaz, "Beyond static toolsets: Self-evolving LLM tool agents via continual documentation adaptation," in *Findings of the Association for Computational Linguistics: ACL 2026*, pp. 21519–21539, 2026.',
    'G. Chen, Z. Zhang, X. Cong, F. Guo, Y. Wu, Y. Lin, et al., "Learning evolving tools for large language models," in *Proc. Int. Conf. Learning Representations (ICLR)*, 2025. arXiv:2410.06617.',
    'H. Liu, K. Hu, J. Liao, Q. Wang, P. Qian, Y. Zhai, et al., "MCPEvol-Bench: Benchmarking LLM agent performance across dynamic evolutions of MCP servers," arXiv:2607.14642, 2026.',
    'G. Li, Y. Xie, Y. Liu, Z. Dong, X. Pan, T. Zheng, et al., "The world won’t stay still: Programmable evolution for agent benchmarks," arXiv:2603.05910, 2026.',
    'D. Misra, N. Islah, V. May, B. Rauby, Z. Wang, J. Gehring, et al., "GitChameleon 2.0: Evaluating AI code generation against Python library version incompatibilities," in *Proc. 64th Annual Meeting of the Association for Computational Linguistics (ACL)*, pp. 46792–46831, 2026. arXiv:2507.12367.',
    'Z. L. Liu, S. Pandit, X. Ye, E. Choi, and G. Durrett, "CodeUpdateArena: Benchmarking knowledge editing on API updates," arXiv:2407.06249, 2024.',
    'T. Wu, W. Wu, X. Wang, K. Xu, S. Ma, B. Jiang, et al., "VersiCode: Towards version-controllable code generation," arXiv:2406.07411, 2024.',
    'S. Kuhar, W. U. Ahmad, Z. Wang, N. Jain, H. Qian, B. Ray, et al., "LibEvolutionEval: A benchmark and study for version-specific code generation," in *Proc. NAACL*, pp. 6826–6840, 2025.',
    'C. Wang, Z. Chu, Z. Cheng, X. Yang, K. Qiu, Y. Wan, et al., "CodeSync: Synchronizing large language models with dynamic code evolution at scale," in *Proc. ICML*, PMLR 267, pp. 62672–62700, 2025.',
    # 19-24 policy / guardrails / staleness
    'J. Choi, J. Yoon, L. T. Le, S. Jha, and T. Pfister, "PolicyBank: Evolving policy understanding for LLM agents," arXiv:2604.15505, 2026.',
    'S. Yao, N. Shinn, P. Razavi, and K. Narasimhan, "τ-bench: A benchmark for tool-agent-user interaction in real-world domains," in *Proc. ICLR*, 2025.',
    'Z. Xiang, L. Zheng, Y. Li, J. Hong, Q. Li, H. Xie, et al., "GuardAgent: Safeguard LLM agents via knowledge-enabled reasoning," in *Proc. ICML*, 2025.',
    'Z. Chen, M. Kang, and B. Li, "ShieldAgent: Shielding agents via verifiable safety policy reasoning," in *Proc. ICML*, PMLR 267, pp. 8313–8344, 2025.',
    'H. Chao, Y. Bai, R. Sheng, T. Li, and Y. Sun, "STALE: Can LLM agents know when their memories are no longer valid?," arXiv:2605.06527, 2026.',
    'Y. Shu, B. Jiménez Gutiérrez, S. P. Jonnalagedda, Y. Yao, H. Sun, and Y. Su, "AgentCL: Toward rigorous evaluation of continual learning in language agents," arXiv:2606.02461, 2026.',
    # 25-31 continual learning / unlearning / editing
    'J. Kirkpatrick, R. Pascanu, N. Rabinowitz, J. Veness, G. Desjardins, et al., "Overcoming catastrophic forgetting in neural networks," *Proc. National Academy of Sciences*, vol. 114, no. 13, pp. 3521–3526, 2017.',
    'L. Wang, X. Zhang, H. Su, and J. Zhu, "A comprehensive survey of continual learning: Theory, method and application," *IEEE Trans. Pattern Analysis and Machine Intelligence*, 2024, doi: 10.1109/TPAMI.2024.3367329.',
    'D. Lopez-Paz and M. Ranzato, "Gradient episodic memory for continual learning," in *Advances in Neural Information Processing Systems 30*, pp. 6467–6476, 2017.',
    'L. Bourtoule, V. Chandrasekaran, C. A. Choquette-Choo, H. Jia, A. Travers, B. Zhang, et al., "Machine unlearning," in *Proc. IEEE Symp. Security and Privacy*, pp. 141–159, 2021, doi: 10.1109/SP40001.2021.00019.',
    'K. Meng, D. Bau, A. Andonian, and Y. Belinkov, "Locating and editing factual associations in GPT," in *Advances in Neural Information Processing Systems 35*, 2022.',
    'K. Meng, A. Sen Sharma, A. Andonian, Y. Belinkov, and D. Bau, "Mass-editing memory in a transformer," in *Proc. ICLR*, 2023.',
    'R. Cohen, E. Biran, O. Yoran, A. Globerson, and M. Geva, "Evaluating the ripple effects of knowledge editing in language models," *Trans. Association for Computational Linguistics*, vol. 12, pp. 283–298, 2024.',
    # 32-39 primary sources for events
    'National Institute of Standards and Technology, "Digital identity guidelines: Authentication and lifecycle management," NIST SP 800-63B, June 2017 (updated Mar. 2, 2020), doi: 10.6028/NIST.SP.800-63b.',
    'National Institute of Standards and Technology, "Digital identity guidelines: Authentication and authenticator management," NIST SP 800-63B-4, July 2025, doi: 10.6028/NIST.SP.800-63b-4.',
    'E. Barker and A. Roginsky, "Transitioning the use of cryptographic algorithms and key lengths," NIST SP 800-131A Rev. 2, Mar. 2019, doi: 10.6028/NIST.SP.800-131Ar2.',
    'National Institute of Standards and Technology, "Digital signature standard (DSS)," FIPS PUB 186-5, Feb. 2023, doi: 10.6028/NIST.FIPS.186-5.',
    'OWASP Foundation, "Password storage cheat sheet," OWASP Cheat Sheet Series, revisions 728bbcd (2021-03-17) through c3c1952 (2026-05-12), https://github.com/OWASP/CheatSheetSeries (CC BY-SA 4.0).',
    'Mozilla, "Server side TLS guidelines," versions 5.6–6.0, mozilla/ssl-config-generator, https://github.com/mozilla/ssl-config-generator (MPL-2.0).',
    'Python Software Foundation, "What’s new in Python 3.12 / 3.13 / 3.14," https://docs.python.org/3/whatsnew/ (release dates 2023-10-02, 2024-10-07, 2025-10-07).',
    'Release notes of PyYAML 6.0, SQLAlchemy 2.0 and 2.1, pandas 2.0 and 3.0, NumPy 2.0, 2.3, 2.4 and 2.5, pydantic 2.0, httpx 0.28, marshmallow 4.0, setuptools 82 and cryptography 43.0 (official repositories; exact URLs and fetch scripts in the artifact).',
    # 40
    'PyCQA, "Bandit: a security linter for Python," https://github.com/PyCQA/bandit.',
]
