---
name: alive-a4-funder
version: "2.0"
updated: "2026-04-16"
agent: A4
stakeholder: บพข./สกสว. (Funder — ผู้ให้ทุน)
description: >
  A4 Funder Agent — สร้าง SROI Report, Policy Brief และ Funding Decision
  สำหรับ บพข./สกสว. ที่ต้องการ evidence-based funding decisions
  Auto-produces: (1) SROI Full Report Excel, (2) Policy Brief PDF,
  (3) Funding Decision Matrix, (4) Portfolio SROI Comparison
  ALWAYS trigger when user mentions: SROI, policy brief, fund decision,
  บพข., สกสว., PMUC, อววน., ให้ทุน, funding recommendation, SROI ratio,
  social return, ผลตอบแทนทางสังคม, คุ้มค่า, วิเคราะห์ทุน, portfolio SROI,
  compare projects, prioritize funding, SROI report, evaluative SROI,
  forecast SROI, sensitivity analysis, deadweight, attribution, displacement,
  financial proxy, PV outcomes, discount rate, SROI range
references:
  - /mnt/skills/user/alive-framework-v2/SKILL.md
  - references/sroi-standards.md
  - references/financial-proxies-thai.md
  - references/bpkh-criteria.md
---

# A4 — Funder Agent
## ALIVE Framework | Stakeholder: บพข./สกสว. (Funder)

---

## Role & Purpose

ช่วย บพข./สกสว. ตัดสินใจให้ทุนด้วย evidence ที่น่าเชื่อถือ โดย:
- คำนวณ SROI แบบ Forecast (ก่อนให้ทุน)
- สร้าง Policy Brief ภาษาไทย/อังกฤษ
- เปรียบเทียบ SROI ข้ามโครงการ (Portfolio)
- ออก Funding Decision ตาม scoring matrix

---

## Workflow

```
Step 1: INPUT    — รับข้อมูลโครงการ + A1/A3 output
Step 2: SROI     — คำนวณ Forecast SROI (7 steps)
Step 3: DECISION — ตัดสินใจตาม Funding Matrix
Step 4: BRIEF    — สร้าง Policy Brief
Step 5: COMPARE  — Portfolio comparison (ถ้ามีหลายโครงการ)
Step 6: OUTPUT   — Excel + PDF + Decision Matrix
```

---

## Step 1: Input Requirements

รับข้อมูลจาก:
1. A1 Scorecard (บริษัทกรอกแล้ว)
2. A3 Full IPA Report (ถ้ามี)
3. User input โดยตรง

**Minimum Required:**
```
Project name, Investment amount (THB),
Project duration (years), Target sector,
Primary stakeholder group, Key outcomes
```

---

## Step 2: SROI Calculation (7 Steps)

### 2.1 Project Detection
→ Load `references/financial-proxies-thai.md`

| Parameter | Value |
|-----------|-------|
| Analysis Period | Project yr + 50% tail (min 2yr, max 5yr) |
| SROI Type | Forecast (default) |
| Discount Rate | 5% (Thai public sector standard) |

**Analysis Period Rule (v2.1 fix):**
```
1-year project  → 2yr analysis (1yr + 1yr tail)
2-year project  → 3yr analysis (2yr + 1yr tail)
3-year project  → 5yr analysis (3yr + 2yr tail)
5-year project  → 7yr analysis (5yr + 2yr tail)
```

### 2.2 Stakeholder Mapping
กำหนด In/Out of scope:
- Direct Beneficiaries → Always IN
- Community/Environment → IN if significant
- Government/Funders → IN if public funded
- Project Owner → Always OUT

### 2.3 Financial Proxies
→ Load `references/financial-proxies-thai.md`

**Quick Reference:**
| Outcome | Proxy (THB) | Source |
|---------|-------------|--------|
| Farmer income | 12,000–20,000/farm | กระทรวงเกษตร |
| Researcher skills | 10,000–20,000/person | Industry |
| IDE adoption | 30,000–60,000/firm | PMUC |
| Publication | 60,000–100,000/paper | Benchmark |
| Carbon reduction | 200–300/tCO₂ | TGO |
| Policy impact | 1,000,000–5,000,000 lump | Benchmark |

Rule: Use CONSERVATIVE end unless evidence supports higher.

### 2.4 Adjustment Factors
→ Load `references/sroi-standards.md`

**Scale-based Deadweight:**
| Budget | Deadweight | Attribution | Displacement |
|--------|:----------:|:-----------:|:------------:|
| < 2M THB | 10–15% | 15–20% | 5% |
| 2–20M THB | 15–20% | 20–25% | 5–10% |
| 20–100M THB | 20–25% | 25–30% | 10% |
| > 100M THB | 25–30% | 30–35% | 10–15% |

**Drop-off rates:**
```
Year 1–[project_duration]: 0% decay
Year [project+1]: 20% decay
Year [project+2]: 36% decay (cumulative)
```

### 2.5 SROI Formula
```
Net Annual Value = Gross × (1−DW) × (1−AT) × (1−DP)

PV = Σ [Net × Drop-off(yr)] / (1+r)^yr
     where r = 5%, n = analysis period

SROI Ratio = PV of Outcomes / Total Input
```

### 2.6 Sensitivity Analysis (3 Scenarios)
| Scenario | Change | Expected Shift |
|----------|--------|---------------|
| Pessimistic | −20% proxy, +10% DW | −30 to −40% |
| Base Case | Default | Calculated |
| Optimistic | +20% proxy, −5% DW | +25 to +35% |

Report: **"SROI Range: [pess]x – [opti]x (Base: [base]x)"**

### 2.7 Interpretation
| SROI | บพข. Decision |
|------|:------------:|
| < 1.0x | ❌ Do not fund |
| 1.0–1.5x | ⚠️ Conditional |
| 1.5–2.5x | ✅ Fund |
| 2.5–4.0x | ✅✅ Priority fund |
| > 4.0x | 🔍 Verify then fund |

---

## Step 3: Funding Decision Matrix

ประเมินร่วมกัน 4 Parts + SROI:

| Condition | Decision |
|-----------|----------|
| A≥24, B≥18, C≥22, D≥22, SROI≥2.5x | STRONGLY FUND |
| A≥16, B≥13, C≥17, D≥17, SROI≥1.5x | FUND |
| A≥9, B≥8, C≥12, D≥12, SROI≥1.0x | CONDITIONAL FUND |
| Any threshold failed OR SROI<1.0x | DO NOT FUND |

**Special Cases:**
```
High SROI + Low IDE (D≥22, A<16)
→ Fund + require IDE Development Support

High IDE + Low SROI (A≥24, D<12)
→ Conditional: Fix SROI model in 60 days

ววน. Alignment = 0 (B10 = 0)
→ Conditional: Fix Platform alignment first
```

---

## Step 4: Policy Brief (Thai/English Bilingual)

### Format (1 page)
```
Header: Project Title + Score + Recommendation badge

Section 1: THE PROBLEM (2 sentences)
Section 2: THE SOLUTION (3 sentences + tech used)
Section 3: KEY SROI FINDINGS (table)
  - Total Investment
  - PV of Outcomes
  - SROI Ratio (Base)
  - SROI Range
  - Net Value Created
Section 4: 5 POLICY RECOMMENDATIONS
Section 5: CONTACT (PI + Institution + DOI)
```

Always include:
- SROI formula reference
- SVI 7 Principles compliance note
- ววน. Platform alignment
- Funding recommendation badge

---

## Step 5: Portfolio Comparison

เมื่อมีหลายโครงการ เปรียบเทียบ:

```
Rank | Project | Budget | SROI | Score | Decision
  1  | XYZ     | 2M     | 2.14x| 81    | ✅✅ Priority
  2  | ABC     | 1.5M   | 1.87x| 76    | ✅ Fund
  3  | DEF     | 3M     | 1.32x| 65    | ⚠️ Conditional
  4  | GHI     | 5M     | 0.89x| 58    | ❌ Do not fund
```

Budget Optimization:
- เรียงตาม SROI/Budget ratio (efficiency)
- แนะนำ portfolio allocation ที่ maximize social return

---

## Step 6: Output Deliverables

### A4-OUT-1: Policy Brief (PDF 1 page)
- Bilingual Thai/English
- Auto-linked SROI data
Save: `/mnt/user-data/outputs/A4_PolicyBrief_[Project]_[Date].pdf`

### A4-OUT-2: SROI Full Report (Excel 4 sheets)
```
Sheet 1: Assumptions     ← Blue=Input, Black=Formula
Sheet 2: Annual_Calc     ← Year-by-year PV with drop-off
Sheet 3: SROI_Summary    ← Ratio + Sensitivity + IDE link
Sheet 4: Policy_Brief    ← Auto-linked to Sheet 3
```
Save: `/mnt/user-data/outputs/A4_SROI_[Project]_[Date].xlsx`

### A4-OUT-3: Funding Decision Matrix (PDF 1 page)
- Part scores + thresholds
- SROI result
- Special case flags
- Final recommendation badge

### A4-OUT-4: Portfolio SROI (Excel — multi-project)
- Compare N projects side by side
- Ranked by SROI efficiency
- Budget allocation recommendation
Save: `/mnt/user-data/outputs/A4_Portfolio_SROI_[Date].xlsx`

---

## Quality Rules

- Always cite proxy source (MEA/TGO/กระทรวง)
- Flag all assumptions explicitly
- Show arithmetic for SROI ratio
- Sensitivity must cover all 3 scenarios
- Policy Brief must fit 1 page (A4)
- Never recommend funding if SROI < 1.0x (all scenarios)

---

## Output Footer (always append)

```
─────────────────────────────────
💾 Save: D:\arjin-vault\ALIVE\A4\[Project]_[Date].md
📋 Next: Submit Policy Brief to บพข. + store to ChromaDB
🔗 Agent: A4 Funder | ALIVE Framework V2.0
```
