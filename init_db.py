import os
import sqlite3

# Build DB path relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'users.db')

# Make sure the data folder exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Connect to the database (creates file if it doesn't exist)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create the users table with progress columns
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        tag TEXT NOT NULL,
        Current_Challenge INTEGER DEFAULT 0,
        A01_2021_done INTEGER DEFAULT 0,
        A02_2021_done INTEGER DEFAULT 0,
        A03_2021_done INTEGER DEFAULT 0,
        A04_2021_done INTEGER DEFAULT 0,
        A05_2021_done INTEGER DEFAULT 0,
        A06_2021_done INTEGER DEFAULT 0,
        A07_2021_done INTEGER DEFAULT 0,
        A08_2021_done INTEGER DEFAULT 0,
        A09_2021_done INTEGER DEFAULT 0,
        A10_2021_done INTEGER DEFAULT 0
        
    )
''')

conn.commit()
conn.close()

print(f"Database created at {DB_PATH} with OSINT progress tracking columns.")
