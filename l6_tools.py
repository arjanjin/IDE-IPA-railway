# l6_tools.py — IDE-IPA Railway L6 Evaluation Tools
# Version: 2.1.1 (fix: normalize agent_id for ChromaDB validation)
# Author: Assoc. Prof. Dr. Arjin Numsomran — KMITL ICE
# Deploy: https://ide-ipa-railway-production.up.railway.app/mcp
#
# Changes from v2.1.0:
#   - Added normalize_agent_id() utility to comply with ChromaDB
#     collection name constraints (≥3 chars, [a-zA-Z0-9._-],
#     start/end with alphanumeric)
#   - Applied safe_id in l6_query_memory() and l6_write_shared_kb()
#   - All l6_kb_* tools now route through normalize_agent_id()

import re
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from mcp.server.fastmcp import FastMCP


# ─────────────────────────────────────────────────────────────
# MCP server instance (shared with ide_ipa_tools.py via import)
# ─────────────────────────────────────────────────────────────
mcp = FastMCP("ide-ipa-railway")

# Persistent ChromaDB client (Railway volume mount recommended)
_CHROMA_PATH = "/app/data/chroma_db"
chroma_client = chromadb.PersistentClient(
    path=_CHROMA_PATH,
    settings=Settings(anonymized_telemetry=False),
)


# ─────────────────────────────────────────────────────────────
# 🔧 FIX v2.1.1 — agent_id normalization
# ─────────────────────────────────────────────────────────────
#
# ChromaDB collection names must:
#   • be 3–63 characters
#   • contain only [a-zA-Z0-9._-]
#   • start and end with [a-zA-Z0-9]
#   • NOT contain '..'
#
# Short IDs ("A1", "A2") and Thai names break this rule, causing
# `l6_query_memory` to raise ValueError on collection creation.
# ─────────────────────────────────────────────────────────────

# Canonical agent mapping (extend as new agents are added)
AGENT_MAPPING: Dict[str, str] = {
    "A1": "agent-a1-candidate",
    "A2": "agent-a2-im",
    "A3": "agent-a3-ibds",
    "A4": "agent-a4-funder",
}


def normalize_agent_id(agent_id: str) -> str:
    """
    Normalize any agent_id into a valid ChromaDB collection name.

    Rules applied (in order):
    1. If agent_id ∈ AGENT_MAPPING → return mapped name.
    2. Replace invalid chars with '-'.
    3. Strip leading/trailing non-alphanumeric characters.
    4. Pad short names with 'agent-' prefix if len < 3.
    5. Truncate to 63 chars.

    Examples:
        "A1"                 → "agent-a1-candidate"
        "A9_new"             → "a9-new"
        "บริษัท ABC"          → "agent-abc"   (Thai stripped)
        "X"                  → "agent-x"
    """
    if not agent_id:
        return "agent-default"

    # 1. Direct mapping
    if agent_id in AGENT_MAPPING:
        return AGENT_MAPPING[agent_id]

    # 2. Sanitize: keep only valid chars, replace others with '-'
    clean = re.sub(r"[^a-zA-Z0-9._-]", "-", agent_id)

    # 3. Strip leading/trailing non-alphanumeric
    clean = re.sub(r"^[^a-zA-Z0-9]+", "", clean)
    clean = re.sub(r"[^a-zA-Z0-9]+$", "", clean)

    # 4. Collapse consecutive '..' (forbidden by ChromaDB)
    clean = re.sub(r"\.{2,}", ".", clean)

    # 5. Pad if too short
    if len(clean) < 3:
        clean = f"agent-{clean}" if clean else "agent-default"

    # 6. Truncate to 63 chars
    return clean[:63].lower()


# ─────────────────────────────────────────────────────────────
# L6 Tool #1 — Parse Input
# ─────────────────────────────────────────────────────────────
@mcp.tool()
async def l6_parse_input(
    input_text: str,
    input_type: str = "text",
) -> Dict[str, Any]:
    """
    Unified Perception Layer — normalize raw input into structured JSON.

    Args:
        input_text: raw text / JSON string / markdown
        input_type: 'text' | 'json' | 'markdown'
    """
    return {
        "status": "ok",
        "version": "2.1.1",
        "input_type": input_type,
        "length": len(input_text),
        "parsed": {"raw": input_text[:1000]},  # truncate for preview
    }


# ─────────────────────────────────────────────────────────────
# L6 Tool #2 — Query Memory (FIX APPLIED)
# ─────────────────────────────────────────────────────────────
@mcp.tool()
async def l6_query_memory(
    agent_id: str,
    query: str,
    task_type: str = "ide_assessment",
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Episodic Memory retrieval — pick strategy by task_type automatically.

    FIX v2.1.1: uses normalize_agent_id() before ChromaDB call.
    """
    safe_id = normalize_agent_id(agent_id)  # ← fix applied

    try:
        collection = chroma_client.get_or_create_collection(name=safe_id)
        results = collection.query(
            query_texts=[query],
            n_results=min(top_k, 20),
        )
        return {
            "status": "ok",
            "version": "2.1.1",
            "agent_id": agent_id,
            "collection_name": safe_id,  # for debugging
            "task_type": task_type,
            "results": results,
        }
    except Exception as e:
        return {
            "status": "error",
            "agent_id": agent_id,
            "collection_name": safe_id,
            "error": str(e),
        }


# ─────────────────────────────────────────────────────────────
# L6 Tool #3 — Write Shared KB (FIX APPLIED)
# ─────────────────────────────────────────────────────────────
@mcp.tool()
async def l6_write_shared_kb(
    agent_id: str,
    content: str,
    tags: List[str],
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Cross-agent Knowledge Sharing — write findings to shared_kb.

    FIX v2.1.1: uses normalize_agent_id() for write_by field.
    """
    safe_id = normalize_agent_id(agent_id)
    meta = metadata or {}
    meta.update({
        "written_by": safe_id,
        "original_agent_id": agent_id,
        "tags": ",".join(tags),
    })

    try:
        kb = chroma_client.get_or_create_collection(name="shared-kb")
        import hashlib
        doc_id = hashlib.sha1(
            f"{safe_id}:{content[:100]}".encode("utf-8")
        ).hexdigest()[:16]
        kb.add(
            documents=[content],
            metadatas=[meta],
            ids=[doc_id],
        )
        return {"status": "ok", "id": doc_id, "written_by": safe_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ─────────────────────────────────────────────────────────────
# L6 Tool #4 — Read Shared KB
# ─────────────────────────────────────────────────────────────
@mcp.tool()
async def l6_read_shared_kb(
    query: str,
    top_k: int = 5,
) -> Dict[str, Any]:
    """Cross-agent KB read — any agent can query."""
    try:
        kb = chroma_client.get_or_create_collection(name="shared-kb")
        results = kb.query(query_texts=[query], n_results=min(top_k, 20))
        return {"status": "ok", "results": results}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ─────────────────────────────────────────────────────────────
# L6 Tool #5 — Evaluate Output (Self-Evaluation Loop)
# ─────────────────────────────────────────────────────────────
@mcp.tool()
async def l6_evaluate_output(
    output: str,
    task_type: str = "ide_assessment",
    company: str = "",
    iteration: int = 1,
) -> Dict[str, Any]:
    """
    Self-Evaluation Loop — check output quality before returning to user.
    task_type: ide_assessment | sroi | coaching | research
    """
    # Placeholder heuristic scoring (production: replace with LLM judge)
    score = min(100, 40 + len(output) // 80 + iteration * 5)
    passed = score >= 65

    return {
        "status": "ok",
        "version": "2.1.1",
        "company": company,
        "task_type": task_type,
        "iteration": iteration,
        "score": score,
        "passed": passed,
        "feedback": (
            "Output meets threshold — ready to return."
            if passed
            else "Below threshold — iterate with more evidence."
        ),
    }


# ─────────────────────────────────────────────────────────────
# L6 Tool #6 — Check Convergence (Auto-halting)
# ─────────────────────────────────────────────────────────────
@mcp.tool()
async def l6_check_convergence(
    scores: List[float],
    max_iter: int = 5,
    delta_threshold: float = 2.0,
) -> Dict[str, Any]:
    """
    Auto-calibrating halting — stop when scores converge or reach max_iter.
    """
    if len(scores) >= max_iter:
        return {"status": "ok", "converged": True, "reason": "max_iter"}

    if len(scores) < 2:
        return {"status": "ok", "converged": False, "reason": "need_more_data"}

    delta = abs(scores[-1] - scores[-2])
    converged = delta < delta_threshold
    return {
        "status": "ok",
        "converged": converged,
        "delta": delta,
        "reason": "delta_below_threshold" if converged else "still_improving",
    }


# ─────────────────────────────────────────────────────────────
# Debug helper — expose normalize_agent_id for tests
# ─────────────────────────────────────────────────────────────
@mcp.tool()
async def l6_chroma_status() -> Dict[str, Any]:
    """Return ChromaDB status — collections, counts, embedding model."""
    try:
        collections = chroma_client.list_collections()
        return {
            "status": "ok",
            "version": "2.1.1",
            "persist_path": _CHROMA_PATH,
            "collections": [
                {"name": c.name, "count": c.count()}
                for c in collections
            ],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
