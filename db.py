"""
AAOS Database Layer — PostgreSQL (Railway)
ไม่ต้องใช้ ANTHROPIC_API_KEY
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./aaos_local.db")
_is_sqlite = DATABASE_URL.startswith("sqlite")
engine = create_engine(DATABASE_URL)

# SQLite ใช้ INTEGER PRIMARY KEY AUTOINCREMENT แทน SERIAL
# SQLite ใช้ CURRENT_TIMESTAMP แทน NOW()
_PK = "INTEGER PRIMARY KEY AUTOINCREMENT" if _is_sqlite else "SERIAL PRIMARY KEY"
_NOW = "CURRENT_TIMESTAMP" if _is_sqlite else "NOW()"


def init_db():
    """สร้าง tables ถ้ายังไม่มี"""
    with engine.connect() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS assessments (
                id          {_PK},
                company     TEXT NOT NULL,
                part        TEXT NOT NULL,
                score       INTEGER NOT NULL,
                max_score   INTEGER NOT NULL,
                level       TEXT,
                passed      BOOLEAN,
                assessed_at TIMESTAMP DEFAULT {_NOW}
            )
        """))
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS overall_scores (
                id          {_PK},
                company     TEXT NOT NULL,
                project     TEXT,
                score_a     INTEGER,
                score_b     INTEGER,
                score_c     INTEGER,
                score_d     INTEGER,
                total       INTEGER,
                grade       TEXT,
                level       TEXT,
                funding     TEXT,
                assessed_at TIMESTAMP DEFAULT {_NOW}
            )
        """))
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS sroi_records (
                id              {_PK},
                company         TEXT NOT NULL,
                investment      FLOAT,
                gross_annual    FLOAT,
                duration_yr     INTEGER,
                sroi_base       FLOAT,
                sroi_pessimistic FLOAT,
                sroi_optimistic  FLOAT,
                pv_base         FLOAT,
                net_factor      FLOAT,
                calculated_at   TIMESTAMP DEFAULT {_NOW}
            )
        """))
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS coaching_sessions (
                id           {_PK},
                company      TEXT NOT NULL,
                session_no   INTEGER,
                focus        TEXT,
                score_before INTEGER,
                score_after  INTEGER,
                gain         INTEGER,
                notes        TEXT,
                status       TEXT DEFAULT 'In Progress',
                logged_at    TIMESTAMP DEFAULT {_NOW}
            )
        """))
        conn.commit()


# ── Assessment CRUD ──────────────────────────────────────
def save_score(company: str, part: str, score: int,
               max_score: int, level: str, passed: bool):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO assessments
                (company, part, score, max_score, level, passed)
            VALUES
                (:company, :part, :score, :max_score, :level, :passed)
        """), {"company": company, "part": part, "score": score,
               "max_score": max_score, "level": level, "passed": passed})
        conn.commit()


def save_overall(company: str, project: str, score_a: int,
                 score_b: int, score_c: int, score_d: int,
                 total: int, grade: str, level: str, funding: str):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO overall_scores
                (company, project, score_a, score_b, score_c,
                 score_d, total, grade, level, funding)
            VALUES
                (:company, :project, :score_a, :score_b, :score_c,
                 :score_d, :total, :grade, :level, :funding)
        """), {"company": company, "project": project,
               "score_a": score_a, "score_b": score_b,
               "score_c": score_c, "score_d": score_d,
               "total": total, "grade": grade,
               "level": level, "funding": funding})
        conn.commit()


def save_sroi(company: str, investment: float, gross_annual: float,
              duration_yr: int, sroi_base: float, sroi_pess: float,
              sroi_opt: float, pv_base: float, net_factor: float):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO sroi_records
                (company, investment, gross_annual, duration_yr,
                 sroi_base, sroi_pessimistic, sroi_optimistic,
                 pv_base, net_factor)
            VALUES
                (:company, :investment, :gross_annual, :duration_yr,
                 :sroi_base, :sroi_pess, :sroi_opt, :pv_base, :net_factor)
        """), {"company": company, "investment": investment,
               "gross_annual": gross_annual, "duration_yr": duration_yr,
               "sroi_base": sroi_base, "sroi_pess": sroi_pess,
               "sroi_opt": sroi_opt, "pv_base": pv_base,
               "net_factor": net_factor})
        conn.commit()


def save_session(company: str, session_no: int, focus: str,
                 score_before: int, score_after: int, notes: str):
    gain = score_after - score_before
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO coaching_sessions
                (company, session_no, focus, score_before,
                 score_after, gain, notes)
            VALUES
                (:company, :session_no, :focus, :score_before,
                 :score_after, :gain, :notes)
        """), {"company": company, "session_no": session_no,
               "focus": focus, "score_before": score_before,
               "score_after": score_after, "gain": gain,
               "notes": notes})
        conn.commit()


def get_assessment_history(company: str) -> list:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT * FROM overall_scores
            WHERE company = :company
            ORDER BY assessed_at DESC
            LIMIT 20
        """), {"company": company}).fetchall()
        return [dict(r._mapping) for r in rows]


def get_coaching_log(company: str) -> list:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT * FROM coaching_sessions
            WHERE company = :company
            ORDER BY logged_at DESC
        """), {"company": company}).fetchall()
        return [dict(r._mapping) for r in rows]
