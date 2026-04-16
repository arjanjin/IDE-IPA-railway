# IDE-IPA Analyzer Pro 🚀
**Innovation Driven Enterprise — Impact Performance Assessment**
ไม่ต้องใช้ `ANTHROPIC_API_KEY` — Claude Max Plan ทำ AI ทั้งหมด

---

## Architecture

```
claude.ai (Max Plan)
    ↕ MCP (HTTPS)
IDE-IPA Analyzer Pro Server         ← Tools + Database + Skills
    ├── /mcp                        ← Tool Manifest
    ├── /mcp/tools/...              ← 7 Analyzer Pro Tools
    ├── skills/                     ← 4 AI Agent Skills (A1–A4)
    │   ├── A1 Candidate            ← IDEs Readiness + Gap
    │   ├── A2 IM                   ← Coaching + Portfolio
    │   ├── A3 IBDS                 ← Full Report + Presentation
    │   └── A4 Funder               ← SROI + Policy Brief
    ├── PostgreSQL                  ← Assessment history (persistent)
    └── /data/chromadb              ← Vector memory (Railway volume)
```

## 7 Tools

| Tool | Endpoint | Method |
|------|----------|--------|
| load_framework | `/mcp/tools/analyzer_pro_load_framework` | GET |
| score_part_a | `/mcp/tools/analyzer_pro_score_part_a` | POST |
| score_part_d | `/mcp/tools/analyzer_pro_score_part_d` | POST |
| overall_score | `/mcp/tools/analyzer_pro_overall_score` | POST |
| calculate_sroi | `/mcp/tools/analyzer_pro_calculate_sroi` | POST |
| log_coaching | `/mcp/tools/analyzer_pro_log_coaching_session` | POST |
| get_history | `/mcp/tools/analyzer_pro_get_history/{company}` | GET |

---

## Deploy to Railway

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "IDE-IPA Analyzer Pro v2.0"
git remote add origin https://github.com/arjanjin/IDE-IPA-railway.git
git push -u origin main
```

### 2. Create Railway Project
```bash
npm install -g @railway/cli
railway login
railway init          # ชื่อ: ide-ipa-analyzer-pro
railway add postgresql
railway up
```

### 3. Set Environment Variables (Railway Dashboard)
```
DATABASE_URL   → auto-injected by Railway PostgreSQL plugin
CHROMA_PATH    → /data/chromadb
MCP_SECRET     → your-secret-key
AAOS_LEVEL     → 5.5
```

### 4. Get HTTPS URL
```bash
railway domain
# → https://ide-ipa-analyzer-pro.railway.app ✅
```

---

## Claude MCP Config

เพิ่มใน `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ide-ipa-analyzer-pro": {
      "type": "url",
      "url": "https://ide-ipa-analyzer-pro.railway.app/mcp",
      "headers": {
        "x-mcp-secret": "your-secret-key"
      }
    }
  }
}
```

---

## Local Development (ทดสอบก่อน deploy)

```bash
# 1. สร้าง virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env
cp .env.example .env
# แก้ไข DATABASE_URL เป็น SQLite สำหรับ local:
# DATABASE_URL=sqlite:///./aaos_local.db

# 4. Run
uvicorn main:app --reload --port 8000

# 5. Test
curl http://localhost:8000/health
curl http://localhost:8000/mcp
```

---

## Cost Estimate

| Service | Cost/month |
|---------|:----------:|
| Railway App | ~$2 |
| PostgreSQL | ~$1 |
| Volume (ChromaDB) | ~$0.25/GB |
| **ANTHROPIC_API_KEY** | **$0** |
| **Total** | **~$3–4** |

---

## 4 AI Agent Skills

Claude ใช้ skills เหล่านี้เป็น prompt/context สำหรับวิเคราะห์ตามบทบาทของ stakeholder แต่ละกลุ่ม

| Agent | Skill | Stakeholder | หน้าที่หลัก |
|:-----:|-------|-------------|------------|
| A1 | `ide-ipa-a1-candidate` | บริษัท (ME/LE) | ประเมิน IDEs Readiness, Gap Analysis, Quick Wins |
| A2 | `ide-ipa-a2-im` | Intermediary | Coaching Plan, Portfolio Tracking, Monthly Report |
| A3 | `ide-ipa-a3-ibds` | IBDS (ที่ปรึกษา) | Full IPA Report, Radar Chart, Presentation |
| A4 | `ide-ipa-a4-funder` | บพข./สกสว. | SROI Calculation, Policy Brief, Funding Decision |

### Shared Framework
- `ide-ipa-framework-v2.1` — IDE-IPA Scoring Framework v2.1 (100 คะแนน: A:28 / B:22 / C:25 / D:25)

### Agent Workflow

```
บริษัท (ME/LE)          Intermediary          IBDS (ที่ปรึกษา)        บพข./สกสว.
      │                      │                      │                    │
  ┌───▼───┐              ┌───▼───┐              ┌───▼───┐           ┌───▼───┐
  │  A1   │──Scorecard──▶│  A2   │──At-Risk───▶│  A3   │──Report──▶│  A4   │
  │Candidate│             │  IM   │              │ IBDS  │           │Funder │
  └───────┘              └───────┘              └───────┘           └───────┘
  IDEs Readiness         Coaching Plan         Full IPA Report      SROI + Policy
  Gap Analysis           Progress Track        Presentation         Funding Decision
  Quick Wins             Monthly Report        Literature Pack      Portfolio Compare
```

### Output Deliverables

| Agent | Deliverables |
|:-----:|-------------|
| A1 | HTML Dashboard, Excel Scorecard, Gap Report, Quick Wins Checklist |
| A2 | Portfolio Dashboard, Coaching Report, Progress Excel, Monthly PDF |
| A3 | Full IPA Report (PDF), Visual Canvas (HTML), PPTX (15 slides), Radar Chart (SVG), Literature Pack |
| A4 | Policy Brief (PDF), SROI Excel (4 sheets), Funding Decision Matrix, Portfolio SROI |

---

## Project Structure

```
IDE-IPA-railway/
├── main.py                ← FastAPI + MCP endpoints
├── db.py                  ← PostgreSQL layer
├── tools/
│   ├── ide_ipa_tools.py   ← 7 Analyzer Pro tools (no AI calls)
│   └── l6_tools.py        ← L6 evaluation tools
├── skills/
│   ├── ide-ipa-framework-v2.1/
│   │   └── SKILL.md       ← Scoring Framework (shared reference)
│   ├── ide-ipa-a1-candidate/
│   │   └── SKILL.md       ← A1 Agent: บริษัท (ME/LE)
│   ├── ide-ipa-a2-im/
│   │   └── SKILL.md       ← A2 Agent: Intermediary
│   ├── ide-ipa-a3-ibds/
│   │   └── SKILL.md       ← A3 Agent: IBDS (ที่ปรึกษา)
│   └── ide-ipa-a4-funder/
│       └── SKILL.md       ← A4 Agent: บพข./สกสว.
├── requirements.txt
├── Dockerfile
├── railway.toml
├── .env.example
└── README.md
```

---

*IDE-IPA Analyzer Pro | AAOS KMITL*
*Assoc. Prof. Dr. Arjin Numsomran*
*Dept. of Instrumentation & Control Engineering, KMITL*
