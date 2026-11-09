import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import DB_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date TEXT NOT NULL,
                entry_time TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                raw_transcript TEXT,
                image_description TEXT,
                image_path TEXT,
                audio_path TEXT,
                mood TEXT DEFAULT 'Bình yên',
                mood_emoji TEXT DEFAULT '🌿',
                tags TEXT DEFAULT '',
                time_of_day TEXT DEFAULT 'Ngày',
                is_favorite INTEGER DEFAULT 0,
                ai_generated INTEGER DEFAULT 0
            );
        """)
        
        # Indexes for fast querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_date ON entries(entry_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_created ON entries(created_at DESC);")
        
        # Daily summaries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summaries (
                date TEXT PRIMARY KEY,
                summary TEXT NOT NULL,
                mood_overview TEXT,
                highlights TEXT,
                created_at TEXT NOT NULL
            );
        """)
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)
        
        # Default settings if not already present
        defaults = {
            "ai_provider": "gemini",
            "gemini_model": "gemini-2.5-flash",
            "gemini_api_key": "",
            "openai_api_key": "",
            "openai_model": "gpt-4o-mini",
            "ai_tone": "chan_that",
            "auto_fill_daily": "1"
        }
        for k, v in defaults.items():
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
            
        conn.commit()

# --- Entry Queries ---

def create_entry(data: Dict[str, Any]) -> int:
    now = datetime.now()
    entry_date = data.get("entry_date") or now.strftime("%Y-%m-%d")
    entry_time = data.get("entry_time") or now.strftime("%H:%M:%S")
    created_at = data.get("created_at") or now.isoformat()
    
    tags = data.get("tags", "")
    if isinstance(tags, list):
        tags = ",".join(tags)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO entries (
                entry_date, entry_time, created_at, updated_at,
                title, content, raw_transcript, image_description,
                image_path, audio_path, mood, mood_emoji,
                tags, time_of_day, is_favorite, ai_generated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_date,
            entry_time,
            created_at,
            created_at,
            data.get("title", "Khoảnh khắc mới"),
            data.get("content", ""),
            data.get("raw_transcript", ""),
            data.get("image_description", ""),
            data.get("image_path", ""),
            data.get("audio_path", ""),
            data.get("mood", "Bình yên"),
            data.get("mood_emoji", "🌿"),
            tags,
            data.get("time_of_day", "Ngày"),
            1 if data.get("is_favorite") else 0,
            1 if data.get("ai_generated") else 0
        ))
        conn.commit()
        return cursor.lastrowid

def get_entry(entry_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_entries(date: Optional[str] = None, keyword: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM entries WHERE 1=1"
        params: List[Any] = []
        
        if date:
            query += " AND entry_date = ?"
            params.append(date)
            
        if keyword:
            query += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ? OR raw_transcript LIKE ?)"
            pattern = f"%{keyword}%"
            params.extend([pattern, pattern, pattern, pattern])
            
        query += " ORDER BY entry_date DESC, entry_time DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def update_entry(entry_id: int, data: Dict[str, Any]) -> bool:
    fields = []
    values = []
    now_iso = datetime.now().isoformat()
    
    for key in ["title", "content", "raw_transcript", "image_description", "image_path", "audio_path", "mood", "mood_emoji", "tags", "time_of_day", "is_favorite", "entry_date", "entry_time"]:
        if key in data:
            val = data[key]
            if key == "tags" and isinstance(val, list):
                val = ",".join(val)
            if key == "is_favorite":
                val = 1 if val else 0
            fields.append(f"{key} = ?")
            values.append(val)
            
    if not fields:
        return False
        
    fields.append("updated_at = ?")
    values.append(now_iso)
    values.append(entry_id)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE entries SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        return cursor.rowcount > 0

def delete_entry(entry_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()
        return cursor.rowcount > 0

def toggle_favorite(entry_id: int) -> Optional[bool]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_favorite FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        if not row:
            return None
        new_val = 0 if row["is_favorite"] else 1
        cursor.execute("UPDATE entries SET is_favorite = ?, updated_at = ? WHERE id = ?", (new_val, datetime.now().isoformat(), entry_id))
        conn.commit()
        return bool(new_val)

def get_entry_dates() -> List[Dict[str, Any]]:
    """Returns list of distinct dates with entry count."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT entry_date as date, COUNT(*) as count 
            FROM entries 
            GROUP BY entry_date 
            ORDER BY entry_date DESC
        """)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def get_stats() -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total_entries FROM entries")
        total_entries = cursor.fetchone()["total_entries"]
        
        cursor.execute("SELECT COUNT(DISTINCT entry_date) as total_days FROM entries")
        total_days = cursor.fetchone()["total_days"]
        
        cursor.execute("SELECT COUNT(*) as total_images FROM entries WHERE image_path IS NOT NULL AND image_path != ''")
        total_images = cursor.fetchone()["total_images"]
        
        cursor.execute("SELECT COUNT(*) as total_audios FROM entries WHERE audio_path IS NOT NULL AND audio_path != ''")
        total_audios = cursor.fetchone()["total_audios"]
        
        cursor.execute("SELECT COUNT(*) as total_favorites FROM entries WHERE is_favorite = 1")
        total_favorites = cursor.fetchone()["total_favorites"]
        
        return {
            "total_entries": total_entries,
            "total_days": total_days,
            "total_images": total_images,
            "total_audios": total_audios,
            "total_favorites": total_favorites
        }

# --- Daily Summaries ---

def get_daily_summary(date: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_summaries WHERE date = ?", (date,))
        row = cursor.fetchone()
        return dict(row) if row else None

def save_daily_summary(date: str, summary: str, mood_overview: str = "", highlights: str = "") -> None:
    now_iso = datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO daily_summaries (date, summary, mood_overview, highlights, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                summary = excluded.summary,
                mood_overview = excluded.mood_overview,
                highlights = excluded.highlights,
                created_at = excluded.created_at
        """, (date, summary, mood_overview, highlights, now_iso))
        conn.commit()

# --- Settings ---

def get_setting(key: str, default: str = "") -> str:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

def get_all_settings() -> Dict[str, str]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        return {r["key"]: r["value"] for r in rows}

def set_setting(key: str, value: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))
        conn.commit()

def set_multiple_settings(settings: Dict[str, str]) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        for k, v in settings.items():
            cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (k, str(v)))
        conn.commit()
