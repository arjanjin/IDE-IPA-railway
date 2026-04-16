"""
ALIVE Framework V2.0 — MCP Protocol Server + Health Endpoints
ไม่ต้องใช้ ANTHROPIC_API_KEY
Claude (claude.ai Max Plan) เป็น AI
Railway host: Tools + PostgreSQL + ChromaDB
"""
import os
import json
import hmac
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.routing import Route
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

import db
from tools.l6_tools import (evaluate_output, check_convergence, query_memory,
                             write_shared_kb, read_shared_kb, parse_input, init_l6_db)
from tools.ide_ipa_tools import (
    load_framework,
    score_part_a,
    score_part_b,
    score_part_c,
    score_part_d,
    alive_overall_score,
    calculate_sroi,
    log_coaching_session,
    get_history,
)

load_dotenv()
db.init_db()
init_l6_db()

# ════════════════════════════════════════════════════════
# Auth — Bearer Token
# ════════════════════════════════════════════════════════
# MCP_AUTH_TOKENS: comma-separated list of valid tokens
# e.g. "token_alice_abc123,token_bob_def456,token_team_xyz789"
MCP_AUTH_TOKENS = set(
    t.strip() for t in os.environ.get("MCP_AUTH_TOKENS", "").split(",")
    if t.strip()
)


class BearerTokenAuthMiddleware(BaseHTTPMiddleware):
    """ตรวจ Authorization: Bearer <token> เฉพาะ /mcp endpoint"""

    async def dispatch(self, request, call_next):
        # Health endpoints ไม่ต้อง auth
        if request.url.path.startswith("/health"):
            return await call_next(request)

        # ถ้าไม่ได้ตั้ง tokens ไว้ = เปิดสาธารณะ
        if not MCP_AUTH_TOKENS:
            return await call_next(request)

        # ตรวจ Bearer token
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return PlainTextResponse(
                "Unauthorized — ต้องใส่ Authorization: Bearer <token>",
                status_code=401,
                headers={"WWW-Authenticate": 'Bearer realm="ALIVE Framework"'},
            )

        token = auth_header[7:]  # ตัด "Bearer " ออก
        # ใช้ hmac.compare_digest เพื่อป้องกัน timing attack
        token_valid = any(
            hmac.compare_digest(token, valid_token)
            for valid_token in MCP_AUTH_TOKENS
        )

        if not token_valid:
            return PlainTextResponse(
                "Forbidden — token ไม่ถูกต้อง",
                status_code=403,
            )

        return await call_next(request)


# ════════════════════════════════════════════════════════
# MCP Protocol Server (FastMCP)
# ════════════════════════════════════════════════════════
mcp = FastMCP(
    "ALIVE Framework",
    instructions="ALIVE Framework V2.0 — tools for assessing Innovation Driven Enterprises. ไม่ต้องใช้ API Key.",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


# ── ALIVE Tools (7) ───────────────────────────────────
@mcp.tool()
def analyzer_pro_load_framework() -> dict:
    """โหลด ALIVE Framework V2.0 Scoring Rubric ทั้งหมด (Parts A-D, thresholds, dimensions, special_cases)"""
    return load_framework()


@mcp.tool()
def analyzer_pro_score_part_a(
    company: str,
    innovation_capability: int,
    business_model: int,
    team_organization: int,
    market_readiness: int,
    financial_sustainability: int,
    network_partnerships: int,
) -> dict:
    """ประเมิน Part A Standard IDE Assessment (max 28 คะแนน) ALIVE V2.0
    - innovation_capability: 0-6 (Novelty, IP Strategy, Technical Feasibility)
    - business_model: 0-6 (Value Proposition, Revenue Model, Market Size)
    - team_organization: 0-4 (Team Composition, Management Capacity)
    - market_readiness: 0-4 (Customer Discovery, Competitive Analysis, Go-to-Market)
    - financial_sustainability: 0-4 ⭐NEW (Funding Strategy, Financial Projections, Resource Efficiency)
    - network_partnerships: 0-4 (Partnership Quality, Ecosystem Integration, Stakeholder Engagement)
    """
    return score_part_a(company, innovation_capability, business_model,
                        team_organization, market_readiness,
                        financial_sustainability, network_partnerships)


@mcp.tool()
def analyzer_pro_score_part_b(
    company: str,
    b7_research_quality: int,
    b8_tech_transfer: int,
    b9_scalability_replication: int,
    b10_vvn_alignment: int,
) -> dict:
    """ประเมิน Part B Research-Specific Assessment (max 22 คะแนน) ALIVE V2.0
    - b7_research_quality: 0-8 (Methodological Rigor, Evidence Base, Research Team)
    - b8_tech_transfer: 0-6 (TRL/MRL Advancement, IP & Commercialization, Industry Collaboration)
    - b9_scalability_replication: 0-6 (Adaptability, Replication Strategy, Scaling Economics)
    - b10_vvn_alignment: 0-2 ⭐NEW (Platform & Frontier Alignment, National KPI Contribution)
    """
    return score_part_b(company, b7_research_quality, b8_tech_transfer,
                        b9_scalability_replication, b10_vvn_alignment)


@mcp.tool()
def analyzer_pro_score_part_c(
    company: str,
    c1_pathway_architecture: int,
    c2_causal_logic_toc: int,
    c3_assumptions_risk: int,
    c4_impact_measurement: int,
    c5_adaptive_management: int,
) -> dict:
    """ประเมิน Part C Impact Pathway Logic — Ex-Ante Analysis (max 25 คะแนน) ALIVE V2.0
    - c1_pathway_architecture: 0-7 (Five-Stage Structure, Stakeholder Mapping, Temporal Logic)
    - c2_causal_logic_toc: 0-8 (If-Then Causal Statements, Theoretical Grounding, Evidence Base)
    - c3_assumptions_risk: 0-5 (Critical Assumptions, Risk Assessment Matrix, Mitigation)
    - c4_impact_measurement: 0-3 (SMART Indicators, Measurement Feasibility)
    - c5_adaptive_management: 0-2 (Monitoring & Feedback Loops, Learning & Knowledge Management)
    """
    return score_part_c(company, c1_pathway_architecture, c2_causal_logic_toc,
                        c3_assumptions_risk, c4_impact_measurement,
                        c5_adaptive_management)


@mcp.tool()
def analyzer_pro_score_part_d(
    company: str,
    d1_forecast_model: int,
    d2_calculation: int,
    d3_evaluative_plan: int,
) -> dict:
    """ประเมิน Part D SROI Assessment (max 25 คะแนน) ALIVE V2.0
    - d1_forecast_model: 0-10 (Input Identification, Outcome Valuation, Impact Adjustment DW×AT×DP×Dropoff)
    - d2_calculation: 0-8 (NPV & Discount Rate, Sensitivity 3 Scenarios, Transparency)
    - d3_evaluative_plan: 0-7 (Baseline & Counterfactual, Stakeholder Engagement, Reporting)
    """
    return score_part_d(company, d1_forecast_model, d2_calculation, d3_evaluative_plan)


@mcp.tool()
def analyzer_pro_overall_score(
    company: str,
    score_a: int,
    score_b: int,
    score_c: int,
    score_d: int,
    project: str = "",
    save: bool = True,
) -> dict:
    """คำนวณ Overall Score + Funding Decision (100 คะแนน) จาก Part A-D"""
    return alive_overall_score(company, score_a, score_b, score_c, score_d, project, save)


@mcp.tool()
def analyzer_pro_calculate_sroi(
    company: str,
    investment: float,
    gross_annual: float,
    duration_yr: int,
    deadweight: float = 0.15,
    attribution: float = 0.20,
    displacement: float = 0.05,
    discount_rate: float = 0.05,
) -> dict:
    """คำนวณ Forecast SROI + Sensitivity Analysis 3 Scenarios (pessimistic/base/optimistic)
    - investment: เงินลงทุน (THB)
    - gross_annual: ผลตอบแทนรวมต่อปี (THB/yr)
    - duration_yr: ระยะเวลาโครงการ (ปี)
    """
    return calculate_sroi(company, investment, gross_annual, duration_yr,
                          deadweight, attribution, displacement, discount_rate)


@mcp.tool()
def analyzer_pro_log_coaching_session(
    company: str,
    session_no: int,
    focus: str,
    score_before: int,
    score_after: int,
    notes: str = "",
) -> dict:
    """บันทึก Coaching Session ลง PostgreSQL"""
    return log_coaching_session(company, session_no, focus,
                                score_before, score_after, notes)


@mcp.tool()
def analyzer_pro_get_history(company: str) -> dict:
    """ดึง Assessment History + Coaching Log จาก PostgreSQL"""
    return get_history(company)


# ── L6 Agentic Tools (6) ──────────────────────────────
@mcp.tool()
def l6_evaluate_output(
    output: str,
    task_type: str,
    company: str = "",
    iteration: int = 1,
) -> dict:
    """Self-Evaluation Loop — ตรวจสอบ output ก่อนส่งให้ผู้ใช้ (task_type: ide_assessment, sroi, coaching, research)"""
    return evaluate_output(output, task_type, company, iteration)


@mcp.tool()
def l6_check_convergence(
    company: str,
    scores: list,
    target: float = 0.85,
    epsilon: float = 0.02,
    max_iter: int = 5,
) -> dict:
    """Auto-calibrating Halting — หยุดเมื่อ score converge หรือถึง max_iter"""
    return check_convergence(company, scores, target, epsilon, max_iter)


@mcp.tool()
def l6_query_memory(
    query: str,
    task_type: str,
    agent_id: str,
    top_k: int = 5,
) -> dict:
    """Episodic Memory Strategy Selector — เลือก retrieval strategy ตาม task_type อัตโนมัติ"""
    return query_memory(query, task_type, agent_id, top_k)


@mcp.tool()
def l6_write_shared_kb(
    agent_id: str,
    finding: str,
    tags: list,
    topic: str = "",
) -> dict:
    """Cross-agent Knowledge Sharing — เขียน findings ไป shared_kb (ChromaDB)"""
    return write_shared_kb(agent_id, finding, tags, topic)


@mcp.tool()
def l6_read_shared_kb(
    query: str,
    min_relevance: float = 0.7,
    top_k: int = 5,
) -> dict:
    """Cross-agent Knowledge Sharing — อ่าน shared_kb ทุก agent อ่านได้"""
    return read_shared_kb(query, min_relevance, top_k)


@mcp.tool()
def l6_parse_input(
    raw_input: str,
    input_type: str,
) -> dict:
    """Unified Perception Layer — normalize input เป็น structured JSON (input_type: text, pdf_text, notion_block, image_description, json)"""
    return parse_input(raw_input, input_type)


# ════════════════════════════════════════════════════════
# Health Endpoints
# ════════════════════════════════════════════════════════
async def health(request):
    return JSONResponse({
        "status": "ok",
        "aaos_level": os.environ.get("AAOS_LEVEL", "5.5"),
        "framework": "ALIVE Framework V2.0",
        "tools": 15,
        "mcp_protocol": True,
        "auth": "bearer_token" if MCP_AUTH_TOKENS else "none",
        "db": "PostgreSQL",
        "api_key_required": False,
    })


async def health_l6(request):
    return JSONResponse({
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
    })


# ════════════════════════════════════════════════════════
# ASGI App — MCP protocol + auth + health
# ════════════════════════════════════════════════════════
app = mcp.streamable_http_app()
app.routes.insert(0, Route("/health", health))
app.routes.insert(1, Route("/health/l6", health_l6))
app.add_middleware(BearerTokenAuthMiddleware)
