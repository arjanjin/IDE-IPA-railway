"""
ALIVE Framework V2.0 Tools — ไม่ต้องใช้ ANTHROPIC_API_KEY
Claude (claude.ai Max Plan) เป็น AI — Railway host แค่ Tools + DB
"""
from db import (save_score, save_overall, save_sroi,
                save_session, get_assessment_history, get_coaching_log)

FRAMEWORK = {
    "version": "2.0",
    "parts": {"A": 28, "B": 22, "C": 25, "D": 25},
    "thresholds": {"A": 9, "B": 8, "C": 12, "D": 12},
}

# ── Level Helpers ────────────────────────────────────────
def level_a(score: int) -> str:
    if score >= 24: return "LEADER"
    if score >= 16: return "SCALER"
    if score >= 9:  return "STARTER"
    return "PRE-STARTER"

def level_b(score: int) -> str:
    if score >= 19: return "Excellent"
    if score >= 14: return "Good"
    if score >= 8:  return "Fair"
    return "Poor"

def level_c(score: int) -> str:
    if score >= 22: return "Exemplary"
    if score >= 17: return "Strong"
    if score >= 12: return "Adequate"
    return "Weak/Inadequate"

def level_d(score: int) -> str:
    if score >= 22: return "Exemplary"
    if score >= 17: return "Strong"
    if score >= 12: return "Adequate"
    return "Weak"

def overall_grade(total: int) -> tuple[str, str]:
    if total >= 90: return "A+", "Exceptional"
    if total >= 80: return "A",  "Excellent"
    if total >= 70: return "B+", "Very Good"
    if total >= 60: return "B",  "Good"
    if total >= 50: return "C+", "Fair"
    if total >= 40: return "C",  "Marginal"
    return "F", "Poor"

def funding_decision(a, b, c, d, total) -> str:
    all_pass = (a >= 9 and b >= 8 and c >= 12 and d >= 12)
    if not all_pass:         return "DO NOT FUND"
    if total >= 85:          return "STRONGLY FUND"
    if total >= 64:          return "FUND"
    if total >= 44:          return "CONDITIONAL FUND"
    return "DO NOT FUND"


# ════════════════════════════════════════════════════════
# TOOL 1 — Load Framework
# ════════════════════════════════════════════════════════
def load_framework() -> dict:
    """โหลด ALIVE Framework V2.0 Scoring Rubric"""
    return {
        "framework_version": FRAMEWORK["version"],
        "parts": FRAMEWORK["parts"],
        "thresholds": FRAMEWORK["thresholds"],
        "scoring": {
            "A": {
                "total": 28,
                "description": "Standard IDE Assessment (นวัตกรรม, Business Model, ทีม, ตลาด, Financial, เครือข่าย)",
                "dimensions": {
                    "1_innovation_capability":   {"max": 6, "sub": ["Novelty & Differentiation(3)", "IP Strategy(2)", "Technical Feasibility(1)"]},
                    "2_business_model":          {"max": 6, "sub": ["Value Proposition(3)", "Revenue Model & Customer Acquisition(2)", "Market Size & Growth(1)"]},
                    "3_team_organization":       {"max": 4, "sub": ["Team Composition & Expertise(2)", "Management Capacity & Governance(2)"]},
                    "4_market_readiness":        {"max": 4, "sub": ["Customer Discovery & Validation(2)", "Competitive Analysis(1)", "Go-to-Market Strategy(1)"]},
                    "5_financial_sustainability": {"max": 4, "sub": ["Funding Strategy & Diversification(2)", "Financial Projections & Unit Economics(1)", "Resource Efficiency & Budget Allocation(1)"]},
                    "6_network_partnerships":    {"max": 4, "sub": ["Partnership Quality & Commitment(2)", "Ecosystem Integration(1)", "Stakeholder Engagement Plan(1)"]},
                }
            },
            "B": {
                "total": 22,
                "description": "Research-Specific Assessment (Research Quality + ววน. Alignment)",
                "dimensions": {
                    "7_research_quality":        {"max": 8, "sub": ["Methodological Rigor(3)", "Evidence Base & Literature(3)", "Research Team Capability(2)"]},
                    "8_tech_transfer":           {"max": 6, "sub": ["TRL/MRL Advancement(3)", "IP & Commercialization Strategy(2)", "Industry Collaboration(1)"]},
                    "9_scalability_replication":  {"max": 6, "sub": ["Adaptability to Contexts(2)", "Replication Strategy & Knowledge Transfer(2)", "Scaling Economics(2)"]},
                    "10_vvn_alignment":          {"max": 2, "sub": ["Platform & Frontier Alignment(1)", "National KPI Contribution(1)"]},
                }
            },
            "C": {
                "total": 25,
                "description": "Impact Pathway Logic — Ex-Ante Analysis",
                "dimensions": {
                    "C1_pathway_architecture":   {"max": 7, "sub": ["Five-Stage Structure(3)", "Stakeholder Mapping(2)", "Temporal Logic(2)"]},
                    "C2_causal_logic_toc":       {"max": 8, "sub": ["If-Then Causal Statements(3)", "Theoretical Grounding(3)", "Evidence Base(2)"]},
                    "C3_assumptions_risk":       {"max": 5, "sub": ["Critical Assumptions(2)", "Risk Assessment Matrix(2)", "Mitigation & Contingency(1)"]},
                    "C4_impact_measurement":     {"max": 3, "sub": ["SMART Indicators(2)", "Measurement Feasibility(1)"]},
                    "C5_adaptive_management":    {"max": 2, "sub": ["Monitoring & Feedback Loops(1)", "Learning & Knowledge Management(1)"]},
                }
            },
            "D": {
                "total": 25,
                "description": "SROI Assessment (Forecast Model, Calculation, Evaluative Plan)",
                "dimensions": {
                    "D1_forecast_model":    {"max": 10, "sub": ["Input Identification & Valuation(3)", "Outcome Valuation & Financial Proxy(4)", "Impact Adjustment Factors: DW×AT×DP×Dropoff(3)"]},
                    "D2_calculation":       {"max": 8,  "sub": ["NPV Calculation & Discount Rate Justification(4)", "Sensitivity Analysis 3 Scenarios(2)", "Transparency & Assumption Documentation(2)"]},
                    "D3_evaluative_plan":   {"max": 7,  "sub": ["Baseline & Counterfactual Strategy(3)", "Stakeholder Engagement in Evaluation(2)", "Reporting & Learning Integration(2)"]},
                }
            }
        },
        "special_cases": {
            "high_cd_low_a": "Fund พร้อมแผน IDE Development Support: Mentoring, Training, Partnership Facilitation",
            "high_a_low_cd": "Conditional Fund: แก้ไข Impact Pathway และ SROI Model ก่อนเบิกงวดแรก ภายใน 60 วัน",
            "high_b_low_ad": "พิจารณาเฉพาะ Research Funding เท่านั้น ไม่เหมาะกับ IDE Program",
            "high_d_low_c":  "ต้องแก้ไข Theory of Change ก่อน เพราะ SROI ที่ดีต้องมี Pathway Logic รองรับ",
            "vvn_zero":      "Conditional Fund: ให้ปรับ Proposal เพื่อแสดง Platform Alignment และ National KPI Contribution ก่อนรับทุน",
        }
    }


# ════════════════════════════════════════════════════════
# TOOL 2 — Score Part A
# ════════════════════════════════════════════════════════
def score_part_a(company: str, innovation_capability: int,
                 business_model: int, team_organization: int,
                 market_readiness: int, financial_sustainability: int,
                 network_partnerships: int) -> dict:
    """ประเมิน Part A — Standard IDE Assessment (max 28)
    ALIVE V2.0: 6 มิติ — innovation(6), business(6), team(4), market(4), financial(4), network(4)"""
    MAX_DIM = {"1_innovation_capability": 6, "2_business_model": 6,
               "3_team_organization": 4, "4_market_readiness": 4,
               "5_financial_sustainability": 4, "6_network_partnerships": 4}
    scores = {
        "1_innovation_capability":   min(innovation_capability, 6),
        "2_business_model":          min(business_model, 6),
        "3_team_organization":       min(team_organization, 4),
        "4_market_readiness":        min(market_readiness, 4),
        "5_financial_sustainability": min(financial_sustainability, 4),
        "6_network_partnerships":    min(network_partnerships, 4),
    }
    total = sum(scores.values())
    lv = level_a(total)
    passed = total >= FRAMEWORK["thresholds"]["A"]

    save_score(company, "A", total, 28, lv, passed)

    return {
        "company": company,
        "part": "A",
        "scores": scores,
        "max_per_dim": MAX_DIM,
        "total": total,
        "max": 28,
        "pct": round(total / 28 * 100, 1),
        "level": lv,
        "threshold": 9,
        "pass": passed,
    }


# ════════════════════════════════════════════════════════
# TOOL 3 — Score Part B
# ════════════════════════════════════════════════════════
def score_part_b(company: str, b7_research_quality: int,
                 b8_tech_transfer: int, b9_scalability_replication: int,
                 b10_vvn_alignment: int) -> dict:
    """ประเมิน Part B — Research-Specific Assessment (max 22)
    ALIVE V2.0: 4 มิติ — research_quality(8), tech_transfer(6), scalability(6), ววน.alignment(2)"""
    MAX_DIM = {"7_research_quality": 8, "8_tech_transfer": 6,
               "9_scalability_replication": 6, "10_vvn_alignment": 2}
    scores = {
        "7_research_quality":       min(b7_research_quality, 8),
        "8_tech_transfer":          min(b8_tech_transfer, 6),
        "9_scalability_replication": min(b9_scalability_replication, 6),
        "10_vvn_alignment":         min(b10_vvn_alignment, 2),
    }
    total = sum(scores.values())
    lv = level_b(total)
    passed = total >= FRAMEWORK["thresholds"]["B"]

    save_score(company, "B", total, 22, lv, passed)

    return {
        "company": company,
        "part": "B",
        "scores": scores,
        "max_per_dim": MAX_DIM,
        "total": total,
        "max": 22,
        "pct": round(total / 22 * 100, 1),
        "level": lv,
        "threshold": 8,
        "pass": passed,
        "vvn_flag": "⚠️ ววน. Alignment = 0 — ต้องปรับ Proposal" if scores["10_vvn_alignment"] == 0 else None,
    }


# ════════════════════════════════════════════════════════
# TOOL 4 — Score Part C
# ════════════════════════════════════════════════════════
def score_part_c(company: str, c1_pathway_architecture: int,
                 c2_causal_logic_toc: int, c3_assumptions_risk: int,
                 c4_impact_measurement: int, c5_adaptive_management: int) -> dict:
    """ประเมิน Part C — Impact Pathway Logic, Ex-Ante Analysis (max 25)
    ALIVE V2.0: 5 มิติ — pathway(7), causal_logic(8), assumptions(5), measurement(3), adaptive(2)"""
    MAX_DIM = {"C1_pathway_architecture": 7, "C2_causal_logic_toc": 8,
               "C3_assumptions_risk": 5, "C4_impact_measurement": 3,
               "C5_adaptive_management": 2}
    scores = {
        "C1_pathway_architecture": min(c1_pathway_architecture, 7),
        "C2_causal_logic_toc":     min(c2_causal_logic_toc, 8),
        "C3_assumptions_risk":     min(c3_assumptions_risk, 5),
        "C4_impact_measurement":   min(c4_impact_measurement, 3),
        "C5_adaptive_management":  min(c5_adaptive_management, 2),
    }
    total = sum(scores.values())
    lv = level_c(total)
    passed = total >= FRAMEWORK["thresholds"]["C"]

    save_score(company, "C", total, 25, lv, passed)

    return {
        "company": company,
        "part": "C",
        "scores": scores,
        "max_per_dim": MAX_DIM,
        "total": total,
        "max": 25,
        "pct": round(total / 25 * 100, 1),
        "level": lv,
        "threshold": 12,
        "pass": passed,
    }


# ════════════════════════════════════════════════════════
# TOOL 5 — Score Part D
# ════════════════════════════════════════════════════════
def score_part_d(company: str, d1_forecast_model: int,
                 d2_calculation: int, d3_evaluative_plan: int) -> dict:
    """ประเมิน Part D — SROI Assessment (max 25)
    ALIVE V2.0: 3 มิติ — forecast_model(10), calculation(8), evaluative_plan(7)"""
    MAX_DIM = {"D1_forecast_model": 10, "D2_calculation": 8,
               "D3_evaluative_plan": 7}
    scores = {
        "D1_forecast_model":  min(d1_forecast_model, 10),
        "D2_calculation":     min(d2_calculation, 8),
        "D3_evaluative_plan": min(d3_evaluative_plan, 7),
    }
    total = sum(scores.values())
    lv = level_d(total)
    passed = total >= FRAMEWORK["thresholds"]["D"]

    save_score(company, "D", total, 25, lv, passed)

    return {
        "company": company,
        "part": "D",
        "scores": scores,
        "max_per_dim": MAX_DIM,
        "total": total,
        "max": 25,
        "pct": round(total / 25 * 100, 1),
        "level": lv,
        "threshold": 12,
        "pass": passed,
    }


# ════════════════════════════════════════════════════════
# TOOL 4 — Overall Score
# ════════════════════════════════════════════════════════
def alive_overall_score(company: str, score_a: int, score_b: int,
                          score_c: int, score_d: int,
                          project: str = "", save: bool = True) -> dict:
    """คำนวณ Overall Score + Funding Decision"""
    total = score_a + score_b + score_c + score_d
    grade, lv = overall_grade(total)
    funding = funding_decision(score_a, score_b, score_c, score_d, total)
    all_pass = (score_a >= 9 and score_b >= 8 and
                score_c >= 12 and score_d >= 12)

    if save:
        save_overall(company, project, score_a, score_b,
                     score_c, score_d, total, grade, lv, funding)

    return {
        "company": company,
        "project": project,
        "scores": {
            "A": {"score": score_a, "max": 28, "level": level_a(score_a), "pass": score_a >= 9},
            "B": {"score": score_b, "max": 22, "level": level_b(score_b), "pass": score_b >= 8},
            "C": {"score": score_c, "max": 25, "level": level_c(score_c), "pass": score_c >= 12},
            "D": {"score": score_d, "max": 25, "level": level_d(score_d), "pass": score_d >= 12},
        },
        "total": total,
        "max": 100,
        "all_thresholds_pass": all_pass,
        "grade": grade,
        "level": lv,
        "funding_decision": funding,
        "framework_version": FRAMEWORK["version"],
    }


# ════════════════════════════════════════════════════════
# TOOL 5 — Calculate SROI
# ════════════════════════════════════════════════════════
def calculate_sroi(company: str, investment: float, gross_annual: float,
                   duration_yr: int, deadweight: float = 0.15,
                   attribution: float = 0.20, displacement: float = 0.05,
                   discount_rate: float = 0.05) -> dict:
    """คำนวณ Forecast SROI + Sensitivity Analysis 3 Scenarios (ALIVE V2.0)"""
    if investment <= 0:
        return {"error": "investment must be > 0", "company": company}

    def compute_pv(gross_factor: float) -> float:
        net = gross_annual * gross_factor
        return sum(net / (1 + discount_rate) ** n
                   for n in range(1, duration_yr + 2))

    net_factor = (1 - deadweight) * (1 - attribution) * (1 - displacement)

    pv_base = round(compute_pv(net_factor))
    pv_pess = round(compute_pv(net_factor * 0.7))
    pv_opt  = round(compute_pv(net_factor * 1.27))

    sroi_base = round(pv_base / investment, 2)
    sroi_pess = round(pv_pess / investment, 2)
    sroi_opt  = round(pv_opt  / investment, 2)

    def fund_signal(r: float) -> str:
        if r >= 4.0: return "✅✅ Priority Fund"
        if r >= 2.5: return "✅ Strong Fund"
        if r >= 1.5: return "✅ Fund"
        return "❌ Do Not Fund"

    save_sroi(company, investment, gross_annual, duration_yr,
              sroi_base, sroi_pess, sroi_opt, pv_base, net_factor)

    return {
        "company": company,
        "investment_thb": investment,
        "analysis_period": f"{duration_yr + 1} yrs ({duration_yr}yr + 1yr tail)",
        "adjustments": {
            "deadweight": deadweight,
            "attribution": attribution,
            "displacement": displacement,
            "net_factor": round(net_factor, 3),
        },
        "base_case": {
            "pv_outcomes": pv_base,
            "net_value": pv_base - investment,
            "sroi_ratio": sroi_base,
            "decision": fund_signal(sroi_base),
        },
        "sensitivity": {
            "pessimistic": {"pv": pv_pess, "sroi": sroi_pess, "decision": fund_signal(sroi_pess)},
            "base":        {"pv": pv_base, "sroi": sroi_base, "decision": fund_signal(sroi_base)},
            "optimistic":  {"pv": pv_opt,  "sroi": sroi_opt,  "decision": fund_signal(sroi_opt)},
        },
        "sroi_range": f"{sroi_pess}x – {sroi_opt}x (Base: {sroi_base}x)",
        "standard": "SVI 7 Principles + ALIVE Framework V2.0",
    }


# ════════════════════════════════════════════════════════
# TOOL 6 — Log Coaching Session
# ════════════════════════════════════════════════════════
def log_coaching_session(company: str, session_no: int, focus: str,
                          score_before: int, score_after: int,
                          notes: str = "") -> dict:
    """บันทึก Coaching Session ลง PostgreSQL"""
    gain = score_after - score_before
    trend = "📈 Improved" if gain > 0 else ("➡️ No Change" if gain == 0 else "📉 Declined")

    save_session(company, session_no, focus,
                 score_before, score_after, notes)

    return {
        "company": company,
        "session": session_no,
        "focus": focus,
        "score_before": score_before,
        "score_after": score_after,
        "gain": gain,
        "trend": trend,
        "status": "In Progress 🟡",
    }


# ════════════════════════════════════════════════════════
# TOOL 7 — Get Assessment History
# ════════════════════════════════════════════════════════
def get_history(company: str) -> dict:
    """ดึง Assessment History จาก PostgreSQL"""
    assessments = get_assessment_history(company)
    coaching = get_coaching_log(company)
    return {
        "company": company,
        "total_assessments": len(assessments),
        "assessments": assessments,
        "coaching_sessions": coaching,
    }
