"""
biav_engine.py — BIAV 专属 Claude Agent 引擎

为银芯（BIAV-SC）和黑池（BIAV-BP）双系统深度优化的 Claude Code 级 Agent。
集成 9 模块记忆系统 + 文件/Bash 工具 + 双系统数据隔离 + 角色会话管理。

Usage:
  python scripts/biav_engine.py                       # 交互式（银芯·主控台）
  python scripts/biav_engine.py --role Code-wiki      # 指定角色
  python scripts/biav_engine.py --system blackpool    # 黑池模式
  python scripts/biav_engine.py --model claude-opus-4-6  # 指定模型
  python scripts/biav_engine.py --continue            # 恢复上次会话
"""

import argparse
import glob as globmod
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

SESSIONS_DIR = REPO / "memory" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

# ── Optional imports from existing 9 modules ───────────────────────
def _safe_import(fn):
    """Wrap import so missing deps don't crash the engine."""
    try:
        return fn()
    except Exception:
        return None

mem_search = _safe_import(lambda: __import__("memory_search").search)
mem_build_index = _safe_import(lambda: __import__("memory_search").build_index)
kg_find_node = _safe_import(lambda: __import__("knowledge_graph").find_node)
kg_get_neighbors = _safe_import(lambda: __import__("knowledge_graph").get_neighbors)
kg_find_related = _safe_import(lambda: __import__("knowledge_graph").find_related_files)
kg_build_graph = _safe_import(lambda: __import__("knowledge_graph").build_graph)
memrl_compute = _safe_import(lambda: __import__("memrl").compute_utility)
memrl_archival = _safe_import(lambda: __import__("memrl").suggest_archival)
ctx_recommend = _safe_import(lambda: __import__("context_manager").recommend_context)
reflexion_scan = _safe_import(lambda: __import__("reflexion").scan_all)
boot_snapshot = _safe_import(lambda: __import__("boot_snapshot").generate_snapshot)

try:
    from dream import check_precomputed_cache as dream_cache
except Exception:
    dream_cache = None

try:
    import anthropic
except ImportError:
    print("ERROR: pip install anthropic")
    sys.exit(1)

# ── ANSI colors ────────────────────────────────────────────────────
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_CYAN = "\033[36m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_RED = "\033[31m"
C_MAGENTA = "\033[35m"


# ══════════════════════════════════════════════════════════════════
# Section 1: Dual System Guard
# ══════════════════════════════════════════════════════════════════

class DualSystemGuard:
    """Enforce data isolation between Silver Core and Black Pool."""

    def __init__(self, system: str = "silvercore"):
        self.system = system
        self.repo = str(REPO)
        self.violations: list[dict] = []

    def check_read(self, path: str) -> tuple[bool, str]:
        p = str(Path(path).resolve())
        if self.system == "silvercore":
            # Block reading anything flagged as blackpool
            if "black-pool" in p or "blackpool" in p or "biav-bp" in p.lower():
                return False, "银芯模式禁止读取黑池路径"
        return True, ""

    def check_write(self, path: str) -> tuple[bool, str]:
        p = str(Path(path).resolve())
        if self.system == "silvercore":
            if not p.startswith(self.repo):
                return False, f"银芯模式禁止写入仓库外路径: {p}"
            if "black-pool" in p or "blackpool" in p:
                return False, "银芯模式禁止写入黑池路径"
        elif self.system == "blackpool":
            if p.startswith(self.repo):
                return False, "黑池模式禁止写入银芯仓库"
        return True, ""

    def check_bash(self, command: str) -> tuple[bool, str]:
        dangerous = ["rm -rf /", "rm -rf ~", "> /dev/sda", "mkfs.", ":(){", "fork bomb"]
        for d in dangerous:
            if d in command:
                return False, f"危险命令被阻止: {d}"
        if self.system == "silvercore":
            if "black-pool" in command or "biav-bp" in command.lower():
                return False, "银芯模式禁止访问黑池资源"
        return True, ""

    def log_violation(self, tool: str, detail: str):
        v = {"time": datetime.now().isoformat(), "tool": tool, "detail": detail}
        self.violations.append(v)
        print(f"{C_RED}[GUARD] {detail}{C_RESET}")


# ══════════════════════════════════════════════════════════════════
# Section 2: Tool Definitions (Anthropic API format)
# ══════════════════════════════════════════════════════════════════

TOOLS = [
    # ── File Tools ──
    {
        "name": "read_file",
        "description": "Read a file and return contents with line numbers. Use offset/limit for large files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute or repo-relative file path"},
                "offset": {"type": "integer", "description": "Start line (0-based)", "default": 0},
                "limit": {"type": "integer", "description": "Max lines to read", "default": 2000},
            },
            "required": ["path"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace old_string with new_string in a file. old_string must be unique in the file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_string": {"type": "string", "description": "Exact text to find"},
                "new_string": {"type": "string", "description": "Replacement text"},
            },
            "required": ["path", "old_string", "new_string"],
        },
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a file with the given content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "glob_files",
        "description": "Find files matching a glob pattern (e.g. '**/*.py', 'memory/*.md').",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"},
                "path": {"type": "string", "description": "Base directory (default: repo root)"},
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "grep_search",
        "description": "Search file contents using regex pattern. Returns matching lines with file paths.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern"},
                "path": {"type": "string", "description": "Directory to search (default: repo root)"},
                "glob": {"type": "string", "description": "File filter (e.g. '*.py')"},
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "bash",
        "description": "Execute a shell command and return stdout+stderr. Use for git, npm, python, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 120},
            },
            "required": ["command"],
        },
    },
    # ── Memory Tools (wrapping existing 9 modules) ──
    {
        "name": "memory_search",
        "description": "Semantic search across BIAV knowledge base (TF-IDF + 4D reranking). Searches memory/, assets/data/, BIAV-SC.md.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "graph_query",
        "description": "Query the BIAV knowledge graph. Find entities and their neighbors (characters, decisions, files, concepts).",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity": {"type": "string", "description": "Entity name to look up"},
                "depth": {"type": "integer", "default": 1, "description": "Traversal hops"},
            },
            "required": ["entity"],
        },
    },
    {
        "name": "graph_related_files",
        "description": "Find files related to an entity via the knowledge graph.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity": {"type": "string"},
                "max_depth": {"type": "integer", "default": 2},
            },
            "required": ["entity"],
        },
    },
    {
        "name": "memory_utility",
        "description": "Get MemRL utility scores for knowledge files. Shows which files are most/least useful.",
        "input_schema": {
            "type": "object",
            "properties": {
                "top_n": {"type": "integer", "default": 10},
            },
        },
    },
    {
        "name": "check_cache",
        "description": "Check Sleep-Time Compute precomputed cache for a query. Returns cached answer if available.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "recommend_context",
        "description": "Get smart context file recommendations based on query + role + semantic/graph/utility signals.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "role": {"type": "string", "default": ""},
                "max_files": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "rebuild_indexes",
        "description": "Rebuild all memory indexes: vector index, knowledge graph, and utility scores.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]


# ══════════════════════════════════════════════════════════════════
# Section 3: Tool Executor
# ══════════════════════════════════════════════════════════════════

class ToolExecutor:
    """Execute tools with dual-system boundary enforcement."""

    def __init__(self, guard: DualSystemGuard):
        self.guard = guard

    def _resolve_path(self, path: str) -> str:
        p = Path(path)
        if not p.is_absolute():
            p = REPO / p
        return str(p.resolve())

    def execute(self, name: str, args: dict) -> str:
        fn = getattr(self, f"_tool_{name}", None)
        if fn is None:
            return json.dumps({"error": f"Unknown tool: {name}"})
        try:
            return fn(args)
        except Exception as e:
            return json.dumps({"error": str(e)})

    # ── File Tools ─────────────────────────────────────────────

    def _tool_read_file(self, args: dict) -> str:
        path = self._resolve_path(args["path"])
        ok, reason = self.guard.check_read(path)
        if not ok:
            self.guard.log_violation("read_file", reason)
            return json.dumps({"error": reason})
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return json.dumps({"error": f"File not found: {path}"})
        except IsADirectoryError:
            return json.dumps({"error": f"Is a directory: {path}. Use glob_files or bash ls."})

        offset = args.get("offset", 0)
        limit = args.get("limit", 2000)
        selected = lines[offset : offset + limit]
        numbered = "".join(f"{offset + i + 1}\t{line}" for i, line in enumerate(selected))
        total = len(lines)
        header = f"[{path}] ({total} lines, showing {offset+1}-{min(offset+limit, total)})\n"
        return header + numbered

    def _tool_edit_file(self, args: dict) -> str:
        path = self._resolve_path(args["path"])
        ok, reason = self.guard.check_write(path)
        if not ok:
            self.guard.log_violation("edit_file", reason)
            return json.dumps({"error": reason})
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            return json.dumps({"error": f"File not found: {path}"})

        old = args["old_string"]
        new = args["new_string"]
        count = content.count(old)
        if count == 0:
            return json.dumps({"error": "old_string not found in file"})
        if count > 1:
            return json.dumps({"error": f"old_string found {count} times, must be unique. Provide more context."})

        content = content.replace(old, new, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return json.dumps({"success": True, "path": path})

    def _tool_write_file(self, args: dict) -> str:
        path = self._resolve_path(args["path"])
        ok, reason = self.guard.check_write(path)
        if not ok:
            self.guard.log_violation("write_file", reason)
            return json.dumps({"error": reason})
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(args["content"])
        return json.dumps({"success": True, "path": path, "bytes": len(args["content"])})

    def _tool_glob_files(self, args: dict) -> str:
        base = self._resolve_path(args.get("path", str(REPO)))
        pattern = args["pattern"]
        full = os.path.join(base, pattern)
        matches = sorted(globmod.glob(full, recursive=True))
        # Filter by guard
        filtered = []
        for m in matches:
            ok, _ = self.guard.check_read(m)
            if ok and os.path.isfile(m):
                filtered.append(os.path.relpath(m, str(REPO)))
        return json.dumps({"count": len(filtered), "files": filtered[:200]})

    def _tool_grep_search(self, args: dict) -> str:
        path = self._resolve_path(args.get("path", str(REPO)))
        ok, reason = self.guard.check_read(path)
        if not ok:
            self.guard.log_violation("grep_search", reason)
            return json.dumps({"error": reason})
        cmd = ["grep", "-rn", "--include", args.get("glob", "*"), "-E", args["pattern"], path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            lines = result.stdout.strip().split("\n")[:100]
            return "\n".join(lines) if lines[0] else "No matches found."
        except subprocess.TimeoutExpired:
            return json.dumps({"error": "grep timed out"})

    def _tool_bash(self, args: dict) -> str:
        command = args["command"]
        ok, reason = self.guard.check_bash(command)
        if not ok:
            self.guard.log_violation("bash", reason)
            return json.dumps({"error": reason})
        timeout = args.get("timeout", 120)
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout, cwd=str(REPO)
            )
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return output[:50000] or "(no output)"
        except subprocess.TimeoutExpired:
            return json.dumps({"error": f"Command timed out after {timeout}s"})

    # ── Memory Tools (wrapping existing modules) ───────────────

    def _tool_memory_search(self, args: dict) -> str:
        if mem_search is None:
            return json.dumps({"error": "memory_search module not available"})
        results = mem_search(args["query"], top_k=args.get("top_k", 5))
        return json.dumps(results, ensure_ascii=False, default=str)

    def _tool_graph_query(self, args: dict) -> str:
        if kg_find_node is None:
            return json.dumps({"error": "knowledge_graph module not available"})
        entity = args["entity"]
        depth = args.get("depth", 1)
        node = kg_find_node(entity)
        if not node:
            return json.dumps({"error": f"Entity '{entity}' not found in graph"})
        neighbors = kg_get_neighbors(node["id"], max_hops=depth)
        return json.dumps({"node": node, "neighbors": neighbors}, ensure_ascii=False, default=str)

    def _tool_graph_related_files(self, args: dict) -> str:
        if kg_find_related is None:
            return json.dumps({"error": "knowledge_graph module not available"})
        files = kg_find_related(args["entity"], max_depth=args.get("max_depth", 2))
        return json.dumps(files, ensure_ascii=False, default=str)

    def _tool_memory_utility(self, args: dict) -> str:
        if memrl_compute is None:
            return json.dumps({"error": "memrl module not available"})
        scores = memrl_compute()
        top_n = args.get("top_n", 10)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1].get("utility", 0), reverse=True)[:top_n]
        return json.dumps(dict(sorted_scores), ensure_ascii=False, default=str)

    def _tool_check_cache(self, args: dict) -> str:
        if dream_cache is None:
            return json.dumps({"error": "dream cache not available"})
        result = dream_cache(args["query"])
        if result:
            return json.dumps(result, ensure_ascii=False, default=str)
        return json.dumps({"miss": True, "query": args["query"]})

    def _tool_recommend_context(self, args: dict) -> str:
        if ctx_recommend is None:
            return json.dumps({"error": "context_manager module not available"})
        result = ctx_recommend(
            args["query"],
            role=args.get("role", ""),
            max_files=args.get("max_files", 5),
        )
        return json.dumps(result, ensure_ascii=False, default=str)

    def _tool_rebuild_indexes(self, args: dict) -> str:
        results = {}
        if mem_build_index:
            try:
                mem_build_index()
                results["vector_index"] = "rebuilt"
            except Exception as e:
                results["vector_index"] = f"error: {e}"
        if kg_build_graph:
            try:
                kg_build_graph()
                results["knowledge_graph"] = "rebuilt"
            except Exception as e:
                results["knowledge_graph"] = f"error: {e}"
        if memrl_compute:
            try:
                memrl_compute()
                results["memory_utility"] = "rebuilt"
            except Exception as e:
                results["memory_utility"] = f"error: {e}"
        return json.dumps(results, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════
# Section 4: Role System + System Prompts
# ══════════════════════════════════════════════════════════════════

ROLE_CONFIGS = {
    # ── 银芯角色 ──
    "Code-主控台": {
        "system": "silvercore",
        "desc": "架构决策、协调、代码审查（不写业务代码）",
        "defaults": ["BIAV-SC.md", "memory/project-status.md", "memory/decisions.md"],
    },
    "Code-wiki": {
        "system": "silvercore",
        "desc": "游戏数据集 + 多语言 Wiki 维护",
        "defaults": ["BIAV-SC.md", "memory/project-status.md", "projects/wiki/data/db/characters.json"],
    },
    "Code-news": {
        "system": "silvercore",
        "desc": "社区聚合器 + 报告系统",
        "defaults": ["BIAV-SC.md", "memory/project-status.md", "projects/news/output/daily-latest.md"],
    },
    "Code-site": {
        "system": "silvercore",
        "desc": "主站 + 部署流水线 + 跨站视觉一致性",
        "defaults": ["BIAV-SC.md", "memory/project-status.md", "memory/style-guide.md"],
    },
    # ── 黑池角色 ──
    "黑池·主控": {
        "system": "blackpool",
        "desc": "内部项目管理、跨部门协调、排期追踪",
        "defaults": ["memory/project-status.md", "memory/decisions.md"],
    },
    "黑池·数值": {
        "system": "blackpool",
        "desc": "战斗数值平衡、养成曲线、经济系统",
        "defaults": ["memory/project-status.md"],
    },
    "黑池·运营": {
        "system": "blackpool",
        "desc": "活动策划、商业化分析、玩家行为分析",
        "defaults": ["memory/project-status.md"],
    },
    "黑池·叙事": {
        "system": "blackpool",
        "desc": "剧情大纲管理、角色设定归档、世界观一致性检查",
        "defaults": ["memory/project-status.md"],
    },
}


def build_system_prompt(role: str, system: str) -> str:
    """Build role-aware system prompt with BIAV context."""
    cfg = ROLE_CONFIGS.get(role, {})
    role_desc = cfg.get("desc", "通用助手")

    # Load BIAV-SC.md for silvercore roles
    biav_context = ""
    if system == "silvercore":
        biav_path = REPO / "BIAV-SC.md"
        if biav_path.exists():
            biav_context = biav_path.read_text(encoding="utf-8")[:8000]

    # Load boot snapshot if available
    snapshot = ""
    snap_path = REPO / "memory" / "boot-snapshot.md"
    if snap_path.exists():
        snapshot = snap_path.read_text(encoding="utf-8")[:4000]

    sys_label = "银芯（BIAV-SC）" if system == "silvercore" else "黑池（BIAV-BP）"
    boundary = (
        "你在银芯（公开信息层）工作。绝不触碰未公开的内部信息、商业数据。"
        if system == "silvercore"
        else "你在黑池（内部信息层）工作。绝不将内部信息泄露到银芯或任何公开渠道。"
    )

    prompt = f"""你是 BIAV 专属 AI Agent，角色：{role}
系统：{sys_label}
职责：{role_desc}

## 数据边界
{boundary}

## 能力
你拥有 13 个工具：
- 文件操作：read_file, edit_file, write_file, glob_files, grep_search, bash
- 记忆系统：memory_search（语义检索）, graph_query（知识图谱）, graph_related_files, memory_utility（效用评分）, check_cache（预计算缓存）, recommend_context（上下文推荐）, rebuild_indexes

## 工作规则
- 修改 memory/ 文件时更新头部时间戳
- 重要决策记录到 memory/decisions.md
- 所有代码产出放到 projects/对应子项目/output/
- 始终使用中文进行说明和对话，代码注释和 commit message 可用英文
- 先理解再行动：读取文件后再修改，不猜测内容

## 当前状态
{snapshot[:2000] if snapshot else '（启动快照未加载，请用 read_file 读取 memory/project-status.md）'}
"""
    if biav_context:
        prompt += f"\n## 项目定义（摘要）\n{biav_context[:3000]}\n"

    return prompt


# ══════════════════════════════════════════════════════════════════
# Section 5: Agent Loop
# ══════════════════════════════════════════════════════════════════

class BiavAgent:
    """Core agent loop: prompt → model → tool_use → execute → repeat."""

    def __init__(self, role: str = "Code-主控台", system: str = "silvercore",
                 model: str = "claude-sonnet-4-6", max_turns: int = 30):
        self.role = role
        self.system = system
        self.model = model
        self.max_turns = max_turns
        self.guard = DualSystemGuard(system)
        self.executor = ToolExecutor(self.guard)
        self.client = anthropic.Anthropic()
        self.system_prompt = build_system_prompt(role, system)
        self.messages: list[dict] = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.session_file = SESSIONS_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"

    def _save_message(self, msg: dict):
        """Append message to session file."""
        with open(self.session_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg, ensure_ascii=False, default=str) + "\n")

    def _load_session(self, path: Path):
        """Load messages from a session file."""
        self.messages = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.messages.append(json.loads(line))
        self.session_file = path
        print(f"{C_DIM}恢复会话: {path.name} ({len(self.messages)} 条消息){C_RESET}")

    def run_turn(self, user_input: str) -> str:
        """Run one complete user→agent interaction (may involve multiple tool turns)."""
        self.messages.append({"role": "user", "content": user_input})
        self._save_message({"role": "user", "content": user_input})

        turns = 0
        final_text = ""

        while turns < self.max_turns:
            turns += 1

            # Call Claude API
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8192,
                    system=self.system_prompt,
                    tools=TOOLS,
                    messages=self.messages,
                )
            except anthropic.APIError as e:
                return f"{C_RED}API Error: {e}{C_RESET}"

            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens

            # Process response content
            assistant_content = response.content
            self.messages.append({"role": "assistant", "content": _serialize_content(assistant_content)})

            # Extract text and tool_use blocks
            text_parts = []
            tool_uses = []
            for block in assistant_content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)

            # Print text output
            if text_parts:
                text = "\n".join(text_parts)
                final_text += text + "\n"
                print(f"\n{C_CYAN}{text}{C_RESET}")

            # No tool calls → done
            if not tool_uses:
                break

            # Execute tools
            tool_results = []
            for tu in tool_uses:
                print(f"{C_DIM}  ⚙ {tu.name}({_brief_args(tu.input)}){C_RESET}")
                result_str = self.executor.execute(tu.name, tu.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": result_str[:30000],  # Truncate huge outputs
                })

            self.messages.append({"role": "user", "content": tool_results})

            # Check stop reason
            if response.stop_reason == "end_turn":
                break

        if turns >= self.max_turns:
            print(f"{C_YELLOW}[达到最大轮次 {self.max_turns}]{C_RESET}")

        # Save assistant response
        self._save_message({"role": "assistant", "content": final_text.strip()})
        return final_text.strip()

    def run_streaming_turn(self, user_input: str) -> str:
        """Run with streaming output (shows tokens as they arrive)."""
        self.messages.append({"role": "user", "content": user_input})
        self._save_message({"role": "user", "content": user_input})

        turns = 0
        final_text = ""

        while turns < self.max_turns:
            turns += 1

            try:
                with self.client.messages.stream(
                    model=self.model,
                    max_tokens=8192,
                    system=self.system_prompt,
                    tools=TOOLS,
                    messages=self.messages,
                ) as stream:
                    response = stream.get_final_message()
            except anthropic.APIError as e:
                return f"{C_RED}API Error: {e}{C_RESET}"

            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens

            assistant_content = response.content
            self.messages.append({"role": "assistant", "content": _serialize_content(assistant_content)})

            text_parts = []
            tool_uses = []
            for block in assistant_content:
                if block.type == "text":
                    text_parts.append(block.text)
                    print(f"{C_CYAN}{block.text}{C_RESET}", end="", flush=True)
                elif block.type == "tool_use":
                    tool_uses.append(block)

            if text_parts:
                final_text += "\n".join(text_parts) + "\n"
                print()  # newline after streaming

            if not tool_uses:
                break

            tool_results = []
            for tu in tool_uses:
                print(f"{C_DIM}  ⚙ {tu.name}({_brief_args(tu.input)}){C_RESET}")
                result_str = self.executor.execute(tu.name, tu.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": result_str[:30000],
                })

            self.messages.append({"role": "user", "content": tool_results})

            if response.stop_reason == "end_turn":
                break

        self._save_message({"role": "assistant", "content": final_text.strip()})
        return final_text.strip()


def _serialize_content(content) -> list:
    """Serialize Anthropic content blocks to JSON-safe dicts."""
    result = []
    for block in content:
        if block.type == "text":
            result.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            result.append({"type": "tool_use", "id": block.id, "name": block.name, "input": block.input})
    return result


def _brief_args(args: dict, max_len: int = 80) -> str:
    """Shorten tool args for display."""
    s = json.dumps(args, ensure_ascii=False)
    return s[:max_len] + "..." if len(s) > max_len else s


# ══════════════════════════════════════════════════════════════════
# Section 6: CLI Interface
# ══════════════════════════════════════════════════════════════════

BANNER = f"""
{C_BOLD}{C_CYAN}╔══════════════════════════════════════════════════╗
║         BIAV Engine — 缸中之脑 Agent 引擎        ║
╚══════════════════════════════════════════════════╝{C_RESET}
"""


def find_latest_session() -> Path | None:
    """Find the most recent session file."""
    sessions = sorted(SESSIONS_DIR.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return sessions[0] if sessions else None


def print_status(agent: BiavAgent):
    """Print current agent status."""
    print(f"\n{C_GREEN}── 状态 ──{C_RESET}")
    print(f"  角色: {agent.role}")
    print(f"  系统: {'银芯' if agent.system == 'silvercore' else '黑池'}")
    print(f"  模型: {agent.model}")
    print(f"  消息数: {len(agent.messages)}")
    print(f"  Token: ↑{agent.total_input_tokens:,} ↓{agent.total_output_tokens:,}")
    print(f"  会话: {agent.session_file.name}")
    if agent.guard.violations:
        print(f"  {C_RED}违规: {len(agent.guard.violations)} 次{C_RESET}")
    # Memory module availability
    modules = {
        "向量检索": mem_search, "知识图谱": kg_find_node,
        "MemRL": memrl_compute, "预计算缓存": dream_cache,
        "上下文推荐": ctx_recommend, "Reflexion": reflexion_scan,
    }
    avail = [k for k, v in modules.items() if v]
    print(f"  记忆模块: {', '.join(avail) if avail else '无'}")
    print()


def main():
    parser = argparse.ArgumentParser(description="BIAV Engine — 缸中之脑 Agent 引擎")
    parser.add_argument("--role", default="Code-主控台", choices=list(ROLE_CONFIGS.keys()),
                        help="会话角色")
    parser.add_argument("--system", default="silvercore", choices=["silvercore", "blackpool"],
                        help="运行系统")
    parser.add_argument("--model", default="claude-sonnet-4-6", help="Claude 模型")
    parser.add_argument("--max-turns", type=int, default=30, help="每轮最大工具调用次数")
    parser.add_argument("--continue", dest="cont", action="store_true",
                        help="恢复上次会话")
    parser.add_argument("--stream", action="store_true", default=True,
                        help="流式输出（默认开启）")
    parser.add_argument("--no-stream", dest="stream", action="store_false",
                        help="关闭流式输出")
    parser.add_argument("prompt", nargs="*", help="直接执行的提示（非交互模式）")
    args = parser.parse_args()

    # Auto-detect system from role
    role_cfg = ROLE_CONFIGS.get(args.role, {})
    if role_cfg.get("system"):
        args.system = role_cfg["system"]

    # Create agent
    agent = BiavAgent(
        role=args.role,
        system=args.system,
        model=args.model,
        max_turns=args.max_turns,
    )

    # Resume session if requested
    if args.cont:
        latest = find_latest_session()
        if latest:
            agent._load_session(latest)
        else:
            print(f"{C_YELLOW}没有可恢复的会话{C_RESET}")

    # Non-interactive mode
    if args.prompt:
        prompt = " ".join(args.prompt)
        if args.stream:
            agent.run_streaming_turn(prompt)
        else:
            result = agent.run_turn(prompt)
            print(result)
        return

    # Interactive REPL
    print(BANNER)
    sys_label = f"{C_GREEN}银芯{C_RESET}" if args.system == "silvercore" else f"{C_RED}黑池{C_RESET}"
    print(f"  角色: {C_BOLD}{args.role}{C_RESET}  系统: {sys_label}  模型: {args.model}")
    print(f"  命令: /quit /status /role /rebuild /help")
    print()

    while True:
        try:
            user_input = input(f"{C_BOLD}{C_MAGENTA}{'▶' if args.system == 'silvercore' else '◆'} {C_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{C_DIM}退出{C_RESET}")
            break

        if not user_input:
            continue

        # Slash commands
        if user_input == "/quit" or user_input == "/exit":
            break
        elif user_input == "/status":
            print_status(agent)
            continue
        elif user_input == "/help":
            print(f"""
{C_GREEN}可用命令:{C_RESET}
  /quit      退出
  /status    查看状态（token、模块、违规记录）
  /role      查看所有可用角色
  /rebuild   重建记忆索引（向量+图谱+效用）
  /clear     清空当前对话（保留系统提示）
  /help      显示本帮助
""")
            continue
        elif user_input == "/role":
            print(f"\n{C_GREEN}可用角色:{C_RESET}")
            for name, cfg in ROLE_CONFIGS.items():
                sys_tag = "银芯" if cfg["system"] == "silvercore" else "黑池"
                mark = " ← 当前" if name == agent.role else ""
                print(f"  {name:12s} [{sys_tag}] {cfg['desc']}{C_BOLD}{mark}{C_RESET}")
            print()
            continue
        elif user_input == "/rebuild":
            print(f"{C_DIM}重建索引...{C_RESET}")
            result = agent.executor.execute("rebuild_indexes", {})
            print(result)
            continue
        elif user_input == "/clear":
            agent.messages = []
            print(f"{C_DIM}对话已清空{C_RESET}")
            continue

        # Run agent
        try:
            if args.stream:
                agent.run_streaming_turn(user_input)
            else:
                result = agent.run_turn(user_input)
                print(result)
        except KeyboardInterrupt:
            print(f"\n{C_YELLOW}中断当前回复{C_RESET}")
            continue

    # Final stats
    print(f"\n{C_DIM}会话统计: ↑{agent.total_input_tokens:,} ↓{agent.total_output_tokens:,} tokens")
    print(f"会话文件: {agent.session_file}{C_RESET}")


if __name__ == "__main__":
    main()
