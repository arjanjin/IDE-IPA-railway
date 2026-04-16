# SROI Standards Reference
## ALIVE Framework V2.0 | A4 Funder Agent
## Source: Social Value International (SVI) 7 Principles + Thai Public Sector Adaptation
## Updated: 2026-04-16

---

## SVI 7 Principles of SROI

| # | Principle | Application |
|:-:|-----------|-------------|
| 1 | **Involve Stakeholders** | ระบุและให้ผู้มีส่วนได้เสียช่วยกำหนด outcome |
| 2 | **Understand What Changes** | แยก output กับ outcome ให้ชัด ใช้ Theory of Change |
| 3 | **Value the Things That Matter** | ใช้ financial proxy ที่เชื่อมโยงกับ outcome จริง |
| 4 | **Include Only What Is Material** | ตัด outcome ที่ไม่ significant ออก |
| 5 | **Do Not Over-Claim** | หัก Deadweight / Attribution / Displacement |
| 6 | **Be Transparent** | เปิด assumption, data source, proxy ทุกตัว |
| 7 | **Verify the Result** | Sensitivity analysis + stakeholder review |

---

## SROI Type Selection

| Type | เมื่อใช้ | ความน่าเชื่อถือ |
|------|---------|----------------|
| **Forecast SROI** | ก่อนให้ทุน (ประเมินศักยภาพ) | ⭐⭐⭐ (based on assumption) |
| **Evaluative SROI** | หลังดำเนินโครงการ | ⭐⭐⭐⭐⭐ (based on actual data) |

**A4 Default:** Forecast SROI (Step 2.1)

---

## Analysis Period Rule (v2.1 fix)

| Project Duration | Analysis Period | Tail |
|:----------------:|:---------------:|:----:|
| 1 ปี | 2 ปี | +1 ปี |
| 2 ปี | 3 ปี | +1 ปี |
| 3 ปี | 5 ปี | +2 ปี |
| 5 ปี | 7 ปี | +2 ปี |

Rule: `project_years + 50% tail` (min 2, max 5 ปี tail)

---

## Discount Rate Standards

| Context | Rate | Justification |
|---------|:----:|---------------|
| **Thai public sector** ⭐ | **5%** | สกสว./บพข. standard, สภาพัฒน์ฯ |
| Private sector | 8–12% | Cost of capital |
| International aid | 3–5% | OECD-DAC |
| High-risk pilot | 10–15% | Risk premium |

**A4 Default:** 5% (เว้นแต่มีเหตุผลชัดเจน)

---

## Adjustment Factors (Scale-based)

### 1. Deadweight (DW)
ผลที่จะเกิดอยู่แล้วแม้ไม่มีโครงการ

| Budget (THB) | DW Range | Default |
|--------------|:--------:|:-------:|
| < 2M | 10–15% | 12% |
| 2–20M | 15–20% | 17% |
| 20–100M | 20–25% | 22% |
| > 100M | 25–30% | 27% |

### 2. Attribution (AT)
ส่วนที่ผลเกิดจากปัจจัยอื่น ไม่ใช่โครงการนี้

| Budget (THB) | AT Range | Default |
|--------------|:--------:|:-------:|
| < 2M | 15–20% | 17% |
| 2–20M | 20–25% | 22% |
| 20–100M | 25–30% | 27% |
| > 100M | 30–35% | 32% |

### 3. Displacement (DP)
ผลที่ย้ายจากที่อื่นมา (zero-sum)

| Budget (THB) | DP Range | Default |
|--------------|:--------:|:-------:|
| < 2M | 5% | 5% |
| 2–20M | 5–10% | 7% |
| 20–100M | 10% | 10% |
| > 100M | 10–15% | 12% |

### 4. Drop-off Rate (decay)

```
Year 1 → [project_duration]: 0% decay (active period)
Year [project+1]: 20% decay (1st tail year)
Year [project+2]: 36% decay (cumulative, 20% × 2)
Year [project+3]: 48.8% decay (cumulative)
```

Formula: `Drop-off(n) = 1 − (1 − 0.20)^(n − project_duration)`

---

## SROI Formula

```
Net Annual Value = Gross × (1 − DW) × (1 − AT) × (1 − DP)

PV(year n) = Net × Drop-off(n) / (1 + r)^n
              where r = 5%, n = year from start

Total PV = Σ PV(year n) for n = 1 to analysis_period

SROI Ratio = Total PV of Outcomes / Total Input
```

---

## Sensitivity Analysis (3 Scenarios — MANDATORY)

| Scenario | Proxy | DW | Expected Shift |
|----------|:-----:|:---:|:---------------:|
| **Pessimistic** | −20% | +10% | −30 to −40% |
| **Base Case** | Default | Default | Calculated |
| **Optimistic** | +20% | −5% | +25 to +35% |

**Report format:** `"SROI Range: [pess]x – [opti]x (Base: [base]x)"`

Rule: ไม่แนะนำให้ทุนหาก **Pessimistic < 1.0x**

---

## Interpretation Table

| SROI Base | บพข. Decision | เหตุผล |
|-----------|:------------:|--------|
| < 1.0x | ❌ Do not fund | ไม่คุ้มค่าเงินสาธารณะ |
| 1.0–1.5x | ⚠️ Conditional | ต้องแก้ proxy หรือ scope |
| 1.5–2.5x | ✅ Fund | คุ้มค่าเชิงสังคม |
| 2.5–4.0x | ✅✅ Priority fund | ผลตอบแทนสังคมสูง |
| > 4.0x | 🔍 Verify then fund | ตรวจ proxy source ให้แน่ใจก่อน |

---

## Common Pitfalls (Avoid)

1. **Over-claiming**: ไม่หัก DW/AT/DP → SROI เกินจริง
2. **Proxy inflation**: ใช้ค่า benchmark สูงสุดทุกตัว → ต้องใช้ conservative
3. **Missing sensitivity**: รายงานแค่ base case → ต้องมี 3 scenarios
4. **Short analysis period**: ประเมินแค่ปี 1 → ต้องมี tail years
5. **Ignoring drop-off**: outcome คงที่ทุกปี → ต้องมี decay
6. **No proxy source**: ไม่อ้างอิงที่มา → ต้อง cite (MEA/TGO/กระทรวง)

---

## References
- Social Value International. (2012). *A Guide to Social Return on Investment*.
- สกสว. (2565). *แนวทางการประเมินผลกระทบทางเศรษฐกิจและสังคม ววน.*
- บพข. (2566). *เกณฑ์การประเมิน SROI สำหรับโครงการ ววน.*
- HM Treasury. (2018). *The Green Book: Central Government Guidance on Appraisal*.
