import sqlite3
import os

# Path to your database
db_path = os.path.join("data", "embeddings.db")

#  Check if DB file exists
if not os.path.exists(db_path):
    print(f"⚠️ Database file not found at: {db_path}")
    print("Run telegram_bot.py once — it will auto-create the database.")
    exit()

try:
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check if tables exist
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()

    print(" Connected successfully to SQLite database!")
    print(f"Database path: {db_path}")
    print("Existing tables:")
    for t in tables:
        print("  -", t[0])

    # Optional: test a simple query
    if tables:
        table = tables[0][0]
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f" Table '{table}' has {count} rows.")
    else:
        print("⚠️ No tables found. They’ll be created when you run telegram_bot.py")

    conn.close()

except sqlite3.Error as e:
    print("❌ SQLite connection failed:", e)
