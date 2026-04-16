# Literature Sources & Evidence Reference
## ALIVE Framework V2.0 | A3 IBDS Agent
## Source: Scite MCP + Curated Thai/International Databases
## Updated: 2026-04-16

---

## Evidence Pyramid

```
                    ⭐ Tier 1 (Strongest)
                 ┌─────────────────────┐
                 │ Systematic Review   │
                 │ Meta-analysis       │
                 └─────────────────────┘
              ┌─────────────────────────────┐
              │ RCT / Experimental          │
              │ Peer-reviewed Q1/Q2         │
              └─────────────────────────────┘
           ┌───────────────────────────────────┐
           │ Observational / Case-control      │
           │ Peer-reviewed Q3/Q4               │
           └───────────────────────────────────┘
        ┌─────────────────────────────────────────┐
        │ Government report / Grey literature     │
        │ Working papers                          │
        └─────────────────────────────────────────┘
     ┌───────────────────────────────────────────────┐
     │ Industry report / News / Blog                 │ Tier 5 (Weakest)
     └───────────────────────────────────────────────┘
```

---

## Evidence Quality Rating (for IBDS use)

| Rating | Criteria | Use Case |
|--------|----------|----------|
| 🌟 **Strong** | Peer-reviewed Q1/Q2 + >10 citations + direct relevance | Headline claims |
| ⭐ **Medium** | Peer-reviewed Q3/Q4 OR indirect relevance OR Tier 3 | Supporting claims |
| ⚠️ **Weak** | Grey literature, blog, industry report without peer review | Context only — must flag |
| ❌ **Missing** | No supporting evidence found | Flag as assumption |

---

## Primary Databases (by Focus)

### For Scientific Literature
| Source | Access | Focus |
|--------|--------|-------|
| **Scite** (MCP) | ⭐ Primary tool | Smart Citations, full-text |
| PubMed | Open | Biomedical |
| Web of Science | Subscription | Multi-disciplinary |
| Scopus | Subscription | Multi-disciplinary |
| Google Scholar | Open | Broad coverage |
| Semantic Scholar | Open | AI-powered |

### For Thai Research
| Source | Access | Focus |
|--------|--------|-------|
| **ThaiJO** | Open | Thai journals |
| **TCI** (Thai Citation Index) | Open | Thai citation metrics |
| สำนักงานวิจัยแห่งชาติ (NRCT) | Portal | Thai research grants |
| สกสว. Digital Library | Portal | ววน. outputs |
| Chula/Mahidol/KU repositories | Institutional | Thesis & dissertations |

### For Policy Evidence
| Source | Focus |
|--------|-------|
| TDRI | Thai economic policy |
| HITAP | Thai health technology assessment |
| สภาพัฒน์ฯ (NESDC) | National development plans |
| OECD iLibrary | International benchmark |
| World Bank Open Data | Development indicators |

### For Carbon/Environmental
| Source | Focus |
|--------|-------|
| TGO | Thai carbon data |
| IPCC Reports | Climate science |
| IEA | Energy statistics |
| UNEP DTU | Technology transfer |

---

## Using Scite MCP — Best Practices

### Discovery Phase
```
search_literature(term="<domain keywords>", num_results=5)
```
- ใช้ domain-specific vocabulary
- Boolean: AND, OR, NOT
- Phrase search: "exact phrase"

### Reading Phase
```
search_literature(
  dois=["10.xxxx/yyyy"],
  term="methods methodology"
)
```
Extract specific sections:
- `"introduction background"` → motivation/context
- `"methods methodology"` → how the study was done
- `"results findings"` → what was found
- `"discussion conclusion"` → interpretation

### Quality Check
- ALWAYS check `editorialNotices` for retractions
- Construct links as `https://doi.org/{doi}`
- NEVER cite papers not retrieved through the tool

---

## Citation Format (APA 7th)

### In-text
- Single author: `(Smith, 2023)`
- Two authors: `(Smith & Jones, 2023)`
- 3+ authors: `(Smith et al., 2023)`
- Direct quote: `(Smith, 2023, p. 45)`

### Reference List
```
Smith, J., Jones, A., & Brown, C. (2023). Title of the paper.
  *Journal Name*, 45(3), 123-145. https://doi.org/10.xxxx/yyyy
```

### Thai Citations
```
สุรศักดิ์ วงศ์รัตนสมบัติ. (2565). ชื่อบทความ. *ชื่อวารสาร*, 12(2), 45-67.
```

---

## Evidence Search Strategy per Impact Dimension

### 1. Understanding & Awareness
- Keywords: knowledge diffusion, awareness campaign, citation impact
- Sources: Scite, Google Scholar
- Sample claim: "โครงการสร้าง awareness >10,000 คน"

### 2. Attitudinal / Behavior Change
- Keywords: behavior change, social norm, attitude shift
- Sources: Psychology/sociology journals
- Sample claim: "เปลี่ยนพฤติกรรมเกษตรกร 60%"

### 3. Economic
- Keywords: economic impact, SROI, cost-benefit, multiplier
- Sources: TDRI, World Bank, IMF
- Sample claim: "เพิ่มรายได้ครัวเรือน 15,000 THB/ปี"

### 4. Environmental
- Keywords: carbon reduction, biodiversity, sustainability
- Sources: TGO, IPCC, UNEP
- Sample claim: "ลด CO₂ 1,000 tCO₂e/yr"

### 5. Health & Well-being
- Keywords: DALY, quality of life, health outcome
- Sources: HITAP, PubMed, WHO
- Sample claim: "ลด DALY 500 units"

### 6. Policy (ววน. Alignment)
- Keywords: policy impact, standard adoption, regulation
- Sources: สภาพัฒน์ฯ, สกสว., OECD
- Sample claim: "เข้าสู่แผน ววน. Platform 3"

### 7. Cultural
- Keywords: soft power, cultural economy, heritage
- Sources: UNESCO, DEPA, culture ministry
- Sample claim: "เสริมสร้างเอกลักษณ์ไทย"

---

## Unsupported Claims — Flag Protocol

เมื่อค้นหาแล้ว**ไม่พบ** evidence ที่ Strong/Medium:

```markdown
⚠️ **UNSUPPORTED CLAIM FLAG**
Claim: [quoted from proposal]
Location: [section/page in proposal]
Search attempted: [search terms used]
Result: No peer-reviewed evidence found
Recommendation:
  - [ ] Remove claim, OR
  - [ ] Soften to "proposed" / "anticipated"
  - [ ] Add primary data collection plan
  - [ ] Cite grey literature + flag limitations
```

---

## Anti-Patterns (Avoid These)

❌ **Citation Laundering:** Citing a paper that itself cites weakly
❌ **Cherry-picking:** Ignoring contradicting evidence
❌ **Context collapse:** Using developed-country data for Thai rural context without adjustment
❌ **Age abuse:** Citing 20-year-old paper as if current
❌ **Predatory journals:** Papers in non-indexed journals without peer review
❌ **Retracted papers:** Always check editorialNotices

---

## Literature Evidence Pack Format

### Structure per Dimension
```markdown
### [Impact Dimension Name]

**Claim from Proposal:** [exact quote]

**Supporting Evidence:**
1. 🌟 [Author et al. (Year)](https://doi.org/...) —
   "[relevant excerpt, ~50 words]"
2. ⭐ [Author (Year)](https://doi.org/...) —
   "[relevant excerpt]"

**Evidence Quality:** Strong / Medium / Weak / Missing
**Relevance to Thai Context:** High / Medium / Low / Adaptation needed

**References:**
1. Full APA citation
2. Full APA citation
```

---

## Thai Context Adaptation

เมื่อใช้ international evidence สำหรับ Thai context ต้องปรับ:

| Adjustment | Factor | Use Case |
|------------|:------:|----------|
| PPP adjustment (USD → THB value) | × 0.35 | Income, cost data |
| Climate adjustment (temperate → tropical) | variable | Agriculture, energy |
| Cultural adjustment | qualitative | Social programs |
| Infrastructure adjustment | variable | Technology adoption |

---

## References (meta)
- American Psychological Association. (2019). *Publication Manual (7th ed.)*.
- Scite. *Smart Citations Methodology*. https://scite.ai
- Cochrane. *Evidence hierarchy guidelines*.
- WHO. *Grading of Evidence framework*.
