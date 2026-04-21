import sqlite3
from config import Config

def get_conn():
    return sqlite3.connect(Config.DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        victim_name TEXT NOT NULL,
        platform TEXT NOT NULL,
        bullying_text TEXT NOT NULL,
        screenshot_path TEXT,
        toxic_score REAL,
        threat_score REAL,
        severity TEXT,
        legal_section TEXT,
        status TEXT DEFAULT 'Pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def insert_complaint(victim_name, platform, bullying_text, screenshot_path,
                     toxic_score, threat_score, severity, legal_section, status="Pending"):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO complaints (
            victim_name, platform, bullying_text, screenshot_path,
            toxic_score, threat_score, severity, legal_section, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (victim_name, platform, bullying_text, screenshot_path,
          toxic_score, threat_score, severity, legal_section, status))

    conn.commit()
    conn.close()

def fetch_recent(limit=10):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, victim_name, platform, severity, status, created_at
        FROM complaints
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_counts():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM complaints")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM complaints WHERE severity IN ('Medium','High') AND status='Resolved' ")
    detected = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'")
    resolved = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM complaints WHERE severity='Low'")
    low = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM complaints WHERE severity='Medium'")
    medium = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM complaints WHERE severity='High'")
    high = cur.fetchone()[0]

    conn.close()
    return {
        "total": total,
        "detected": detected,
        "resolved": resolved,
        "low": low,
        "medium": medium,
        "high": high
    }

def update_status(cid, new_status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE complaints
        SET status = ?
        WHERE id = ?
    """, (new_status, cid))
    conn.commit()
    conn.close()