import os
import sqlite3

# Path to solutions.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOLUTIONS_DB_PATH = os.path.join(BASE_DIR, 'data', 'solutions.db')

# Challenge solutions and explanations
solutions_data = [
    ('A01_2021', 'GB{A01_INSECURE_LOGIN}', 'Login information is hardcoded in the HTML source code'),
    ('A02_2021', 'GB{A02_ENCRYPTED_MESSAGE}', 'Find a way to decript the encoded message, google a decoder'),
    ('A03_2021', 'GB{A03_INJECTION}', 'explanation/hint'),
    ('A04_2021', 'GB{A04_INSECURE_DEBUG}', 'Trigger debug mode by submitting an invalid input'),
    ('A05_2021', 'GB{A05_MISCONFIG}', 'Explore the exposed config directory for any confidential files'),
    ('A06_2021', 'GB{A06_OUTDATED_COMPONENTS}', 'Use the legacy search tool to enter a file or folder name'),
    ('A07_2021', 'GB{A07_AUTH_FAILURE}', 'Try entering commonly used or weak login credentials'),
    ('A08_2021', 'GB{A08_DATA_TAMPERING}', 'Try bypassing the integrity check with the special coupon code'),
    ('A09_2021', 'GB{A09_MONITORING_FAILURE}', 'Access the Security Dashboard by exploiting login credentials'),
    ('A10_2021', 'GB{A10_INTERNAL_RESOURCES}', 'Try finding the URL to the hidden menu')
]

def setup_solutions():
    conn = sqlite3.connect(SOLUTIONS_DB_PATH)
    curs = conn.cursor()

    # Create the solutions table
    curs.execute("""
        CREATE TABLE IF NOT EXISTS solutions (
            challenge_id TEXT PRIMARY KEY,
            flag TEXT NOT NULL,
            explanation TEXT
        );
    """)

    # Insert data using INSERT OR IGNORE to avoid duplicates
    curs.executemany("""
        INSERT OR IGNORE INTO solutions (challenge_id, flag, explanation)
        VALUES (?, ?, ?);
    """, solutions_data)

    conn.commit()
    conn.close()
    print("Solutions table created and populated in solutions.db")

# Run directly
if __name__ == '__main__':
    setup_solutions()