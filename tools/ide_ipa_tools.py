"""
IDE-IPA Analyzer Pro Tools — ไม่ต้องใช้ ANTHROPIC_API_KEY
Claude (claude.ai Max Plan) เป็น AI — Railway host แค่ Tools + DB
"""
from db import (save_score, save_overall, save_sroi,
                save_session, get_assessment_history, get_coaching_log)

FRAMEWORK = {
    "version": "2.1",
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
    """โหลด IDE-IPA Analyzer Pro Framework v2.1 Scoring Rubric"""
    return {
        "framework_version": FRAMEWORK["version"],
        "parts": FRAMEWORK["parts"],
        "thresholds": FRAMEWORK["thresholds"],
        "scoring": {
            "A": {
                "total": 28,
                "dimensions": {
                    "1_innovation_capability": {"max": 6, "sub": ["Novelty & Differentiation(3)", "IP Strategy(2)", "Technical Feasibility(1)"]},
                    "2_business_model":        {"max": 6, "sub": ["Value Proposition(3)", "Revenue Model(2)", "Market Size(1)"]},
                    "3_team_organization":     {"max": 4, "sub": ["Team Composition(2)", "Management Capacity(2)"]},
                    "4_market_readiness":      {"max": 6, "sub": ["Customer Discovery(3)", "Competitive Analysis(2)", "Go-to-Market(1)"]},
                    "5_network_partnerships":  {"max": 6, "sub": ["Partnership Quality(3)", "Ecosystem Integration(2)", "Stakeholder Engagement(1)"]},
                }
            },
            "B": {
                "total": 22,
                "dimensions": {
                    "B1_technology_readiness":  {"max": 8, "sub": ["TRL Level(3)", "Prototype Status(3)", "Technical Validation(2)"]},
                    "B2_innovation_output":     {"max": 8, "sub": ["Patents/IP(3)", "Products/Services(3)", "Process Innovation(2)"]},
                    "B3_knowledge_management":  {"max": 6, "sub": ["R&D Capability(2)", "Learning Organization(2)", "Knowledge Transfer(2)"]},
                }
            },
            "C": {
                "total": 25,
                "dimensions": {
                    "C1_economic_impact":              {"max": 10, "sub": ["Revenue Growth(4)", "Job Creation(3)", "Value Chain Enhancement(3)"]},
                    "C2_social_impact":                {"max": 8,  "sub": ["Community Benefit(3)", "Skill Development(3)", "Inclusiveness(2)"]},
                    "C3_environmental_sustainability": {"max": 7,  "sub": ["Resource Efficiency(3)", "Carbon Footprint(2)", "Circular Economy(2)"]},
                }
            },
            "D": {
                "total": 25,
                "dimensions": {
                    "D1_forecast_model":    {"max": 10, "sub": ["Input Identification(3)", "Outcome Valuation(4)", "Impact Adjustments(3)"]},
                    "D2_calculation":       {"max": 8,  "sub": ["NPV Calculation(4)", "Sensitivity 3 Scenarios(2)", "Transparency(2)"]},
                    "D3_evaluative_plan":   {"max": 7,  "sub": ["Baseline & Counterfactual(3)", "Stakeholder Engagement(2)", "Reporting(2)"]},
                }
            }
        }
    }


# ════════════════════════════════════════════════════════
# TOOL 2 — Score Part A
# ════════════════════════════════════════════════════════
def score_part_a(company: str, innovation_capability: int,
                 business_model: int, team_organization: int,
                 market_readiness: int, network_partnerships: int) -> dict:
    """ประเมิน Part A — Standard IDE Assessment (max 28)"""
    scores = {
        "1_innovation_capability": innovation_capability,
        "2_business_model":        business_model,
        "3_team_organization":     team_organization,
        "4_market_readiness":      market_readiness,
        "5_network_partnerships":  network_partnerships,
    }
    total = sum(scores.values())
    lv = level_a(total)
    passed = total >= FRAMEWORK["thresholds"]["A"]

    save_score(company, "A", total, 28, lv, passed)

    return {
        "company": company,
        "part": "A",
        "scores": scores,
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
def score_part_b(company: str, b1_technology_readiness: int,
                 b2_innovation_output: int, b3_knowledge_management: int) -> dict:
    """ประเมิน Part B — Innovation Performance (max 22)"""
    scores = {
        "B1_technology_readiness":  b1_technology_readiness,
        "B2_innovation_output":     b2_innovation_output,
        "B3_knowledge_management":  b3_knowledge_management,
    }
    total = sum(scores.values())
    lv = level_b(total)
    passed = total >= FRAMEWORK["thresholds"]["B"]

    save_score(company, "B", total, 22, lv, passed)

    return {
        "company": company,
        "part": "B",
        "scores": scores,
        "total": total,
        "max": 22,
        "pct": round(total / 22 * 100, 1),
        "level": lv,
        "threshold": 8,
        "pass": passed,
    }


# ════════════════════════════════════════════════════════
# TOOL 4 — Score Part C
# ════════════════════════════════════════════════════════
def score_part_c(company: str, c1_economic_impact: int,
                 c2_social_impact: int, c3_environmental_sustainability: int) -> dict:
    """ประเมิน Part C — Impact & Sustainability (max 25)"""
    scores = {
        "C1_economic_impact":               c1_economic_impact,
        "C2_social_impact":                 c2_social_impact,
        "C3_environmental_sustainability":  c3_environmental_sustainability,
    }
    total = sum(scores.values())
    lv = level_c(total)
    passed = total >= FRAMEWORK["thresholds"]["C"]

    save_score(company, "C", total, 25, lv, passed)

    return {
        "company": company,
        "part": "C",
        "scores": scores,
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
    """ประเมิน Part D — SROI Assessment (max 25)"""
    scores = {
        "D1_forecast_model":  d1_forecast_model,
        "D2_calculation":     d2_calculation,
        "D3_evaluative_plan": d3_evaluative_plan,
    }
    total = sum(scores.values())
    lv = level_d(total)
    passed = total >= FRAMEWORK["thresholds"]["D"]

    save_score(company, "D", total, 25, lv, passed)

    return {
        "company": company,
        "part": "D",
        "scores": scores,
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
def ide_ipa_overall_score(company: str, score_a: int, score_b: int,
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
    """คำนวณ Forecast SROI + Sensitivity Analysis 3 Scenarios"""

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
        if r >= 2.5: return "✅✅ Priority Fund"
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
        "standard": "SVI 7 Principles + IDE-IPA Analyzer Pro v2.1",
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
