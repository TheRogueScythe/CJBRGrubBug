import sqlite3
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()
# Build path to users.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'users.db')

# Adds admin to the database using command line input
def AddAdminToDB():
	print("Add Admin to User Database")
	# Prompt for admin credentials
	username = input("Enter admin username: ")
	password = input("Enter admin password: ")
	# Input validation
	if not username or not password:
		print("Username and password cannot be empty.")
		return
    # Password hashing with bcrypt
	hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
	tag = "admin"

	try:
		conn = sqlite3.connect(DB_PATH)
		c = conn.cursor()
		# Inserts admin into user database
		c.execute(
			'INSERT INTO users (username, password, tag) VALUES (?, ?, ?)',
			(username, hashed_pw.decode('utf-8'), 'admin')
		)
		conn.commit()
		print(f"Admin user: '{username}' added successfully.")
	except sqlite3.IntegrityError:
		# Error handling for duplicate usernames
		print(f"Username '{username}' already exists.")
	except sqlite3.Error as e:
		# Logging for database errors
		print(f"Database error: {e}")
	finally:
		conn.close()

# Run directly from command line
if __name__ == '__main__':
    AddAdminToDB()