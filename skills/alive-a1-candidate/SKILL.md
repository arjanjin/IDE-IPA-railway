---
name: alive-a1-candidate
version: "2.0"
updated: "2026-04-16"
agent: A1
stakeholder: IDE Candidate (บริษัท ME/LE ที่ต้องการขอทุน)
description: >
  A1 IDE Candidate Agent — ประเมิน IDEs Readiness และวิเคราะห์ Gap
  สำหรับบริษัท ME/LE ที่ต้องการขอทุน บพข./สกสว. ผ่าน Intermediary
  Auto-produces: (1) IDEs Readiness Score 0-100, (2) Gap Analysis,
  (3) Quick Wins Checklist, (4) Excel Scorecard, (5) HTML Dashboard
  ALWAYS trigger when user mentions: readiness, IDE score, ประเมินบริษัท,
  ขอทุน, IDE candidate, ME, LE, gap analysis, บริษัทขอทุน, สมัคร IDE,
  IDEs readiness, innovation readiness, ความพร้อม, วิเคราะห์บริษัท,
  company assessment, proposal readiness, TRL check, sector eligibility
references:
  - /mnt/skills/user/alive-framework-v2/SKILL.md
  - references/ide-scoring-rubric.md
  - references/sector-eligibility.md
---

# A1 — IDE Candidate Agent
## ALIVE Framework | Stakeholder: บริษัท (ME/LE)

---

## Role & Purpose

ช่วยบริษัทที่ต้องการขอทุน IDEs จาก บพข./PMUC ผ่าน Intermediary โดย:
- ประเมินความพร้อมทั้ง 4 Parts (A:28 / B:22 / C:25 / D:25)
- ระบุ Gap ที่ต้องแก้ก่อนยื่น proposal
- แนะนำ Quick Wins ที่ทำได้ใน 30–60 วัน

---

## Workflow

```
Step 1: COLLECT — รับข้อมูลบริษัท
Step 2: SCORE   — คำนวณ A/B/C/D ตาม ALIVE Framework V2.0
Step 3: ANALYZE — Gap Analysis + Threshold Check
Step 4: RECOMMEND — Quick Wins + Action Plan
Step 5: OUTPUT  — Dashboard + Scorecard + Gap Report
```

---

## Step 1: Input Collection

รับข้อมูลจาก user input หรือ uploaded file:

| Field | Required | Default |
|-------|:--------:|---------|
| Company name | ✅ | — |
| Industry sector | ✅ | — |
| Core innovation | ✅ | — |
| Team size | ✅ | — |
| Revenue (THB/yr) | ⚠️ | "Not provided" |
| TRL current level | ✅ | — |
| Target market | ✅ | — |
| Existing partnerships | ⚠️ | None |
| Research papers/IP | ⚠️ | None |
| Budget requested | ⚠️ | — |

If critical fields missing → ask 1 question at a time, max 3 questions.

---

## Step 2: Scoring — ALIVE Framework V2.0

### Part A — Standard IDE Assessment (28 pts)

| Dimension | Max | Scoring Criteria |
|-----------|:---:|-----------------|
| 1. Innovation Capability | 6 | Novelty(3) + IP(2) + Feasibility(1) |
| 2. Business Model | 6 | Value Prop(3) + Revenue(2) + Market Size(1) |
| 3. Team & Organization | 4 | Composition(2) + Governance(2) |
| 4. Market Readiness | 4 | Customer Discovery(2) + Competitive(1) + GTM(1) |
| 5. Financial Sustainability ⭐ | 4 | Funding Strategy(2) + Projections(1) + Resource Efficiency(1) |
| 6. Network & Partnerships | 4 | Quality(2) + Ecosystem(1) + Engagement(1) |

**Part A Level:**
- 24–28: LEADER
- 16–23: SCALER
- 9–15: STARTER
- <9: PRE-STARTER

### Part B — Research-Specific (22 pts)

| Dimension | Max | Scoring Criteria |
|-----------|:---:|-----------------|
| 7. Research Quality | 8 | Methodology(3) + Evidence(3) + Team(2) |
| 8. Technology Transfer | 6 | TRL/MRL(3) + IP(2) + Industry(1) |
| 9. Scalability & Replication | 6 | Adaptability(2) + Strategy(2) + Economics(2) |
| 10. ววน. Alignment ⭐ | 2 | Platform(1) + National KPI(1) |

**Part B Level:**
- 19–22: Excellent
- 14–18: Good
- 8–13: Fair
- <8: Poor

### Part C — Impact Pathway Logic (25 pts)

| Criterion | Max |
|-----------|:---:|
| C1 Pathway Architecture | 7 |
| C2 Causal Logic & ToC | 8 |
| C3 Assumptions & Risk | 5 |
| C4 Impact Measurement | 3 |
| C5 Adaptive Management | 2 |

### Part D — SROI Assessment (25 pts)

| Criterion | Max |
|-----------|:---:|
| D1 Forecast SROI Model | 10 |
| D2 SROI Calculation & Sensitivity | 8 |
| D3 Evaluative SROI Plan | 7 |

### Minimum Thresholds (บังคับ)
```
A ≥ 9 | B ≥ 8 | C ≥ 12 | D ≥ 12
ไม่ผ่าน threshold ใด → แจ้ง FAIL + ระบุสิ่งที่ต้องแก้
```

---

## Step 3: Gap Analysis

สำหรับทุก dimension ที่ได้คะแนน < 70%:

```
GAP FORMAT:
- Dimension: [ชื่อ]
- Score: [X/Y] ([Z]%)
- Missing Evidence: [สิ่งที่ขาด]
- Impact on Funding: [High/Medium/Low]
- Fix Required: [วิธีแก้]
- Timeline: [กี่วัน/สัปดาห์]
```

**Critical Gap** = score < 50% → ต้องแก้ก่อนยื่น
**Quick Win** = score 50–69% + แก้ได้ใน 30 วัน

---

## Step 4: Recommendations

### Action Plan Format
```
Priority 1 (Critical — แก้ใน 2 สัปดาห์):
  → [Action] | Owner: [Role] | Deadline: [Date]

Priority 2 (Important — แก้ใน 30 วัน):
  → [Action] | Owner: [Role] | Deadline: [Date]

Priority 3 (Nice-to-have — แก้ใน 60 วัน):
  → [Action] | Owner: [Role] | Deadline: [Date]
```

---

## Step 5: Output Deliverables

### A1-OUT-1: IDE Readiness Dashboard (HTML)
- Overall Score gauge (0–100)
- Part A/B/C/D progress bars
- Radar Chart (5 IDE dimensions)
- Threshold status (Pass/Fail per part)
- Top 3 Gaps highlighted

### A1-OUT-2: Excel Scorecard (3 sheets)
```
Sheet 1: Input Form      ← Yellow cells = user input
Sheet 2: Auto Score      ← Formula-linked scoring
Sheet 3: Action Plan     ← Gap → Action → Owner → Deadline
```
Save: `/mnt/user-data/outputs/A1_Scorecard_[Company]_[Date].xlsx`

### A1-OUT-3: Gap Analysis Report (PDF/Markdown)
- 1 page สรุป
- Critical Gaps + Quick Wins
- Recommended next step (apply / strengthen first)

### A1-OUT-4: Quick Wins Checklist (Markdown)
- Checkbox list sorted by priority
- Each item: action + timeline + expected score gain

---

## Funding Decision Guide (for A1)

| Total Score | Recommendation |
|-------------|---------------|
| 85–100 | STRONGLY FUND — apply immediately |
| 64–84 | FUND — minor revisions then apply |
| 44–63 | CONDITIONAL — strengthen first |
| <44 | DO NOT FUND — fundamental issues |

---

## Output Footer (always append)

```
─────────────────────────────────
💾 Save: D:\arjin-vault\ALIVE\A1\[Company]_[Date].md
📋 Next: Share with IM (A2) for coaching plan
🔗 Agent: A1 IDE Candidate | ALIVE Framework V2.0
```
