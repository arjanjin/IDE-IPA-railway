"""
AAOS L6 Tools — 6 New Tools for Agentic Loop
เพิ่มเข้า Railway Server เพื่อยกระดับจาก L5.5 → L6
ไม่ต้องใช้ ANTHROPIC_API_KEY
"""
import os
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./aaos_local.db")
CHROMA_PATH  = os.environ.get("CHROMA_PATH", "./data/chromadb")
_is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(DATABASE_URL)

_PK = "INTEGER PRIMARY KEY AUTOINCREMENT" if _is_sqlite else "SERIAL PRIMARY KEY"
_NOW = "CURRENT_TIMESTAMP" if _is_sqlite else "NOW()"

# ── ChromaDB lazy init ───────────────────────────────────
_chroma_client = None
_embedding_fn = None

def get_embedding_fn():
    """Lazy-load multilingual embedding model (supports Thai)"""
    global _embedding_fn
    if _embedding_fn is None:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        _embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
    return _embedding_fn

def get_chroma():
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _chroma_client

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

def get_collection(name: str):
    """Get or create a ChromaDB collection with multilingual embeddings"""
    return get_chroma().get_or_create_collection(
        name=name,
        embedding_function=get_embedding_fn(),
        metadata={"hnsw:space": "cosine"}
    )


def reset_shared_kb() -> dict:
    """
    Reset shared_kb collection — ลบ collection เก่า (embedded ด้วย default model)
    แล้วสร้างใหม่ด้วย multilingual model เพื่อแก้ embedding mismatch
    """
    try:
        chroma = get_chroma()
        # ดึง docs เก่าก่อนลบ (ถ้ามี)
        old_docs = []
        try:
            old_col = chroma.get_collection(name="shared_kb")
            count = old_col.count()
            if count > 0:
                data = old_col.get(limit=count)
                for doc, meta, doc_id in zip(
                    data["documents"], data["metadatas"], data["ids"]
                ):
                    old_docs.append({"id": doc_id, "document": doc, "metadata": meta})
        except Exception:
            pass

        # ลบ collection เก่า
        try:
            chroma.delete_collection(name="shared_kb")
        except Exception:
            pass

        # สร้างใหม่ด้วย multilingual embedding
        new_col = get_collection("shared_kb")

        # Re-embed docs เก่า
        re_embedded = 0
        if old_docs:
            new_col.upsert(
                ids=[d["id"] for d in old_docs],
                documents=[d["document"] for d in old_docs],
                metadatas=[d["metadata"] for d in old_docs],
            )
            re_embedded = len(old_docs)

        return {
            "reset": True,
            "old_docs_found": len(old_docs),
            "re_embedded": re_embedded,
            "embedding_model": EMBEDDING_MODEL,
            "collection": "shared_kb",
        }
    except Exception as e:
        return {"reset": False, "error": str(e)}


def chroma_status() -> dict:
    """รายงานสถานะ ChromaDB collections ทั้งหมด"""
    try:
        chroma = get_chroma()
        collections = chroma.list_collections()
        col_info = []
        for col in collections:
            c = chroma.get_collection(name=col.name)
            col_info.append({"name": col.name, "count": c.count()})
        return {
            "status": "ok",
            "embedding_model": EMBEDDING_MODEL,
            "chroma_path": CHROMA_PATH,
            "collections": col_info,
            "total_collections": len(col_info),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def init_l6_db():
    """สร้าง tables สำหรับ L6 components"""
    with engine.connect() as conn:
        # Evaluation scores history
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS eval_scores (
                id          {_PK},
                company     TEXT,
                task_type   TEXT,
                iteration   INTEGER,
                score       FLOAT,
                passed      BOOLEAN,
                feedback    TEXT,
                evaluated_at TIMESTAMP DEFAULT {_NOW}
            )
        """))
        # Convergence log
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS convergence_log (
                id          {_PK},
                company     TEXT,
                iteration   INTEGER,
                score       FLOAT,
                delta       FLOAT,
                halted      BOOLEAN,
                logged_at   TIMESTAMP DEFAULT {_NOW}
            )
        """))
        conn.commit()


# ════════════════════════════════════════════════════════
# L6 TOOL 1 — Self-Evaluation Loop
# ════════════════════════════════════════════════════════
RUBRICS = {
    "ide_assessment": {
        "checks": [
            "มี score ครบ 4 Parts (A/B/C/D)",
            "มี Funding Decision",
            "มี Gap Analysis",
            "มี Coaching Recommendation",
        ],
        "weights": [0.3, 0.2, 0.25, 0.25],
        "threshold": 0.85,
    },
    "sroi": {
        "checks": [
            "มี 3 scenarios (pessimistic/base/optimistic)",
            "มี Net Adjustment Factor",
            "มี PV Outcomes",
            "มี SROI ratio > 0",
        ],
        "weights": [0.3, 0.2, 0.25, 0.25],
        "threshold": 0.85,
    },
    "coaching": {
        "checks": [
            "มี Focus Area",
            "มี Action Items",
            "มี Target Score",
            "มี Timeline",
        ],
        "weights": [0.25, 0.35, 0.25, 0.15],
        "threshold": 0.75,
    },
    "research": {
        "checks": [
            "มี Research Question",
            "มี Methodology",
            "มี Evidence/Citation",
            "มี Conclusion",
        ],
        "weights": [0.25, 0.30, 0.30, 0.15],
        "threshold": 0.80,
    },
}


def evaluate_output(output: str, task_type: str,
                    company: str = "", iteration: int = 1) -> dict:
    """
    Self-Evaluation Loop — ตรวจสอบ output ก่อนส่งให้ผู้ใช้
    Claude วนซ้ำจนกว่า passed = True
    """
    rubric = RUBRICS.get(task_type, RUBRICS["ide_assessment"])
    output_lower = output.lower()

    check_results = []
    weighted_score = 0.0

    keywords = {
        "มี score ครบ 4 Parts (A/B/C/D)": ["part a", "part b", "part c", "part d"],
        "มี Funding Decision":             ["fund", "do not fund", "conditional"],
        "มี Gap Analysis":                 ["gap", "priority", "critical"],
        "มี Coaching Recommendation":      ["coaching", "roadmap", "month", "action"],
        "มี 3 scenarios (pessimistic/base/optimistic)": ["pessimistic", "base", "optimistic"],
        "มี Net Adjustment Factor":        ["net factor", "adjustment", "0.6"],
        "มี PV Outcomes":                  ["pv", "present value", "outcomes"],
        "มี SROI ratio > 0":               ["sroi", "x", "ratio"],
        "มี Focus Area":                   ["focus", "part", "dimension"],
        "มี Action Items":                 ["action", "todo", "task", "เพิ่ม", "แก้ไข"],
        "มี Target Score":                 ["target", "→", "เป้า"],
        "มี Timeline":                     ["month", "week", "day", "เดือน", "สัปดาห์"],
        "มี Research Question":            ["research question", "objective", "วัตถุประสงค์"],
        "มี Methodology":                  ["methodology", "method", "วิธีการ"],
        "มี Evidence/Citation":            ["citation", "reference", "evidence", "doi"],
        "มี Conclusion":                   ["conclusion", "สรุป", "result"],
    }

    for check, weight in zip(rubric["checks"], rubric["weights"]):
        kws = keywords.get(check, [check.lower()])
        passed = any(kw in output_lower for kw in kws)
        check_results.append({"check": check, "passed": passed})
        if passed:
            weighted_score += weight

    score = round(weighted_score, 3)
    passed = score >= rubric["threshold"]
    failed = [c["check"] for c in check_results if not c["passed"]]
    feedback = (
        f"ผ่านแล้ว (score={score})" if passed
        else f"ยังขาด: {', '.join(failed)} | score={score} < {rubric['threshold']}"
    )

    # บันทึก DB
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO eval_scores
                (company, task_type, iteration, score, passed, feedback)
            VALUES (:company, :task_type, :iteration, :score, :passed, :feedback)
        """), {"company": company, "task_type": task_type,
               "iteration": iteration, "score": score,
               "passed": passed, "feedback": feedback})
        conn.commit()

    return {
        "task_type": task_type,
        "iteration": iteration,
        "score": score,
        "threshold": rubric["threshold"],
        "passed": passed,
        "checks": check_results,
        "feedback": feedback,
        "next_action": "ส่ง output" if passed else "แก้ไขและ evaluate ใหม่",
    }


# ════════════════════════════════════════════════════════
# L6 TOOL 2 — Auto-calibrating Halting Condition
# ════════════════════════════════════════════════════════
def check_convergence(company: str, scores: list,
                      target: float = 0.85,
                      epsilon: float = 0.02,
                      max_iter: int = 5) -> dict:
    """
    Auto-calibrating Halting — หยุดเมื่อ converge หรือถึง max_iter
    แทนที่ hardcoded max_iter=3
    """
    n = len(scores)
    delta = abs(scores[-1] - scores[-2]) if n >= 2 else 1.0
    current = scores[-1] if scores else 0.0

    reason = None
    if current >= target:
        reason = f"score ({current}) >= target ({target})"
    elif delta < epsilon:
        reason = f"delta ({delta:.4f}) < epsilon ({epsilon}) — converged"
    elif n >= max_iter:
        reason = f"max_iter ({max_iter}) reached"

    should_halt = reason is not None

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO convergence_log
                (company, iteration, score, delta, halted)
            VALUES (:company, :iteration, :score, :delta, :halted)
        """), {"company": company, "iteration": n,
               "score": current, "delta": round(delta, 4),
               "halted": should_halt})
        conn.commit()

    return {
        "company": company,
        "iteration": n,
        "current_score": current,
        "delta": round(delta, 4),
        "target": target,
        "epsilon": epsilon,
        "should_halt": should_halt,
        "halt_reason": reason,
        "scores_history": scores,
    }


# ════════════════════════════════════════════════════════
# L6 TOOL 3 — Episodic Memory Strategy Selector
# ════════════════════════════════════════════════════════
MEMORY_STRATEGIES = {
    "research":    "similarity_search",
    "engineering": "keyword_exact",
    "reflect":     "temporal_recent",
    "medical":     "similarity_search",
    "business":    "similarity_search",
}


def query_memory(query: str, task_type: str,
                 agent_id: str, top_k: int = 5) -> dict:
    """
    Episodic Memory Strategy Selector
    เลือก retrieval strategy ตาม task_type อัตโนมัติ
    """
    strategy = MEMORY_STRATEGIES.get(task_type, "similarity_search")

    try:
        collection = get_collection(agent_id)
        count = collection.count()

        if count == 0:
            return {
                "agent_id": agent_id,
                "strategy": strategy,
                "task_type": task_type,
                "memories": [],
                "count": 0,
                "note": "ยังไม่มี memories ใน collection นี้",
            }

        results = collection.query(
            query_texts=[query],
            n_results=min(top_k, count),
        )
        memories = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                memories.append({
                    "content": doc[:300],
                    "metadata": meta,
                    "relevance": round(1 - dist, 3),
                })

        return {
            "agent_id": agent_id,
            "strategy": strategy,
            "task_type": task_type,
            "memories": memories,
            "count": len(memories),
        }

    except Exception as e:
        return {
            "agent_id": agent_id,
            "strategy": strategy,
            "error": str(e),
            "memories": [],
        }


# ════════════════════════════════════════════════════════
# L6 TOOL 4 — Write Shared Knowledge Base
# ════════════════════════════════════════════════════════
def write_shared_kb(agent_id: str, finding: str,
                    tags: list, topic: str = "") -> dict:
    """
    Cross-agent Knowledge Sharing — เขียน findings ไป shared_kb
    ทุก Agent (A1-A4) เขียนและอ่านได้
    """
    try:
        collection = get_collection("shared_kb")
        doc_id = f"{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        collection.upsert(
            ids=[doc_id],
            documents=[finding],
            metadatas=[{
                "source_agent": agent_id,
                "tags": json.dumps(tags),
                "topic": topic,
                "written_at": datetime.now().isoformat(),
            }]
        )
        return {
            "saved": True,
            "doc_id": doc_id,
            "source_agent": agent_id,
            "tags": tags,
            "collection": "shared_kb",
            "total_docs": collection.count(),
        }
    except Exception as e:
        return {"saved": False, "error": str(e)}


# ════════════════════════════════════════════════════════
# L6 TOOL 5 — Read Shared Knowledge Base
# ════════════════════════════════════════════════════════
def read_shared_kb(query: str, min_relevance: float = 0.35,
                   top_k: int = 5) -> dict:
    """
    Cross-agent Knowledge Sharing — อ่าน shared_kb
    ทุก agent อ่านได้ — filter ด้วย min_relevance
    """
    try:
        collection = get_collection("shared_kb")
        count = collection.count()

        if count == 0:
            return {
                "findings": [],
                "count": 0,
                "note": "shared_kb ยังว่างเปล่า",
            }

        # Similarity search with multilingual embedding
        all_results = []
        similarity_ok = False
        similarity_error = None

        try:
            results = collection.query(
                query_texts=[query],
                n_results=min(top_k, count),
                include=["documents", "metadatas", "distances"],
            )
            if results["documents"] and results["documents"][0]:
                similarity_ok = True
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                ):
                    relevance = round(1 - dist, 3)
                    all_results.append({
                        "content": doc[:400],
                        "source_agent": meta.get("source_agent"),
                        "tags": json.loads(meta.get("tags", "[]")),
                        "topic": meta.get("topic", ""),
                        "relevance": relevance,
                        "written_at": meta.get("written_at"),
                    })
        except Exception as e:
            similarity_error = str(e)[:120]

        # Filter by min_relevance
        findings = [r for r in all_results if r["relevance"] >= min_relevance]

        # If nothing passes threshold, return all with below_threshold note
        if not findings and all_results:
            best = max(r["relevance"] for r in all_results)
            findings = all_results
            for f in findings:
                f["note"] = f"below min_relevance ({min_relevance}), best={best}"

        # Fallback only if similarity search itself failed
        if not similarity_ok and not all_results and count > 0:
            fallback = collection.get(limit=top_k)
            for doc, meta in zip(
                fallback["documents"],
                fallback["metadatas"],
            ):
                findings.append({
                    "content": doc[:400],
                    "source_agent": meta.get("source_agent"),
                    "tags": json.loads(meta.get("tags", "[]")),
                    "topic": meta.get("topic", ""),
                    "relevance": 0.0,
                    "written_at": meta.get("written_at"),
                    "note": f"fallback — similarity failed: {similarity_error}",
                })

        result = {
            "query": query,
            "min_relevance": min_relevance,
            "findings": findings,
            "count": len(findings),
            "total_in_kb": count,
        }
        if similarity_error:
            result["similarity_error"] = similarity_error
        return result

    except Exception as e:
        return {"findings": [], "error": str(e)}


# ════════════════════════════════════════════════════════
# L6 TOOL 6 — Unified Perception Layer
# ════════════════════════════════════════════════════════
def parse_input(raw_input: str, input_type: str) -> dict:
    """
    Unified Perception Layer — normalize ทุก input → structured JSON
    รองรับ: text, pdf_text, notion_block, image_description, json
    """
    def parse_text(x):
        return {"content": x, "word_count": len(x.split()),
                "lang": "th" if any(
                    "\u0e00" <= c <= "\u0e7f" for c in x) else "en"}

    def parse_pdf_text(x):
        lines = [l.strip() for l in x.split("\n") if l.strip()]
        return {"content": x, "lines": len(lines),
                "sections": [l for l in lines if l.isupper() or l.startswith("#")]}

    def parse_notion_block(x):
        return {"content": x, "format": "notion_markdown",
                "has_tables": "|" in x, "has_code": "```" in x}

    def parse_image_desc(x):
        return {"description": x, "format": "image",
                "note": "ส่ง image กลับให้ Claude Vision ประมวลผลต่อ"}

    def parse_json_input(x):
        try:
            parsed = json.loads(x)
            return {"content": parsed, "format": "json",
                    "keys": list(parsed.keys()) if isinstance(parsed, dict) else []}
        except Exception:
            return {"content": x, "format": "json", "error": "parse failed"}

    parsers = {
        "text":              parse_text,
        "pdf_text":          parse_pdf_text,
        "notion_block":      parse_notion_block,
        "image_description": parse_image_desc,
        "json":              parse_json_input,
    }

    parser = parsers.get(input_type, parse_text)
    structured = parser(raw_input)

    return {
        "input_type": input_type,
        "char_count": len(raw_input),
        "structured": structured,
        "ready_for_agent": True,
    }


# ════════════════════════════════════════════════════════
# L6 KNOWLEDGE BROKER — 4 tools (extract / match / broadcast / flag risk)
# ════════════════════════════════════════════════════════
# Storage: shared_kb collection, distinguished by metadata field `type`
#   type="knowledge"     → default (existing write_shared_kb)
#   type="lesson_atom"   → extracted from coaching sessions
#   type="broadcast"     → peer-learning broadcasts
#   type="risk_alert"    → critical risk flags

_LESSON_KEYWORDS = {
    "solution":      ["solved", "successfully", "achieved", "completed", "delivered", "shipped"],
    "risk":          ["gap", "weakness", "risk", "below", "rejection", "failed", "missing", "ปัญหา"],
    "best_practice": ["best practice", "recommend", "framework", "strategy", "approach"],
}


def _classify_atom(text: str) -> str:
    t = text.lower()
    for atom_type, kws in _LESSON_KEYWORDS.items():
        if any(k in t for k in kws):
            return atom_type
    return "pattern"


def _kb_query(query_text: str, where: dict = None, n: int = 20) -> list:
    """Semantic query against shared_kb. Returns list of {id, document, metadata, distance}."""
    col = get_collection("shared_kb")
    if col.count() == 0:
        return []
    kwargs = {"query_texts": [query_text], "n_results": min(n, col.count())}
    if where:
        kwargs["where"] = where
    q = col.query(**kwargs)
    out = []
    for i, rid in enumerate(q["ids"][0]):
        out.append({
            "id": rid,
            "document": q["documents"][0][i],
            "metadata": q["metadatas"][0][i] or {},
            "distance": q["distances"][0][i],
        })
    return out


def kb_extract_lessons(session_query: str, max_lessons: int = 5) -> dict:
    """Extract lesson atoms from coaching session(s) found via semantic query.
    Stores atoms back to shared_kb with type=lesson_atom.
    """
    try:
        sources = _kb_query(session_query, n=10)
        sources = [s for s in sources if s["metadata"].get("type") != "lesson_atom"]
        if not sources:
            return {"extracted": 0, "lessons": [], "reason": "no source documents matched query"}

        col = get_collection("shared_kb")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        lessons = []
        for idx, src in enumerate(sources[:max_lessons]):
            doc = src["document"] or ""
            atom_type = _classify_atom(doc)
            atom_id = f"KB_LESSON_{ts}_{idx:02d}"
            content = doc[:600]
            src_meta = src["metadata"]
            tags_raw = src_meta.get("tags", "[]")
            try:
                src_tags = json.loads(tags_raw) if isinstance(tags_raw, str) else (tags_raw or [])
            except Exception:
                src_tags = []
            meta = {
                "type": "lesson_atom",
                "atom_type": atom_type,
                "source_id": src["id"],
                "source_agent": src_meta.get("source_agent", "unknown"),
                "source_topic": src_meta.get("topic", ""),
                "tags": json.dumps(src_tags),
                "topic": f"Lesson: {src_meta.get('topic','')[:80]}",
                "written_at": datetime.now().isoformat(),
                "confidence": 0.7 if atom_type == "pattern" else 0.85,
            }
            col.upsert(ids=[atom_id], documents=[content], metadatas=[meta])
            lessons.append({
                "atom_id": atom_id,
                "atom_type": atom_type,
                "source_id": src["id"],
                "source_topic": src_meta.get("topic", ""),
                "preview": content[:160],
            })
        return {"extracted": len(lessons), "lessons": lessons, "session_query": session_query}
    except Exception as e:
        return {"extracted": 0, "error": str(e)}


def kb_match_peers(target_query: str, top_k: int = 3, exclude_agents: list = None) -> dict:
    """Find peer documents/agents semantically similar to target_query.
    Aggregates by source_agent — returns top peers with relevance.
    """
    try:
        results = _kb_query(target_query, n=20)
        results = [r for r in results if r["metadata"].get("type") not in ("broadcast", "risk_alert")]
        excl = set(a.lower() for a in (exclude_agents or []))
        agg = {}
        for r in results:
            agent = r["metadata"].get("source_agent", "unknown")
            if agent.lower() in excl:
                continue
            relevance = max(0.0, 1.0 - r["distance"])
            entry = agg.setdefault(agent, {"agent": agent, "matches": [], "best_relevance": 0.0})
            entry["matches"].append({
                "id": r["id"],
                "topic": r["metadata"].get("topic", ""),
                "relevance": round(relevance, 3),
            })
            entry["best_relevance"] = max(entry["best_relevance"], relevance)
        ranked = sorted(agg.values(), key=lambda x: x["best_relevance"], reverse=True)[:top_k]
        for p in ranked:
            p["matches"] = sorted(p["matches"], key=lambda m: m["relevance"], reverse=True)[:3]
            p["best_relevance"] = round(p["best_relevance"], 3)
        return {"target_query": target_query, "peers_found": len(ranked), "peers": ranked}
    except Exception as e:
        return {"peers_found": 0, "error": str(e)}


def kb_broadcast_lessons(target_audience: str, lesson_query: str,
                         priority: str = "medium", max_lessons: int = 3) -> dict:
    """Compose a peer-learning broadcast. Selects relevant lesson_atoms via lesson_query
    and stores the broadcast as type=broadcast in shared_kb.
    """
    if priority not in ("low", "medium", "high", "critical"):
        return {"broadcast_created": False, "error": "priority must be low/medium/high/critical"}
    try:
        atoms = _kb_query(lesson_query, where={"type": "lesson_atom"}, n=max_lessons)
        if not atoms:
            return {"broadcast_created": False, "reason": "no lesson_atom matched", "lesson_query": lesson_query}

        deadline_days = {"critical": 1, "high": 3, "medium": 7, "low": 14}[priority]
        deadline = (datetime.now() + timedelta(days=deadline_days)).isoformat()
        body_lines = [f"Peer-learning broadcast for: {target_audience}",
                      f"Priority: {priority} | Action by: {deadline}",
                      "Recommended lessons:"]
        atom_ids = []
        for a in atoms:
            body_lines.append(f"  - [{a['id']}] {a['metadata'].get('topic','')}: {a['document'][:140]}")
            atom_ids.append(a["id"])
        body = "\n".join(body_lines)

        col = get_collection("shared_kb")
        bid = f"KB_BROADCAST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        col.upsert(ids=[bid], documents=[body], metadatas=[{
            "type": "broadcast",
            "target_audience": target_audience,
            "priority": priority,
            "deadline": deadline,
            "lesson_atom_ids": json.dumps(atom_ids),
            "topic": f"Broadcast → {target_audience}",
            "tags": json.dumps(["broadcast", priority]),
            "written_at": datetime.now().isoformat(),
        }])
        return {
            "broadcast_created": True,
            "broadcast_id": bid,
            "target_audience": target_audience,
            "priority": priority,
            "deadline": deadline,
            "lesson_count": len(atom_ids),
            "lesson_atom_ids": atom_ids,
        }
    except Exception as e:
        return {"broadcast_created": False, "error": str(e)}


def kb_flag_critical_risk(company_id: str, risk_description: str,
                          severity: str = "high",
                          escalation_contacts: list = None) -> dict:
    """Flag and persist a critical risk alert as type=risk_alert in shared_kb."""
    if severity not in ("low", "medium", "high", "critical"):
        return {"alert_created": False, "error": "severity must be low/medium/high/critical"}
    try:
        deadline_days = {"critical": 1, "high": 3, "medium": 7, "low": 14}[severity]
        deadline = (datetime.now() + timedelta(days=deadline_days)).isoformat()
        contacts = escalation_contacts or []
        col = get_collection("shared_kb")
        aid = f"KB_RISK_{company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        body = f"RISK ALERT [{severity.upper()}] for {company_id}\n\n{risk_description}\n\nDeadline: {deadline}"
        col.upsert(ids=[aid], documents=[body], metadatas=[{
            "type": "risk_alert",
            "company_id": company_id,
            "severity": severity,
            "deadline": deadline,
            "escalation_contacts": json.dumps(contacts),
            "topic": f"Risk: {company_id} ({severity})",
            "tags": json.dumps(["risk_alert", severity, company_id]),
            "written_at": datetime.now().isoformat(),
        }])
        return {
            "alert_created": True,
            "alert_id": aid,
            "company_id": company_id,
            "severity": severity,
            "deadline": deadline,
            "escalation_contacts": contacts,
        }
    except Exception as e:
        return {"alert_created": False, "error": str(e)}
