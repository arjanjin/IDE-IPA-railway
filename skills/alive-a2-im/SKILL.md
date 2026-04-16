---
name: alive-a2-im
version: "2.0"
updated: "2026-04-16"
agent: A2
stakeholder: IM — Intermediary (นิติบุคคลไทยที่ coach IDE Candidates)
description: >
  A2 IM Agent — สร้าง Coaching Report และ Progress Tracking
  สำหรับ Intermediary ที่ดูแล portfolio ของ IDE Candidates
  Auto-produces: (1) Coaching Session Report, (2) Portfolio Dashboard,
  (3) Progress Tracking Excel, (4) Monthly Summary for บพข.
  ALWAYS trigger when user mentions: IM, intermediary, coaching,
  portfolio, progress tracking, รายงาน IM, cohort, IDE portfolio,
  coaching plan, session report, coaching summary, บริษัทในพอร์ต,
  ติดตามความก้าวหน้า, dashboard portfolio, monthly report, บพข. report,
  IDE cohort, track progress, coaching session, แผน coaching
references:
  - ../alive-framework-v2/SKILL.md
  - references/coaching-framework.md
  - references/bpkh-reporting.md
---

# A2 — IM (Intermediary) Agent
## ALIVE Framework | Stakeholder: Intermediary

---

## Role & Purpose

ช่วย Intermediary บริหาร portfolio ของ IDE Candidates โดย:
- สร้าง Coaching Plan และ Session Report
- ติดตาม Score Progress ของแต่ละบริษัท
- รายงานความก้าวหน้าให้ บพข. ทุกเดือน
- ระบุบริษัทที่ "At Risk" ก่อนหมดเวลา

---

## Workflow

```
Step 1: LOAD    — โหลด portfolio data จาก ChromaDB / input
Step 2: COACH   — สร้าง coaching plan ต่อบริษัท
Step 3: TRACK   — บันทึก session + score change
Step 4: REPORT  — สร้าง monthly summary สำหรับ บพข.
Step 5: ALERT   — แจ้ง at-risk companies
Step 6: OUTPUT  — Dashboard + Reports + Tracking
```

---

## Step 1: Portfolio Input

รับข้อมูล portfolio จาก:
1. ChromaDB memory (ถ้ามี session ก่อนหน้า)
2. Excel upload (รายชื่อบริษัท + scores)
3. User input (paste ข้อมูล)

**Portfolio Schema:**
```
Company: [ชื่อ]
Sector: [1 ใน 8 target sectors]
A1_Score: [0-28]
B_Score: [0-22]
C_Score: [0-25]
D_Score: [0-25]
Total: [0-100]
Level: [Leader/Scaler/Starter/Pre-Starter]
Coaching_Sessions: [จำนวน]
Status: [Active/Ready/At-Risk/Completed]
Next_Session: [วันที่]
```

---

## Step 2: Coaching Plan

สำหรับแต่ละบริษัท สร้าง coaching plan ตาม Gap:

### Coaching Focus by Score Range

| Gap Area | Score | Coaching Approach |
|----------|:-----:|------------------|
| Innovation Capability | <4/6 | Workshop: IP strategy, differentiation |
| Business Model | <4/6 | Canvas session: Value prop + Revenue model |
| Market Readiness | <4/6 | Customer interview coaching (>20 interviews) |
| Research Quality | <5/8 | Methodology review + literature support |
| ววน. Alignment | 0/2 | Platform mapping workshop |
| SROI | <15/25 | Financial proxy training + model building |

### Session Plan Template
```
Session [N] — [Company] — [Date]
Duration: 2-3 hours
Focus: [Dimension(s)]
Pre-work: [Company prepares X]
Activities:
  1. [Activity 1] — 45 min
  2. [Activity 2] — 60 min
  3. [Activity 3] — 30 min
Expected Score Gain: +[X] pts in [Dimension]
Homework: [Action items with deadline]
Next Session: [Date + Focus]
```

---

## Step 3: Progress Tracking

### Score Change Format
```
[Company] — Session [N] Update
Before: [A/B/C/D] = [Total]
After:  [A/B/C/D] = [Total]
Change: +[X] pts ([Dimension improved])
Status: [Active → Ready] or [At-Risk]
```

### At-Risk Criteria
บริษัทเข้า "At-Risk" เมื่อ:
- Session > 3 แต่ Total < 44
- ไม่ส่ง homework 2 session ติดกัน
- Score ลดลงใน critical dimension
- Deadline เหลือ < 30 วัน แต่ยังไม่ผ่าน threshold

---

## Step 4: Monthly Report to บพข.

### Report Structure (2 pages)

**Page 1: Cohort Summary**
```
Reporting Period: [Month Year]
IM Name: [Organisation]
Total IDE Candidates: [N]
├── Ready to Apply: [N] ([%])
├── In Progress: [N] ([%])
├── At-Risk: [N] ([%])
└── Completed: [N] ([%])

Cohort Average Score: [X]/100
Top Performer: [Company] — [Score]
Most Improved: [Company] — +[X] pts
```

**Page 2: Progress Details + Next Month Plan**
```
Score Distribution Chart
Session Completion Rate: [%]
Key Achievements this Month:
  1. [Achievement]
  2. [Achievement]
Risks & Mitigations:
  1. [Risk] → [Mitigation]
Next Month Focus:
  - [Action 1]
  - [Action 2]
```

---

## Step 5: Alert System

สร้าง alert สำหรับ:

| Alert Type | Trigger | Action |
|------------|---------|--------|
| 🔴 Critical | Score < threshold + deadline < 14 days | Escalate to IM director |
| 🟡 Warning | At-risk criteria met | Schedule emergency session |
| 🟢 Milestone | Company reaches Ready status | Notify for application |
| 📊 Review | No session in 14 days | Send reminder |

---

## Step 6: Output Deliverables

### A2-OUT-1: Portfolio Dashboard (Notion)
- Table: All companies + scores + status
- Filter: By level, sector, status
- Charts: Score distribution, Progress over time
- Auto-update จาก ChromaDB

### A2-OUT-2: Coaching Session Report (PDF)
- 1 page per session
- Score before/after
- Action items + homework
- Next session plan

### A2-OUT-3: Progress Tracking Excel (4 sheets)
```
Sheet 1: Cohort Overview     ← All companies, all scores
Sheet 2: Timeline            ← Coaching schedule Gantt
Sheet 3: Score History       ← Before/After per session
Sheet 4: บพข. KPI Tracker   ← Progress vs target KPIs
```
Save: `/mnt/user-data/outputs/A2_Portfolio_[IM]_[Month].xlsx`

### A2-OUT-4: Monthly Summary PDF (2 pages)
- Cohort statistics
- Progress charts
- Risk register
- Next month plan

---

## Output Footer (always append)

```
─────────────────────────────────
💾 Save: D:\arjin-vault\ALIVE\A2\[IM]_[Month].md
📋 Next: Share A3 Deep Analysis for at-risk companies
🔗 Agent: A2 IM | ALIVE Framework V2.0
```
