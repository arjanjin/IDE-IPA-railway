"""
IDE-IPA Analyzer Pro — FastAPI + MCP Tools
ไม่ต้องใช้ ANTHROPIC_API_KEY
Claude (claude.ai Max Plan) เป็น AI
Railway host: Tools + PostgreSQL + ChromaDB
"""
import os
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

import db
from tools.l6_tools import (evaluate_output, check_convergence, query_memory, write_shared_kb, read_shared_kb, parse_input, init_l6_db)
from tools.ide_ipa_tools import (
    load_framework,
    score_part_a,
    score_part_d,
    ide_ipa_overall_score,
    calculate_sroi,
    log_coaching_session,
    get_history,
)

load_dotenv()
db.init_db()

app = FastAPI(
    title="IDE-IPA Analyzer Pro",
    description="IDE-IPA Analyzer Pro — Innovation Driven Enterprise Assessment Tools (No API Key Required)",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://claude.ai", "https://*.claude.ai"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

MCP_SECRET = os.environ.get("MCP_SECRET", "")

def verify_secret(x_mcp_secret: Optional[str] = None):
    if MCP_SECRET and x_mcp_secret != MCP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")


# ── Health Check ────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "aaos_level": os.environ.get("AAOS_LEVEL", "5.5"),
        "framework": "IDE-IPA Analyzer Pro v2.1",
        "tools": 7,
        "db": "PostgreSQL",
        "api_key_required": False,
    }


# ── MCP Manifest ────────────────────────────────────────
@app.get("/mcp")
def mcp_manifest():
    """MCP Tool Manifest — Claude อ่านเพื่อรู้จัก tools"""
    return {
        "schema_version": "v1",
        "name_for_human": "IDE-IPA Analyzer Pro",
        "name_for_model": "ide_ipa_analyzer_pro",
        "description": "IDE-IPA Analyzer Pro — Framework v2.1 tools for assessing Innovation Driven Enterprises",
        "tools": [
            {
                "name": "analyzer_pro_load_framework",
                "description": "โหลด IDE-IPA Analyzer Pro Framework v2.1 Scoring Rubric ทั้งหมด",
                "parameters": {}
            },
            {
                "name": "analyzer_pro_score_part_a",
                "description": "ประเมิน Part A Standard IDE Assessment (max 28 คะแนน)",
                "parameters": {
                    "company": "string",
                    "innovation_capability": "int (0-6)",
                    "business_model": "int (0-6)",
                    "team_organization": "int (0-4)",
                    "market_readiness": "int (0-6)",
                    "network_partnerships": "int (0-6)",
                }
            },
            {
                "name": "analyzer_pro_score_part_d",
                "description": "ประเมิน Part D SROI Assessment (max 25 คะแนน)",
                "parameters": {
                    "company": "string",
                    "d1_forecast_model": "int (0-10)",
                    "d2_calculation": "int (0-8)",
                    "d3_evaluative_plan": "int (0-7)",
                }
            },
            {
                "name": "analyzer_pro_overall_score",
                "description": "คำนวณ Overall Score + Funding Decision (100 คะแนน)",
                "parameters": {
                    "company": "string",
                    "score_a": "int",
                    "score_b": "int",
                    "score_c": "int",
                    "score_d": "int",
                    "project": "string (optional)",
                    "save": "bool (default true)",
                }
            },
            {
                "name": "analyzer_pro_calculate_sroi",
                "description": "คำนวณ Forecast SROI + Sensitivity Analysis 3 Scenarios",
                "parameters": {
                    "company": "string",
                    "investment": "float (THB)",
                    "gross_annual": "float (THB/yr)",
                    "duration_yr": "int",
                    "deadweight": "float (default 0.15)",
                    "attribution": "float (default 0.20)",
                    "displacement": "float (default 0.05)",
                    "discount_rate": "float (default 0.05)",
                }
            },
            {
                "name": "analyzer_pro_log_coaching_session",
                "description": "บันทึก Coaching Session ลง PostgreSQL",
                "parameters": {
                    "company": "string",
                    "session_no": "int",
                    "focus": "string",
                    "score_before": "int",
                    "score_after": "int",
                    "notes": "string (optional)",
                }
            },
            {
                "name": "analyzer_pro_get_history",
                "description": "ดึง Assessment History + Coaching Log จาก PostgreSQL",
                "parameters": {
                    "company": "string",
                }
            },
        ]
    }


# ── Tool Schemas ────────────────────────────────────────
class ScorePartARequest(BaseModel):
    company: str
    innovation_capability: int
    business_model: int
    team_organization: int
    market_readiness: int
    network_partnerships: int

class ScorePartDRequest(BaseModel):
    company: str
    d1_forecast_model: int
    d2_calculation: int
    d3_evaluative_plan: int

class OverallScoreRequest(BaseModel):
    company: str
    score_a: int
    score_b: int
    score_c: int
    score_d: int
    project: str = ""
    save: bool = True

class SROIRequest(BaseModel):
    company: str
    investment: float
    gross_annual: float
    duration_yr: int
    deadweight: float = 0.15
    attribution: float = 0.20
    displacement: float = 0.05
    discount_rate: float = 0.05

class CoachingSessionRequest(BaseModel):
    company: str
    session_no: int
    focus: str
    score_before: int
    score_after: int
    notes: str = ""


# ── Tool Endpoints ──────────────────────────────────────
@app.get("/mcp/tools/analyzer_pro_load_framework")
def tool_load_framework():
    return load_framework()

@app.post("/mcp/tools/analyzer_pro_score_part_a")
def tool_score_part_a(req: ScorePartARequest,
                      x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return score_part_a(
        req.company, req.innovation_capability, req.business_model,
        req.team_organization, req.market_readiness, req.network_partnerships
    )

@app.post("/mcp/tools/analyzer_pro_score_part_d")
def tool_score_part_d(req: ScorePartDRequest,
                      x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return score_part_d(req.company, req.d1_forecast_model,
                        req.d2_calculation, req.d3_evaluative_plan)

@app.post("/mcp/tools/analyzer_pro_overall_score")
def tool_overall_score(req: OverallScoreRequest,
                       x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return ide_ipa_overall_score(
        req.company, req.score_a, req.score_b, req.score_c, req.score_d,
        req.project, req.save
    )

@app.post("/mcp/tools/analyzer_pro_calculate_sroi")
def tool_calculate_sroi(req: SROIRequest,
                        x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return calculate_sroi(
        req.company, req.investment, req.gross_annual, req.duration_yr,
        req.deadweight, req.attribution, req.displacement, req.discount_rate
    )

@app.post("/mcp/tools/analyzer_pro_log_coaching_session")
def tool_log_session(req: CoachingSessionRequest,
                     x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return log_coaching_session(
        req.company, req.session_no, req.focus,
        req.score_before, req.score_after, req.notes
    )

@app.get("/mcp/tools/analyzer_pro_get_history/{company}")
def tool_get_history(company: str,
                     x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return get_history(company)

# ════════════════════════════════════════════════════════
# L6 Tool Schemas
# ════════════════════════════════════════════════════════
class EvaluateRequest(BaseModel):
    output: str
    task_type: str
    company: str = ""
    iteration: int = 1

class ConvergenceRequest(BaseModel):
    company: str
    scores: list
    target: float = 0.85
    epsilon: float = 0.02
    max_iter: int = 5

class QueryMemoryRequest(BaseModel):
    query: str
    task_type: str
    agent_id: str
    top_k: int = 5

class WriteKBRequest(BaseModel):
    agent_id: str
    finding: str
    tags: list
    topic: str = ""

class ReadKBRequest(BaseModel):
    query: str
    min_relevance: float = 0.7
    top_k: int = 5

class ParseInputRequest(BaseModel):
    raw_input: str
    input_type: str

# ════════════════════════════════════════════════════════
# L6 Endpoints
# ════════════════════════════════════════════════════════
@app.post("/mcp/tools/l6_evaluate_output")
def tool_evaluate_output(req: EvaluateRequest,
                         x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return evaluate_output(req.output, req.task_type,
                           req.company, req.iteration)

@app.post("/mcp/tools/l6_check_convergence")
def tool_check_convergence(req: ConvergenceRequest,
                           x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return check_convergence(req.company, req.scores,
                             req.target, req.epsilon, req.max_iter)

@app.post("/mcp/tools/l6_query_memory")
def tool_query_memory(req: QueryMemoryRequest,
                      x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return query_memory(req.query, req.task_type,
                        req.agent_id, req.top_k)

@app.post("/mcp/tools/l6_write_shared_kb")
def tool_write_kb(req: WriteKBRequest,
                  x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return write_shared_kb(req.agent_id, req.finding,
                           req.tags, req.topic)

@app.post("/mcp/tools/l6_read_shared_kb")
def tool_read_kb(req: ReadKBRequest,
                 x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return read_shared_kb(req.query, req.min_relevance, req.top_k)

@app.post("/mcp/tools/l6_parse_input")
def tool_parse_input(req: ParseInputRequest,
                     x_mcp_secret: Optional[str] = Header(None)):
    verify_secret(x_mcp_secret)
    return parse_input(req.raw_input, req.input_type)

@app.get("/health/l6")
def health_l6():
    return {
        "status": "ok",
        "aaos_level": "L6-ready",
        "l6_tools": 6,
        "tools": [
            "l6_evaluate_output",
            "l6_check_convergence",
            "l6_query_memory",
            "l6_write_shared_kb",
            "l6_read_shared_kb",
            "l6_parse_input",
        ]
    }
