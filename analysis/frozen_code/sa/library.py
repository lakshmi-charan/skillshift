"""Skill library state shared by all methods, plus helpers to run an agent's own (visible) tests."""
import ast
import copy
import re

from . import bench, execute


def initial_library(fid):
    """The epoch-0 library of a family: code, contract (purpose + components) and historical tests."""
    fam = bench.family(fid)
    lib = {}
    for sk in fam["skills"]:
        lib[sk["id"]] = {
            "id": sk["id"], "family": fid, "purpose": sk.get("purpose", ""),
            "components": [dict(c) for c in sk["components"]],
            "code": bench.read(fid, sk["file"]),
            "tests": bench.read(fid, sk["visible_tests"]),
            "status": "active",           # active | retired | quarantined
            "history": [],
        }
    return lib


def clone(lib):
    return copy.deepcopy(lib)


def code_map(lib):
    """skill id -> code for skills that are importable (active); retired/quarantined skills are absent."""
    return {k: (v["code"] if v["status"] == "active" else None) for k, v in lib.items()}


def run_agent_tests(fid, sid, lib, kid, code=None, tests=None):
    """Run a skill's visible tests (or the given test source) in state sid, with the library's other skills
    importable. Returns list of case dicts (name, component, passed, error)."""
    rec = lib[kid]
    code = rec["code"] if code is None else code
    tests = rec["tests"] if tests is None else tests
    if not tests or "@case" not in tests:
        return {"cases": [], "fatal": None}
    libmap = code_map(lib)
    libmap[kid] = code
    extra = {f"{k}.py": c for k, c in libmap.items() if k != kid and c is not None}
    return execute.run_tests(bench.state(fid, sid)["env"], code, None, sid, module_name=kid,
                             extra_files=extra, tests_src=tests)


def summarize_results(res, limit=12):
    lines = []
    if res.get("fatal"):
        lines.append(f"FATAL: {res['fatal'][-600:]}")
    if res.get("import_error"):
        lines.append(f"IMPORT ERROR: {res['import_error']}")
    for c in res.get("cases", []):
        if not c["passed"]:
            lines.append(f"FAIL {c['name']} [{c['component']}]: {c['error']}")
    npass = sum(1 for c in res.get("cases", []) if c["passed"])
    ntot = len(res.get("cases", []))
    head = f"{npass}/{ntot} tests passed"
    return head + ("\n" + "\n".join(lines[:limit]) if lines else "")


def passed_set(res):
    return {c["name"] for c in res.get("cases", []) if c["passed"]}


def failed_set(res):
    return {c["name"] for c in res.get("cases", []) if not c["passed"]}


# ----------------------------------------------------------------------------- static analysis
def api_dependencies(code):
    """Dotted names referenced by a module (imports and attribute chains on imported names)."""
    if code is None:
        return []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    aliases = {}
    deps = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                aliases[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
                deps.add(a.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            for a in node.names:
                aliases[a.asname or a.name] = f"{node.module}.{a.name}"
                deps.add(f"{node.module}.{a.name}")
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            chain = []
            cur = node
            while isinstance(cur, ast.Attribute):
                chain.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name) and cur.id in aliases:
                deps.add(".".join([aliases[cur.id]] + list(reversed(chain))))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            deps.add("." + node.func.attr)   # method names (e.g. .append), matched against change docs
    return sorted(deps)


def signatures(code):
    """Public function/class signatures with docstrings (interface stub without bodies)."""
    if code is None:
        return ""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ""
    out = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
            if isinstance(node, ast.FunctionDef):
                out.append(f"def {node.name}({ast.unparse(node.args)}):")
            else:
                out.append(f"class {node.name}:")
                for sub in node.body:
                    if isinstance(sub, ast.FunctionDef) and (not sub.name.startswith("_") or sub.name == "__init__"):
                        out.append(f"    def {sub.name}({ast.unparse(sub.args)}): ...")
            doc = ast.get_docstring(node)
            if doc:
                out.append(f'    """{doc.strip()}"""')
    return "\n".join(out)


def mentioned_in(deps, doc_text):
    """Dependencies whose last name component appears in a change document (cheap deterministic filter)."""
    hits = []
    low = doc_text
    for d in deps:
        last = d.split(".")[-1]
        if len(last) >= 4 and re.search(r"(?<![A-Za-z0-9_])" + re.escape(last) + r"(?![A-Za-z0-9_])", low):
            hits.append(d)
    return hits


# ----------------------------------------------------------------------------- response parsing
FENCE = re.compile(r"```(?:python|py)?[ \t]*\n(.*?)```", re.S)


def extract_blocks(text):
    """Return {header: code} for blocks preceded by '### <HEADER>' lines, plus 'blocks' list in order."""
    out = {"_blocks": []}
    pos = 0
    for m in FENCE.finditer(text):
        before = text[pos:m.start()]
        hdr = re.findall(r"^#{2,4}\s*([A-Z_ ]+?)\s*$", before, re.M)
        body = m.group(1)
        out["_blocks"].append(body)
        if hdr:
            out[hdr[-1].strip().upper()] = body
        pos = m.end()
    return out


def extract_json(text):
    import json
    m = re.findall(r"```json\s*\n(.*?)```", text, re.S)
    cands = m[::-1] + [text]
    for c in cands:
        c = c.strip()
        i, j = c.find("{"), c.rfind("}")
        if i >= 0 and j > i:
            try:
                return json.loads(c[i:j + 1])
            except Exception:
                continue
    return None


def compiles(code):
    try:
        compile(code, "<skill>", "exec")
        return True
    except SyntaxError:
        return False
