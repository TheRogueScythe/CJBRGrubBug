import sqlite3, random

# Generates challenge completion column names
def completeCols(total: int):
    return [f"A{n:02d}_2021_done" for n in range(1, total + 1)]

# Assigns a random unseen challenge and tracks current challenge
def chooseRandom(username: str, DB_PATH: str, total: int = 10):
    cols = completeCols(total)
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    try:
        curs = conn.cursor()
        # Locks the database for atomic updates, prevent race conditions
        curs.execute("BEGIN IMMEDIATE")
        # Checks user's current challenge and all challenge completion flags
        curs.execute(f"SELECT Current_Challenge, {', '.join(cols)} FROM users WHERE username = ?", (username,))
        row = curs.fetchone()
        if not row:
            conn.rollback()
            return None
        current_challenge = row[0]
        completion_flags = row[1:]
        # Reuses challenge if incomplete
        if current_challenge and 1 <= current_challenge <= total:
            if completion_flags[current_challenge - 1] in (0, None):
                conn.commit()
                return current_challenge
        # Finds all unseen challenges
        unseen = [i + 1 for i, val in enumerate(completion_flags) if val in (0, None)]
        if not unseen:
            conn.rollback()
            return None
        # Randomly chooses one unseen challenge
        rand_choice = random.choice(unseen)
        # Updates Current_Challenge in users.db
        curs.execute("UPDATE users SET Current_Challenge = ? WHERE username = ?", (rand_choice, username))
        conn.commit()
        return rand_choice
    except sqlite3.Error:
        try:
            conn.rollback()
        except Exception:
            pass
        return None
    finally:
        conn.close()

# Returns list of challenges that have been seen
def getSeenList(username: str, DB_PATH: str, total: int = 10):
    cols = completeCols(total)
    try:
        conn = sqlite3.connect(DB_PATH)
        curs = conn.cursor()
        # Checks user's challenge completion flags
        curs.execute(f"SELECT {', '.join(cols)} FROM users WHERE username = ?", (username,))
        row = curs.fetchone()
        conn.close()
        if row is None:
            return None
        # Return list of completed challenges
        return [i + 1 for i, val in enumerate(row) if val]
    except sqlite3.Error:
        return None

# Returns TRUE if all challenges are seen
def allComplete(username: str, DB_PATH: str, total: int = 10):
    seen = getSeenList(username, DB_PATH, total)
    return bool(seen) and len(seen) >= total

# Resets completion flags
def reset(username: str, DB_PATH: str, total: int = 10):
    cols = completeCols(total)
    set = ", ".join(f"{c} = 0" for c in cols)
    try:
        with sqlite3.connect(DB_PATH) as conn:
            curs = conn.cursor()
            # Reset all challenge flags to unseen
            curs.execute(f"UPDATE users SET {set} WHERE username = ?", (username,))
            conn.commit()
            conn.close()
        return True
    except sqlite3.Error:
        return False