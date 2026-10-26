import sqlite3
from datetime import datetime

DB_PATH = "clearbrand.db"

KIND_PREFIX = {"guideline": "R", "fact": "F", "glossary": "G"}


def _now():
    return datetime.now().isoformat(timespec="seconds")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _execute(sql, params=()):
    conn = get_conn()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def _query(sql, params=()):
    conn = get_conn()
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def init_db():
    conn = get_conn()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                kind TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content_type TEXT NOT NULL,
                creator TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS revisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draft_id INTEGER NOT NULL,
                version INTEGER NOT NULL,
                content TEXT NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draft_id INTEGER NOT NULL,
                revision_id INTEGER NOT NULL,
                flagged_text TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                reason TEXT NOT NULL,
                source_code TEXT,
                suggestion TEXT,
                origin TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                dismiss_reason TEXT
            );
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draft_id INTEGER NOT NULL,
                author TEXT NOT NULL,
                role TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


# ---------- Sources: guidelines, approved facts, glossary ----------

def add_source(kind, text):
    prefix = KIND_PREFIX[kind]
    rows = _query(
        "SELECT COALESCE(MAX(CAST(SUBSTR(code, 3) AS INTEGER)), 0) + 1 AS n "
        "FROM sources WHERE kind = ?",
        (kind,),
    )
    code = f"{prefix}-{rows[0]['n']:02d}"
    _execute(
        "INSERT INTO sources (code, kind, text, created_at) VALUES (?, ?, ?, ?)",
        (code, kind, text.strip(), _now()),
    )
    return code


def list_sources(kind=None):
    if kind:
        return _query("SELECT * FROM sources WHERE kind = ? ORDER BY code", (kind,))
    return _query("SELECT * FROM sources ORDER BY kind, code")


def get_source(code):
    rows = _query("SELECT * FROM sources WHERE code = ?", (code,))
    return rows[0] if rows else None


def delete_source(code):
    _execute("DELETE FROM sources WHERE code = ?", (code,))


# ---------- Drafts and revisions ----------

def create_draft(title, content_type, creator, content):
    now = _now()
    draft_id = _execute(
        "INSERT INTO drafts (title, content_type, creator, status, created_at, updated_at) "
        "VALUES (?, ?, ?, 'Draft', ?, ?)",
        (title, content_type, creator, now, now),
    )
    add_revision(draft_id, content, note="First version")
    return draft_id


def add_revision(draft_id, content, note=""):
    rows = _query(
        "SELECT COALESCE(MAX(version), 0) + 1 AS v FROM revisions WHERE draft_id = ?",
        (draft_id,),
    )
    version = rows[0]["v"]
    revision_id = _execute(
        "INSERT INTO revisions (draft_id, version, content, note, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (draft_id, version, content, note, _now()),
    )
    _execute("UPDATE drafts SET updated_at = ? WHERE id = ?", (_now(), draft_id))
    return revision_id


def get_draft(draft_id):
    rows = _query("SELECT * FROM drafts WHERE id = ?", (draft_id,))
    return rows[0] if rows else None


def list_drafts(status=None):
    if status:
        return _query(
            "SELECT * FROM drafts WHERE status = ? ORDER BY updated_at DESC", (status,)
        )
    return _query("SELECT * FROM drafts ORDER BY updated_at DESC")


def update_draft_status(draft_id, status):
    _execute(
        "UPDATE drafts SET status = ?, updated_at = ? WHERE id = ?",
        (status, _now(), draft_id),
    )


def list_revisions(draft_id):
    return _query(
        "SELECT * FROM revisions WHERE draft_id = ? ORDER BY version", (draft_id,)
    )


def latest_revision(draft_id):
    rows = _query(
        "SELECT * FROM revisions WHERE draft_id = ? ORDER BY version DESC LIMIT 1",
        (draft_id,),
    )
    return rows[0] if rows else None


# ---------- Findings ----------

def save_findings(draft_id, revision_id, findings):
    for f in findings:
        _execute(
            "INSERT INTO findings (draft_id, revision_id, flagged_text, category, severity, "
            "reason, source_code, suggestion, origin) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                draft_id,
                revision_id,
                f["flagged_text"],
                f["category"],
                f["severity"],
                f["reason"],
                f.get("source_code"),
                f.get("suggestion"),
                f.get("origin", "rule"),
            ),
        )


def list_findings(draft_id, revision_id=None):
    if revision_id:
        return _query(
            "SELECT * FROM findings WHERE draft_id = ? AND revision_id = ? ORDER BY id",
            (draft_id, revision_id),
        )
    return _query("SELECT * FROM findings WHERE draft_id = ? ORDER BY id", (draft_id,))


def update_finding_status(finding_id, status, dismiss_reason=None):
    _execute(
        "UPDATE findings SET status = ?, dismiss_reason = ? WHERE id = ?",
        (status, dismiss_reason, finding_id),
    )


# ---------- Comments ----------

def add_comment(draft_id, author, role, body):
    _execute(
        "INSERT INTO comments (draft_id, author, role, body, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (draft_id, author, role, body.strip(), _now()),
    )


def list_comments(draft_id):
    return _query(
        "SELECT * FROM comments WHERE draft_id = ? ORDER BY id", (draft_id,)
    )