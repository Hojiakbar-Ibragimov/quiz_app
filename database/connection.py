from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "data" / "quiz.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def execute_commit(query, params=()):
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(query, params)

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(e)
    finally:
        conn.close()

def fetchone(query, params=()):
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(query, params)

        result = cur.fetchone()
        return result
    finally:
        conn.close()

def fetchall(query, params=()):
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(query, params)

        data = cur.fetchall()
        return data
    finally:
        conn.close()
