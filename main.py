"""
IDE-IPA Analyzer Pro — MCP Protocol Server + Health Endpoints
ไม่ต้องใช้ ANTHROPIC_API_KEY
Claude (claude.ai Max Plan) เป็น AI
Railway host: Tools + PostgreSQL + ChromaDB
"""
import os
import json
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.routing import Route
from starlette.responses import JSONResponse

import db
from tools.l6_tools import (evaluate_output, check_convergence, query_memory,
                             write_shared_kb, read_shared_kb, parse_input, init_l6_db)
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

# ════════════════════════════════════════════════════════
# MCP Protocol Server (FastMCP)
# ════════════════════════════════════════════════════════
mcp = FastMCP(
    "IDE-IPA Analyzer Pro",
    instructions="IDE-IPA Analyzer Pro — Framework v2.1 tools for assessing Innovation Driven Enterprises. ไม่ต้องใช้ API Key.",
)


# ── IDE-IPA Tools (7) ──────────────────────────────────
@mcp.tool()
def analyzer_pro_load_framework() -> dict:
    """โหลด IDE-IPA Analyzer Pro Framework v2.1 Scoring Rubric ทั้งหมด (Parts A-D, thresholds, dimensions)"""
    return load_framework()


@mcp.tool()
def analyzer_pro_score_part_a(
    company: str,
    innovation_capability: int,
    business_model: int,
    team_organization: int,
    market_readiness: int,
    network_partnerships: int,
) -> dict:
    """ประเมิน Part A Standard IDE Assessment (max 28 คะแนน)
    - innovation_capability: 0-6
    - business_model: 0-6
    - team_organization: 0-4
    - market_readiness: 0-6
    - network_partnerships: 0-6
    """
    return score_part_a(company, innovation_capability, business_model,
                        team_organization, market_readiness, network_partnerships)


@mcp.tool()
def analyzer_pro_score_part_d(
    company: str,
    d1_forecast_model: int,
    d2_calculation: int,
    d3_evaluative_plan: int,
) -> dict:
    """ประเมิน Part D SROI Assessment (max 25 คะแนน)
    - d1_forecast_model: 0-10
    - d2_calculation: 0-8
    - d3_evaluative_plan: 0-7
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
    return ide_ipa_overall_score(company, score_a, score_b, score_c, score_d, project, save)


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
# Health Endpoints (added to MCP Starlette app)
# ════════════════════════════════════════════════════════
async def health(request):
    return JSONResponse({
        "status": "ok",
        "aaos_level": os.environ.get("AAOS_LEVEL", "5.5"),
        "framework": "IDE-IPA Analyzer Pro v2.1",
        "tools": 13,
        "mcp_protocol": True,
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
# ASGI App — MCP protocol + health routes
# ════════════════════════════════════════════════════════
app = mcp.streamable_http_app()
app.routes.insert(0, Route("/health", health))
app.routes.insert(1, Route("/health/l6", health_l6))
