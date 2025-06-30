# companion_ai/memory.py
import sqlite3
import os
import json
from datetime import datetime

# Define database path
MODULE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(MODULE_DIR, '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DB_PATH = os.path.join(DATA_DIR, 'companion_ai.db')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            summary_text TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            insight_text TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"INFO: Database initialized at {DB_PATH}")

# Profile functions
def upsert_profile_fact(key: str, value: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_profile (key, value) 
        VALUES (?, ?)
    ''', (key, value))
    conn.commit()
    conn.close()

def get_profile_fact(key: str) -> str | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_profile_facts() -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM user_profile")
    results = cursor.fetchall()
    conn.close()
    return {row['key']: row['value'] for row in results}

# Summary functions
def add_summary(summary_text: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversation_summaries (summary_text) VALUES (?)", 
                   (summary_text,))
    conn.commit()
    conn.close()

def get_latest_summary(n: int = 1) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, summary_text 
        FROM conversation_summaries 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (n,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

# Insight functions
def add_insight(insight_text: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ai_insights (insight_text) VALUES (?)", 
                   (insight_text,))
    conn.commit()
    conn.close()

def get_latest_insights(n: int = 1) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, insight_text 
        FROM ai_insights 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (n,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

# Initialize database when imported
init_db()