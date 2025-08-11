# src/ingest.py (no CSV needed)
import sqlite3

def init_db():
    conn = sqlite3.connect("data/vahan.db")
    conn.execute("SELECT COUNT(*) FROM registrations")  # test query
    conn.close()
    print("Database ready.")

if __name__ == "__main__":
    init_db()
