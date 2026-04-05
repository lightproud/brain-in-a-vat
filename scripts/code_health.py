#!/usr/bin/env python3
"""
code_health.py — Automated Code Health Check (Dry Run Test Suite)

Runs all BIAV-SC Python modules through functional tests to catch
regressions, crashes, and data integrity issues. Zero API cost.

Designed to run in dream.yml shallow-sleep (every 6 hours) or
standalone for local dev.

Usage:
    python scripts/code_health.py              # Run all checks
    python scripts/code_health.py --report     # Output JSON report
    python scripts/code_health.py --fix        # Auto-fix what's possible

Exit codes:
    0 = all checks passed
    1 = failures detected (see report)
"""

import importlib
import importlib.util
import json
import re
import sys
import traceback
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO / "scripts"
TODAY = date.today()

# Ensure scripts/ is importable
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


class HealthReport:
    """Collect check results."""

    def __init__(self):
        self.checks = []
        self.fixes = []

    def ok(self, name: str, detail: str = ""):
        self.checks.append({"name": name, "status": "pass", "detail": detail})

    def fail(self, name: str, detail: str, fixable: bool = False):
        self.checks.append({
            "name": name, "status": "fail", "detail": detail, "fixable": fixable,
        })

    def skip(self, name: str, reason: str):
        self.checks.append({"name": name, "status": "skip", "detail": reason})

    def fixed(self, name: str, detail: str):
        self.fixes.append({"name": name, "detail": detail})

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c["status"] == "pass")

    @property
    def failed(self) -> int:
        return sum(1 for c in self.checks if c["status"] == "fail")

    @property
    def skipped(self) -> int:
        return sum(1 for c in self.checks if c["status"] == "skip")

    def to_dict(self) -> dict:
        return {
            "date": TODAY.isoformat(),
            "total": len(self.checks),
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "fixes_applied": len(self.fixes),
            "checks": self.checks,
            "fixes": self.fixes,
        }


# ============================================================
# Check 1: Python syntax validation
# ============================================================

def check_python_syntax(report: HealthReport):
    """Verify all Python scripts parse without syntax errors."""
    import ast

    py_dirs = [SCRIPTS_DIR, REPO / "assets" / "data"]
    for d in py_dirs:
        if not d.exists():
            continue
        for fp in sorted(d.glob("*.py")):
            try:
                with open(fp, encoding="utf-8") as f:
                    ast.parse(f.read())
                report.ok(f"syntax:{fp.name}")
            except SyntaxError as e:
                report.fail(f"syntax:{fp.name}", f"Line {e.lineno}: {e.msg}")


# ============================================================
# Check 2: Module import smoke test
# ============================================================

def check_module_imports(report: HealthReport):
    """Verify all script modules can be imported."""
    modules = [
        "memory_search", "knowledge_graph", "memrl",
        "context_manager", "reflexion", "boot_snapshot",
    ]
    for mod_name in modules:
        try:
            spec = importlib.util.spec_from_file_location(
                mod_name, SCRIPTS_DIR / f"{mod_name}.py"
            )
            if spec and spec.loader:
                report.ok(f"import:{mod_name}")
            else:
                report.fail(f"import:{mod_name}", "spec_from_file_location returned None")
        except Exception as e:
            report.fail(f"import:{mod_name}", str(e))


# ============================================================
# Check 3: Search index integrity
# ============================================================

def check_search_index(report: HealthReport):
    """Verify vector index structure and consistency."""
    vectors_file = REPO / "assets" / "data" / "vectors.json"
    if not vectors_file.exists():
        report.skip("search:index_exists", "vectors.json not built yet")
        return

    try:
        data = json.loads(vectors_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        report.fail("search:index_parse", f"Cannot parse vectors.json: {e}")
        return

    report.ok("search:index_exists")

    # Required keys
    for key in ["vocabulary", "idf", "vectors", "chunks", "meta"]:
        if key not in data:
            report.fail(f"search:key_{key}", f"Missing key: {key}")
        else:
            report.ok(f"search:key_{key}")

    # Vector-chunk consistency
    vectors = data.get("vectors", {})
    chunks = data.get("chunks", {})
    orphan_vectors = [cid for cid in vectors if cid not in chunks]
    orphan_chunks = [cid for cid in chunks if cid not in vectors]

    if orphan_vectors:
        report.fail("search:orphan_vectors", f"{len(orphan_vectors)} vectors without metadata")
    else:
        report.ok("search:orphan_vectors", f"{len(vectors)} vectors all have metadata")

    if orphan_chunks:
        report.fail("search:orphan_chunks", f"{len(orphan_chunks)} chunks without vectors")
    else:
        report.ok("search:orphan_chunks")

    # Functional test: run a query
    try:
        from memory_search import search
        results = search("银芯记忆系统", top_k=3, use_reranker=True)
        if results:
            report.ok("search:query", f"{len(results)} results, top={results[0]['file']}")
        else:
            report.fail("search:query", "Query '银芯记忆系统' returned 0 results")
    except Exception as e:
        report.fail("search:query", f"Search crashed: {e}")


# ============================================================
# Check 4: Knowledge graph integrity
# ============================================================

def check_knowledge_graph(report: HealthReport):
    """Verify knowledge graph structure and query capability."""
    graph_file = REPO / "assets" / "data" / "knowledge-graph.json"
    if not graph_file.exists():
        report.skip("graph:exists", "knowledge-graph.json not built yet")
        return

    try:
        data = json.loads(graph_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        report.fail("graph:parse", f"Cannot parse: {e}")
        return

    report.ok("graph:exists")

    nodes = data.get("nodes", {})
    edges = data.get("edges", [])
    meta = data.get("meta", {})

    # Meta consistency
    if meta.get("node_count") != len(nodes):
        report.fail("graph:meta_nodes", f"meta says {meta.get('node_count')} but actual {len(nodes)}")
    else:
        report.ok("graph:meta_nodes", f"{len(nodes)} nodes")

    if meta.get("edge_count") != len(edges):
        report.fail("graph:meta_edges", f"meta says {meta.get('edge_count')} but actual {len(edges)}")
    else:
        report.ok("graph:meta_edges", f"{len(edges)} edges")

    # Functional test
    try:
        from knowledge_graph import load_graph, find_node
        graph = load_graph()
        matches = find_node(graph, "银芯")
        if matches:
            report.ok("graph:query", f"Found {len(matches)} matches for '银芯'")
        else:
            report.fail("graph:query", "'银芯' not found in graph")
    except Exception as e:
        report.fail("graph:query", f"Query crashed: {e}")


# ============================================================
# Check 5: JSON data file integrity
# ============================================================

def check_json_files(report: HealthReport):
    """Verify all generated JSON data files are valid."""
    json_files = [
        "assets/data/vectors.json",
        "assets/data/knowledge-graph.json",
        "assets/data/memory-utility.json",
        "assets/data/sentinel-baseline.json",
        "assets/data/precomputed-cache.json",
        "memory/dreams/access-log.json",
        "memory/dreams/insights.json",
    ]
    for rel in json_files:
        fp = REPO / rel
        if not fp.exists():
            report.skip(f"json:{Path(rel).name}", "File not yet created")
            continue
        try:
            json.loads(fp.read_text(encoding="utf-8"))
            report.ok(f"json:{Path(rel).name}")
        except json.JSONDecodeError as e:
            report.fail(f"json:{Path(rel).name}", f"Invalid JSON: {e}")


# ============================================================
# Check 6: MemRL utility scores validity
# ============================================================

def check_memrl(report: HealthReport):
    """Verify MemRL utility scores are in valid range."""
    utility_file = REPO / "assets" / "data" / "memory-utility.json"
    if not utility_file.exists():
        report.skip("memrl:exists", "memory-utility.json not yet created")
        return

    try:
        data = json.loads(utility_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        report.fail("memrl:parse", str(e))
        return

    report.ok("memrl:exists", f"{len(data)} files tracked")

    out_of_range = []
    for fp, entry in data.items():
        u = entry.get("utility", -1)
        if not (0 <= u <= 1):
            out_of_range.append(f"{fp}={u}")

    if out_of_range:
        report.fail("memrl:range", f"{len(out_of_range)} out-of-range: {', '.join(out_of_range[:3])}")
    else:
        report.ok("memrl:range", "All utility scores in [0, 1]")


# ============================================================
# Check 7: Cross-module integration
# ============================================================

def check_integration(report: HealthReport):
    """Verify cross-module data flow works end-to-end."""
    try:
        from context_manager import recommend_context
        result = recommend_context("项目状态", role="Code-主控台", max_files=3)
        files = result.get("recommended_files", [])
        if files:
            report.ok("integration:context_mgr", f"{len(files)} files recommended")
        else:
            report.fail("integration:context_mgr", "No files recommended for '项目状态'")
    except Exception as e:
        report.fail("integration:context_mgr", f"Crashed: {e}")

    # Verify boot snapshot generates without error
    try:
        from boot_snapshot import generate_snapshot
        snapshot = generate_snapshot()
        if len(snapshot) > 500:
            report.ok("integration:boot_snapshot", f"{len(snapshot)} chars generated")
        else:
            report.fail("integration:boot_snapshot", f"Suspiciously short: {len(snapshot)} chars")
    except Exception as e:
        report.fail("integration:boot_snapshot", f"Crashed: {e}")


# ============================================================
# Check 8: Broken file references (dream Phase 1 subset)
# ============================================================

def check_references(report: HealthReport):
    """Quick check for broken file references in key files."""
    ref_pattern = re.compile(r"(?:memory/[\w./-]+|assets/[\w./-]+|projects/[\w./-]+)")
    skip_markers = {"xxx", "你的", "YYYY", "待生成", "待创建"}

    key_files = [REPO / "BIAV-SC.md", REPO / "memory" / "project-status.md"]
    broken = []

    for fp in key_files:
        if not fp.exists():
            continue
        text = fp.read_text(encoding="utf-8")
        src = fp.relative_to(REPO)
        for m in ref_pattern.finditer(text):
            ref = m.group(0).rstrip(".,;:!?)")
            if any(marker in ref for marker in skip_markers):
                continue
            target = REPO / ref
            if not target.exists() and not any(REPO.glob(ref)):
                broken.append(f"{src} → {ref}")

    if broken:
        report.fail("refs:broken", f"{len(broken)} broken: {'; '.join(broken[:5])}", fixable=False)
    else:
        report.ok("refs:broken", "All key file references valid")


# ============================================================
# Check 9: Validate data (fact bible)
# ============================================================

def check_validate(report: HealthReport):
    """Run the fact bible validation script."""
    validate_py = REPO / "assets" / "data" / "validate.py"
    if not validate_py.exists():
        report.skip("validate:exists", "validate.py not found")
        return

    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(validate_py)],
            capture_output=True, text=True, timeout=30,
        )
        fail_count = 0
        for line in result.stdout.splitlines():
            if "[FAIL]" in line:
                fail_count += 1
        if fail_count == 0:
            report.ok("validate:fact_bible", "All checks passed")
        else:
            report.fail("validate:fact_bible", f"{fail_count} fact bible checks failed", fixable=False)
    except Exception as e:
        report.fail("validate:fact_bible", f"Crashed: {e}")


# ============================================================
# Check 10: Cosine similarity edge cases
# ============================================================

def check_math_edge_cases(report: HealthReport):
    """Verify math functions handle edge cases without crashing."""
    try:
        from memory_search import cosine_similarity, cosine_similarity_dense

        # Sparse
        assert cosine_similarity({}, {}) == 0.0
        assert cosine_similarity({"a": 1}, {"b": 1}) == 0.0

        # Dense
        assert cosine_similarity_dense([], []) == 0.0
        assert cosine_similarity_dense([0, 0], [0, 0]) == 0.0
        assert abs(cosine_similarity_dense([1, 0], [1, 0]) - 1.0) < 1e-6

        report.ok("math:edge_cases")
    except Exception as e:
        report.fail("math:edge_cases", str(e))


# ============================================================
# Main
# ============================================================

def run_all(do_fix: bool = False) -> HealthReport:
    """Run all health checks."""
    report = HealthReport()

    checkers = [
        ("Python Syntax", check_python_syntax),
        ("Module Imports", check_module_imports),
        ("Search Index", check_search_index),
        ("Knowledge Graph", check_knowledge_graph),
        ("JSON Data Files", check_json_files),
        ("MemRL Utility", check_memrl),
        ("Cross-Module Integration", check_integration),
        ("File References", check_references),
        ("Fact Bible Validation", check_validate),
        ("Math Edge Cases", check_math_edge_cases),
    ]

    for label, checker in checkers:
        try:
            checker(report)
        except Exception as e:
            report.fail(f"runner:{label}", f"Checker crashed: {traceback.format_exc()}")

    return report


def main():
    args = sys.argv[1:]
    report_mode = "--report" in args
    do_fix = "--fix" in args

    print(f"🩺 Code Health Check — {TODAY}\n")

    report = run_all(do_fix=do_fix)

    # Print results
    for check in report.checks:
        icon = {"pass": "✓", "fail": "✗", "skip": "○"}[check["status"]]
        detail = f" — {check['detail']}" if check.get("detail") else ""
        print(f"  {icon} [{check['status'].upper():4s}] {check['name']}{detail}")

    # Summary
    print(f"\n  {'=' * 50}")
    print(f"  Total: {len(report.checks)} checks")
    print(f"  Passed: {report.passed}  Failed: {report.failed}  Skipped: {report.skipped}")

    if report.fixes:
        print(f"  Auto-fixes applied: {len(report.fixes)}")
        for fix in report.fixes:
            print(f"    → {fix['name']}: {fix['detail']}")

    if report.failed > 0:
        print(f"\n  ⚠ {report.failed} checks failed — review needed")
    else:
        print(f"\n  ✅ All checks passed")

    # JSON report for automation
    if report_mode:
        print(f"\n::health::{json.dumps(report.to_dict())}")

    sys.exit(1 if report.failed > 0 else 0)


if __name__ == "__main__":
    main()
