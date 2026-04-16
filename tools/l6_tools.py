"""
AAOS L6 Tools — 6 New Tools for Agentic Loop
เพิ่มเข้า Railway Server เพื่อยกระดับจาก L5.5 → L6
ไม่ต้องใช้ ANTHROPIC_API_KEY
"""
import os
import json
from datetime import datetime
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

def get_chroma():
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _chroma_client


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
        chroma = get_chroma()
        collection = chroma.get_or_create_collection(
            name=agent_id,
            metadata={"hnsw:space": "cosine"}
        )
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
    A2 Researcher เขียน → A1 Engineering อ่านได้เลย
    """
    try:
        chroma = get_chroma()
        collection = chroma.get_or_create_collection(
            name="shared_kb",
            metadata={"hnsw:space": "cosine"}
        )
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
def read_shared_kb(query: str, min_relevance: float = 0.7,
                   top_k: int = 5) -> dict:
    """
    Cross-agent Knowledge Sharing — อ่าน shared_kb
    ทุก agent อ่านได้ — filter ด้วย min_relevance
    """
    try:
        chroma = get_chroma()
        collection = chroma.get_or_create_collection(name="shared_kb")
        count = collection.count()

        if count == 0:
            return {
                "findings": [],
                "count": 0,
                "note": "shared_kb ยังว่างเปล่า",
            }

        # Try similarity search
        findings = []
        try:
            results = collection.query(
                query_texts=[query],
                n_results=min(top_k, count),
            )
            if results["documents"] and results["documents"][0]:
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                ):
                    relevance = round(1 - dist, 3)
                    if relevance >= min_relevance:
                        findings.append({
                            "content": doc[:400],
                            "source_agent": meta.get("source_agent"),
                            "tags": json.loads(meta.get("tags", "[]")),
                            "topic": meta.get("topic", ""),
                            "relevance": relevance,
                            "written_at": meta.get("written_at"),
                        })
        except Exception:
            pass

        # Fallback: ถ้า similarity search ไม่ได้ผล → ดึงทั้งหมด
        if not findings and count > 0:
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
                    "note": "fallback — no similarity score",
                })

        return {
            "query": query,
            "min_relevance": min_relevance,
            "findings": findings,
            "count": len(findings),
            "total_in_kb": count,
        }
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
