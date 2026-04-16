# บพข. IM Reporting Requirements
## ALIVE Framework V2.0 | A2 IM (Intermediary) Agent
## Source: บพข. IM Guidelines + สกสว. Reporting Standards
## Updated: 2026-04-16

---

## Reporting Cadence (บพข.)

| Report | Frequency | Deadline | Format |
|--------|-----------|----------|--------|
| **Monthly Progress** | ทุกเดือน | Day 5 ของเดือนถัดไป | PDF 2 pages + Excel |
| **Quarterly Review** | ทุกไตรมาส | Day 15 | PDF 5 pages + presentation |
| **Mid-term Assessment** | 6 เดือน | Day 30 | Full report + site visit |
| **Annual Report** | ประจำปี | Day 60 ของปีถัดไป | Full annual package |
| **Ad-hoc Alerts** | ทันที | Within 24hr | Email + follow-up report |

---

## Monthly Progress Report (2 pages)

### Page 1: Cohort Summary

```
─────────────────────────────────────────
📊 MONTHLY IM REPORT — [Month Year]
─────────────────────────────────────────

IM Name:          [Organisation]
Reporting Period: [Month Year]
Contract:         [Contract No.]
Total Candidates: [N]

STATUS BREAKDOWN:
├── Ready to Apply:   [N] ([%])  ✅
├── In Progress:      [N] ([%])  🟡
├── At-Risk:          [N] ([%])  🔴
└── Completed:        [N] ([%])  ⭐

KEY METRICS:
- Cohort Average Score: [X]/100
- Score Change (MoM):   +[X] pts
- Top Performer:        [Company] — [Score]
- Most Improved:        [Company] — +[X] pts

COACHING DELIVERY:
- Sessions Delivered:   [N]
- Session Completion:   [%]
- Homework Completion:  [%]
- Coach Hours:          [N hrs]
```

### Page 2: Details + Plan

```
ACHIEVEMENTS THIS MONTH:
1. [Specific achievement + company name]
2. [Specific achievement]
3. [Specific achievement]

RISKS & MITIGATIONS:
| Risk | Company | Severity | Mitigation |
|------|---------|:--------:|------------|
| ...  | ...     | 🔴🟡🟢    | ...        |

NEXT MONTH PLAN:
- [Action 1 with owner + deadline]
- [Action 2]
- [Action 3]

KPI TRACKING:
- Sessions planned:     [N]
- Ready-to-apply target:[N]
- Risk resolution:      [N]
```

---

## Quarterly Review Report (5 pages)

### Structure
```
Page 1: Executive Summary
Page 2: Cohort Analysis (trend charts)
Page 3: Individual Company Profiles (top 5)
Page 4: Financial & Resource Utilization
Page 5: Next Quarter Strategy + Asks
```

### Required Charts
1. Score distribution histogram
2. Score progression over time (line chart)
3. Coaching hours vs score gain (scatter)
4. Sector breakdown (pie/bar)
5. Risk heat map

---

## Mid-term Assessment (6 months)

### Sections
1. **Cohort Health Check** — all companies reviewed
2. **Coaching Effectiveness** — score gain per coach hour
3. **At-Risk Intervention** — outcomes of escalations
4. **Best Practices Learned** — what worked / what didn't
5. **Financial Audit** — budget utilization vs plan
6. **Recommendations to บพข.** — system-level feedback
7. **Go/No-Go per Company** — who continues, who exits

### บพข. Site Visit
- Meet ≥ 3 companies from cohort
- Coach performance review
- Interview ≥ 2 founders
- Review random 5 session reports

---

## Annual Report Package

### Deliverables
1. Annual Narrative Report (20–30 pages PDF)
2. Full Cohort Excel (all data)
3. Financial Audit Report
4. Success Stories (≥ 3 case studies)
5. Lessons Learned Document
6. Policy Recommendations to บพข.
7. Next Year Proposal (if renewing contract)

---

## KPI Definitions (บพข. Official)

### Output KPIs
| KPI | Definition | Target |
|-----|-----------|--------|
| Candidates Enrolled | บริษัทที่เซ็น MOU เข้า cohort | per contract |
| Sessions Delivered | Coaching sessions completed | ≥ 6 per company |
| Coach Hours | ชั่วโมง coaching รวม | per contract |

### Outcome KPIs
| KPI | Definition | Target |
|-----|-----------|--------|
| **Ready-to-Apply Rate** | % บริษัทที่ผ่าน threshold ทุก part | ≥ 60% |
| **Score Improvement** | Avg score change per company | ≥ +20 pts |
| **Application Rate** | % บริษัทยื่น proposal | ≥ 50% |
| **Funded Rate** | % ที่ได้ทุน (ของที่ยื่น) | ≥ 40% |

### Impact KPIs
| KPI | Definition | Target |
|-----|-----------|--------|
| Cohort Total Funding Raised | รวมทุนที่บริษัทใน cohort ได้ | per contract |
| ววน. Platform Coverage | จำนวน Platform ที่มี funded project | ≥ 3 platforms |
| Industry Partnerships | MOUs ใหม่ที่เกิดจาก cohort | ≥ 5 per contract |

---

## Alert Protocols (Real-time)

### Alert Types

#### 🔴 Critical Alert (within 24 hours)
**Triggers:**
- Company drops below threshold in final month
- Fraud/ethics concern detected
- PI/team dissolution
- Partner withdrawal

**Action:**
- Immediate email to บพข. program officer
- Follow-up call within 48 hours
- Written incident report within 7 days

#### 🟡 Warning Alert (within 72 hours)
**Triggers:**
- At-risk criteria met (per coaching-framework.md)
- Sector eligibility question
- Budget overrun > 10%

**Action:**
- Email notification
- Include in next monthly report

#### 🟢 Milestone Alert (within 7 days)
**Triggers:**
- Company reaches Ready status
- Funded company announcement
- Success story milestone

**Action:**
- Report for comms/PR use
- Include in quarterly highlights

---

## Data Submission Standards

### Format Requirements
- **PDF:** Non-editable, signed by IM director
- **Excel:** `.xlsx` with data in defined schema
- **Charts:** Minimum 300 DPI PNG embedded
- **Language:** Thai + English bilingual for summary
- **File Naming:** `IM_[Name]_[ReportType]_[YYYYMM].pdf`

### Data Schema (Excel Cohort Tab)
```
| Field            | Type   | Required |
|------------------|--------|:--------:|
| Company_ID       | String | ✅       |
| Company_Name     | String | ✅       |
| Sector           | Enum   | ✅       |
| ววน._Platform   | Enum   | ✅       |
| TRL_Current      | Int    | ✅       |
| Score_A          | Int    | ✅       |
| Score_B          | Int    | ✅       |
| Score_C          | Int    | ✅       |
| Score_D          | Int    | ✅       |
| Total            | Int    | ✅       |
| Level            | Enum   | ✅       |
| Status           | Enum   | ✅       |
| Last_Session     | Date   | ✅       |
| Next_Session     | Date   | ✅       |
| Coach_Hours_Used | Float  | ✅       |
| Homework_Rate    | Float  | ✅       |
| Notes            | Text   | ⚠️       |
```

---

## Submission Channels

| Channel | Use For |
|---------|---------|
| บพข. Portal (online) | Monthly + Quarterly |
| Email to Program Officer | Ad-hoc alerts |
| Physical mail + digital copy | Annual report |
| In-person | Mid-term site visit |

---

## Penalty & Non-compliance

| Violation | Consequence |
|-----------|------------|
| Late monthly report (1–7 days) | Warning |
| Late monthly report (> 7 days) | 5% of monthly payment withheld |
| Missing quarterly report | 10% payment withheld + review |
| False/misleading data | Contract termination + blacklist |
| Missing annual report | No contract renewal |

---

## Template Files (Available on บพข. Portal)

1. `IM_Monthly_Template.xlsx`
2. `IM_Monthly_Template.docx`
3. `IM_Quarterly_Template.pptx`
4. `IM_CompanyProfile_Template.docx`
5. `IM_Alert_Template.docx`

---

## References
- บพข. (2566). *คู่มือการรายงานสำหรับหน่วยบริหารจัดการและส่งเสริมทุน IM*.
- สกสว. (2565). *มาตรฐานการรายงานผลการดำเนินงาน ววน.*.
- สภานโยบาย อววน. (2566). *แนวทางการติดตามและประเมินผล*.
