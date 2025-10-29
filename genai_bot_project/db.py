# db.py
import sqlite3
import numpy as np
import pickle
from typing import List, Tuple

DB_PATH = "data/embeddings.db"

def _connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS docs (
        id INTEGER PRIMARY KEY,
        title TEXT,
        text TEXT,
        embedding BLOB,
        dim INTEGER
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cache (
        key TEXT PRIMARY KEY,
        embedding BLOB,
        dim INTEGER
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        user_id TEXT,
        ts INTEGER,
        role TEXT,
        text TEXT
    );
    """)
    conn.commit()
    return conn

def save_doc(title: str, text: str, embedding: np.ndarray):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO docs (title, text, embedding, dim) VALUES (?, ?, ?, ?)",
                (title, text, sqlite3.Binary(embedding.tobytes()), embedding.shape[0]))
    conn.commit()

def list_docs() -> List[Tuple[int,str,str]]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT id, title, text FROM docs")
    return cur.fetchall()

def load_all_embeddings():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT id, title, text, embedding, dim FROM docs")
    rows = cur.fetchall()
    out = []
    for r in rows:
        eid, title, text, emb_blob, dim = r
        emb = np.frombuffer(emb_blob, dtype=np.float32).reshape(dim,)
        out.append((eid, title, text, emb))
    return out

def cache_get(key: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT embedding, dim FROM cache WHERE key=?", (key,))
    r = cur.fetchone()
    if not r: return None
    emb_blob, dim = r
    return np.frombuffer(emb_blob, dtype=np.float32).reshape(dim,)

def cache_set(key: str, emb):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("REPLACE INTO cache (key, embedding, dim) VALUES (?, ?, ?)",
                (key, sqlite3.Binary(emb.tobytes()), emb.shape[0]))
    conn.commit()

def add_history(user_id: str, ts: int, role: str, text: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO history (user_id, ts, role, text) VALUES (?, ?, ?, ?)",
                (user_id, ts, role, text))
    conn.commit()

def get_history(user_id: str, limit=3):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT role, text FROM history WHERE user_id=? ORDER BY ts DESC LIMIT ?", (user_id, limit))
    rows = cur.fetchall()
    return rows
