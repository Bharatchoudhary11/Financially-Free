import sqlite3

DB_PATH = "data/vahan.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            vehicle_category TEXT NOT NULL,
            maker TEXT NOT NULL,
            registrations INTEGER NOT NULL
        )
    """)

    # Check if table already has data
    cursor.execute("SELECT COUNT(*) FROM registrations")
    count = cursor.fetchone()[0]
    if count == 0:
        # Insert some dummy sample data
        sample_data = [
            ('2025-01-01', '2W', 'Honda', 1200),
            ('2025-01-01', '4W', 'Maruti', 1500),
            ('2025-02-01', '2W', 'Yamaha', 900),
            ('2025-02-01', '4W', 'Hyundai', 1300),
            ('2025-03-01', '2W', 'Honda', 1400),
        ]
        cursor.executemany("""
            INSERT INTO registrations (date, vehicle_category, maker, registrations)
            VALUES (?, ?, ?, ?)
        """, sample_data)
        print(f"Inserted {len(sample_data)} sample rows.")

    conn.commit()
    conn.close()
    print("Database ready.")

if __name__ == "__main__":
    init_db()
