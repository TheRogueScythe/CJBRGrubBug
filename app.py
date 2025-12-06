from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from vulnRandomizer import chooseRandom, allComplete
import os
import sqlite3
import bcrypt
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24) # Secret key for signing session cookies (keep this safe in production)

# Get the folder where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Build a path to data/users.db inside the project
DB_PATH = os.path.join(BASE_DIR, 'data', 'users.db')
# Build path to table of solutions
SOLUTIONS_DB_PATH = os.path.join(BASE_DIR, 'data', 'solutions.db')

#
#
#   Helper functions
#
#

#check credentials
def check_credentials(username, password):
    # Return True if username exists and bcrypt verifies the password.
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Retrieve password hash for the given username
        c.execute('SELECT password FROM users WHERE username = ?', (username,))
        row = c.fetchone()
        conn.close()

        if row:
            stored_hash = row[0].encode('utf-8')  # back to bytes
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    
# create a user in the database
def create_user_in_db(username, password):
    # bcrypt requires bytes, so encode the password
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # Default tag
    tag = "student"
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Insert new user with default tag and hashed password
        c.execute(
            'INSERT INTO users (username, password, tag) VALUES (?, ?, ?)',
            (username, hashed_pw.decode('utf-8'), tag)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Username already exists
        return False
    except sqlite3.Error as e:
        # Log database errors
        print(f"Database error: {e}")
        return False



def mark_challenge_complete(username, challenge_num):
    # Ensure challenge_num is always two digits (01, 02, ..., 10)
    column = f"A{challenge_num:02d}_2021_done"
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Updates challenge column to mark it as complete
    c.execute(f"UPDATE users SET {column} = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

#
# 
#   User Main Pages
# 
# 

# Route for home page
@app.route('/')
def home():
    return render_template('loginPage.html')

# Login form submission
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    # Validate credentials in the database
    if check_credentials(username, password):
        # Store in session
        session['username'] = username
        return render_template('mainPage.html', user=username)
        # return redirect(url_for('randomizer'))
    else:
        return "Invalid credentials. Please try again."

# Admin specific login page
@app.route('/Admin')
def AdminHome():
    return render_template('loginPageAdmin.html')

# Admin login form submission
@app.route('/loginAdmin', methods=['POST'])
def loginAdmin():
    username = request.form['username']
    password = request.form['password']
    # Validate credentials
    if check_credentials(username, password):
        # Store in session
        session['username'] = username
        #ADD SESSION ASSIGNMENT FOR ADMIN TAG HERE
        return render_template('teacherPages/teacherHome.html', user=username)
    else:
        return "Invalid credentials. Please try again."

# Home page
@app.route('/mainpage')
def mainpage():
    if 'username' not in session:
        # Redirect to login if not authenticated
        return redirect(url_for('home')) 
    return render_template('mainPage.html', user=session['username'])

# Log out user and clear session data
@app.route('/logout')
def logout():
    # Remove username from session
    session.pop('username', None)
    return render_template('loginPage.html')

@app.route('/demopage')
def demopage():
    if 'username' not in session:
        # Redirect to login if not authenticated
        return redirect(url_for('home')) 
    return render_template('demos.html', user=session['username'])

#
# 
#   OWASP PAGES
# 
#  



# Route for OWASP challenge A01:2021
@app.route('/A01_2021')
def A01_2021():
    if 'username' not in session:
        return redirect(url_for('home'))

    
    return render_template('A01_2021/A01_2021.html')

# Helper function that identifies flags, alternative to hard-coding
def get_flag(challenge_id):
    conn = sqlite3.connect(SOLUTIONS_DB_PATH)
    curs = conn.cursor()
    curs.execute("SELECT flag FROM solutions WHERE challenge_id=?", (challenge_id,))
    row = curs.fetchone()
    conn.close()
    return row[0] if row else None

# Fetches A01 flag from solutions.db
@app.route("/flag/A01")
def flag_a01():
    if 'username' not in session:
        return redirect(url_for('home'))
    flag = get_flag("A01_2021")
    return jsonify({"flag": flag})

# Marks challenge A01:2021 as complete
@app.route('/A01_2021_Flag')
def A01_2021_Flag():
    if 'username' not in session:
        return redirect(url_for('home'))
    # Challenge marked as complete
    mark_challenge_complete(session['username'], 1)
    return render_template('A01_2021/A01_2021_Flag.html')

# Route for OWASP challenge A02:2021
@app.route('/A02_2021')
def A02_2021():
    if 'username' not in session:
        return redirect(url_for('home'))

    
    return render_template('A02_2021/A02_2021.html')

@app.route("/flag/A02")
def flag_a02():
    if 'username' not in session:
        return redirect(url_for('home'))

    flag = get_flag("A02_2021")  # reuse your helper
    return jsonify({"flag": flag})

# Marks challenge A02:2021 as complete
@app.route('/A02_2021_Flag')
def A02_2021_Flag():
    if 'username' not in session:
        return redirect(url_for('home'))
    # Challenge marked as complete
    mark_challenge_complete(session['username'], 2)
    return render_template('A02_2021/A02_2021_Flag.html')

# Route for OWASP challenge A03:2021
@app.route('/A03_2021')
def A03_2021():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        #Vulnerable query: string concatenation
        conn = sqlite3.connect(SOLUTIONS_DB_PATH)
        curs = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print("Executing:", query)  # for demo
        curs.execute(query)
        row = curs.fetchone()
        conn.close()

        if row:
            flag = get_flag("A03_2021")
            return render_template("A03_2021/A03_2021_Flag.html", flag=flag)
        else:
            return "Login failed. Try again."
    
    return render_template('A03_2021/A03_2021.html')

# Marks challenge A03:2021 as complete
@app.route('/A03_2021_Flag')
def A03_2021_Flag():
    if 'username' not in session:
        return redirect(url_for('home'))
    # Challenge marked as complete
    mark_challenge_complete(session['username'], 3)
    return render_template('A03_2021/A03_2021_Flag.html')

# Route for OWASP challenge A04:2021
@app.route('/A04_2021')
def A04_2021():
    if 'username' not in session:
        return redirect(url_for('home'))

    
    return render_template('A04_2021/A04_2021.html')

# Route for insecure default vulnerability
@app.route("/insecure-defaults", methods=["GET", "POST"])
def orderDebug():
    if request.method == "POST":
        item = request.form.get("item", "")
        quantity = int(request.form.get("quantity", ""))
        if quantity < 0:
            flag = get_flag("A04_2021")
            raise Exception(f"ERROR: Negative quantity not allowed! {flag}")
        return render_template("A04_2021/confirmation.html", item = item, quantity = quantity)
    return render_template("A04_2021/order.html")

# Marks challenge A04:2021 as complete
@app.route('/A04_2021_Flag')
def A04_2021_Flag():
    if 'username' not in session:
        return redirect(url_for('home'))
    # Challenge marked as complete
    mark_challenge_complete(session['username'], 4)
    return render_template('A04_2021/A04_2021_Flag.html')

# Route for OWASP challenge A05:2021
@app.route('/A05_2021')
def A05_2021():
    if 'username' not in session:
        return redirect(url_for('home'))

    
    return render_template('A05_2021/A05_2021.html')

# Route for exposed directory
@app.route("/configs")
def configs():
    return render_template("A05_2021/configs.html")

# Exposed directory vulnerability
@app.route("/configs/")
def configListing():
    files = ["settings.py", "db.conf", "secrets.txt"]
    return "<h3>Config Directory</h3><ul>" + "".join(
        f"<li><a href='/A05_2021/configs/{f}'>{f}</a></li>" for f in files
    ) + "</ul>"

# Flag
@app.route("/configs/secrets.txt")
def configFlag():
    flag = get_flag("A05_2021")
    return f"{flag}"

# Marks challenge A05:2021 as complete
@app.route('/A05_2021_Flag')
def A05_2021_Flag():
    if 'username' not in session:
        return redirect(url_for('home'))
    # Challenge marked as complete
    mark_challenge_complete(session['username'], 5)
    return render_template('A05_2021/A05_2021_Flag.html')

# Route for OWASP challenge A06:2021
@app.route('/A06_2021')
def A06_2021():
    if 'username' not in session:
        return redirect(url_for('home'))

    
    return render_template('A06_2021/A06_2021.html')

# Route for outdated search tool
@app.route("/unpatched-software", methods=["GET", "POST"])
def unpatched_search():
    query = None
    flag = get_flag("A06_2021")
    if request.method == "POST":
        query = request.form.get("search", "").strip()
    return render_template("A06_2021/search.html", query = query, flag = flag)

# Marks challenge A06:2021 as complete
@app.route('/A06_2021_Flag')
def A06_2021_Flag():
    if 'username' not in session:
        return redirect(url_for('home'))
    # Challenge marked as complete
    mark_challenge_complete(session['username'], 6)
    return render_template('A06_2021/A06_2021_Flag.html')

# Route for OWASP challenge A07:2021
@app.route('/A07_2021')
def A07_2021():
    if 'username' not in session:
        return redirect(url_for('home'))

    
    return render_template('A07_2021/A07_2021.html')

# Route for fake admin login page
@app.route("/weak-passwords", methods=["GET", "POST"])
def weakLogin():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "admin" and password == "password123":
            return redirect("/A07_2021/dashboard")
        else:
            error = "Invalid credentials"
    return render_template("A07_2021/login.html", error = error)

# Route for page that contains flag for A07:2021
@app.route("/dashboard")
def dashboard():
    flag = get_flag("A07_2021")
    return render_template("A07_2021/fakeAdmin.html", flag = flag)

# Marks challenge A07:2021 as complete
@app.route('/A07_2021_Flag')
def A07_2021_Flag():
    if 'username' not in session:
        return redirect(url_for('home'))
    # Challenge marked as complete
    mark_challenge_complete(session['username'], 7)
    return render_template('A07_2021/A07_2021_Flag.html')

# Route for OWASP challenge A08:2021
@app.route('/A08_2021')
def A08_2021():
    if 'username' not in session:
        return redirect(url_for('home'))

    
    return render_template('A08_2021/A08_2021.html')

# Route for tampered data integrity vulnerability
@app.route("/tampered-data", methods=["GET", "POST"])
def coupon():
    code = None
    flag = None
    if request.method == "POST":
        code = request.form.get("coupon", "").strip()
        if code == "FREEFOOD123":
            flag = get_flag("A08_2021")
    return render_template("A08_2021/couponCodes.html", code = code, flag = flag)

# Marks challenge A08:2021 as complete
@app.route('/A08_2021_Flag')
def A08_2021_Flag():
    if 'username' not in session:
        return redirect(url_for('home'))
    # Challenge marked as complete
    mark_challenge_complete(session['username'], 8)
    return render_template('A08_2021/A08_2021_Flag.html')

# Route for OWASP challenge A09:2021
@app.route('/A09_2021')
def A09_2021():
    if 'username' not in session:
        return redirect(url_for('home'))

    
    return render_template('A09_2021/A09_2021.html')

# Route for missing login attempt logs vulnerability
@app.route("/missing-login", methods=["GET", "POST"])
def failedLogin():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "admin" and password == "password1":
            return redirect("/A09_2021/secDashboard")
        else:
            error = "ERROR: username or password is incorrect"
    return render_template("A09_2021/secLogin.html", error = error)

# Route for page containing the flag
@app.route("/secDashboard")
def secDashboard():
    flag = get_flag("A09_2021")
    return render_template("A09_2021/secDashboard.html", flag = flag)

# Marks challenge A09:2021 as complete
@app.route('/A09_2021_Flag')
def A09_2021_Flag():
    if 'username' not in session:
        return redirect(url_for('home'))
    # Challenge marked as complete
    mark_challenge_complete(session['username'], 9)
    return render_template('A09_2021/A09_2021_Flag.html')

# Route for OWASP challenge A10:2021
@app.route('/A10_2021')
def A10_2021():
    if 'username' not in session:
        return redirect(url_for('home'))

    
    return render_template('A10_2021/A10_2021.html')

# Route for internal resource vulnerability
@app.route("/internal-resource-access", methods=["GET", "POST"])
def fetch():
    content = None
    if request.method == "POST":
        url = request.form.get("url", "")
        try:
            resp = requests.get(url)
            content = resp.text[:200]
        except Exception as e:
            content = f"Error fetching URL: {e}"
    return render_template("A10_2021/imageFetch.html", content = content)

# Route for secret page containing the flag
@app.route("/secret")
def secret():
    flag = get_flag("A10_2021")
    return "<h2>You found the hidden menu!</h2><p>{flag}</p>"

# Marks challenge A10:2021 as complete
@app.route('/A10_2021_Flag')
def A10_2021_Flag():
    if 'username' not in session:
        return redirect(url_for('home'))
    # Challenge marked as complete
    mark_challenge_complete(session['username'], 10)
    return render_template('A10_2021/A10_2021_Flag.html')
#
#
#   TEACHER PAGES
#
#

#Teacher home page
@app.route('/teacherHome')
def teacher_home():
    return render_template('teacherPages/teacherHome.html')
    
# Route for creating a new user
@app.route('/createuser', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        # Creates the user in the database
        if create_user_in_db(new_username, new_password):
            # Successful user creation
            return f"User {new_username} created successfully!"
        else:
            # Unsuccessful or duplicate user error message
            return "Username already exists. Please choose another."
    return render_template('teacherPages/createUser.html')

# Remove users page
@app.route("/manageuser")
def manage_user():
    
    return render_template("teacherPages/manageUser.html")


# Route to view all users and progress - ADMIN ONLY
@app.route('/viewdb')
def view_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # All user data and challege completion flags
    c.execute("""
            SELECT id, username, password, tag, Current_Challenge,
            A01_2021_done, A02_2021_done, A03_2021_done, A04_2021_done,
            A05_2021_done, A06_2021_done, A07_2021_done, A08_2021_done,
            A09_2021_done, A10_2021_done
            FROM users """)
    rows = c.fetchall()
    conn.close()

    # Column names for the table header
    columns = [
    "ID",
    "Username",
    "Password Hash",
    "Tag",
    "Current_Challenge",
    "A01_2021",
    "A02_2021",
    "A03_2021",
    "A04_2021",
    "A05_2021",
    "A06_2021",
    "A07_2021",
    "A08_2021",
    "A09_2021",
    "A10_2021"
    ]

    return render_template('teacherPages/viewUsers.html', columns=columns, rows=rows)

# Map of OWASP challenge numbers
# Used by the vulnerability randomizer to assign challenges to users
pageRoutes = {
    1: 'A01_2021',
    2: 'A02_2021',
    3: 'A03_2021',
    4: 'A04_2021',
    5: 'A05_2021',
    6: 'A06_2021',
    7: 'A07_2021',
    8: 'A08_2021',
    9: 'A09_2021',
    10: 'A10_2021',
}

# vulnerability randomizer
@app.route('/randomizer')
def randomizer():
    if 'username' not in session:
        return redirect(url_for('home'))
    username = session['username']
    # Chooses random, uncompleted challenge for the user
    rand_choice = chooseRandom(username, DB_PATH, total = 10)
    # If all challenges are complete, return to main page
    if rand_choice is None:
        return render_template('mainPage.html', user = username)
    # Map the challenge number to route name
    route = pageRoutes.get(rand_choice)
    # Error handling for unmapped challenge numbers
    if not route:
        return render_template('mainPage.html', message="Unknown challenge")
    return redirect(url_for(route))

# dynamic solutions
@app.route('/dynamicSolution', methods=['POST'])
def dynamicSolution():
    data = request.get_json()
    challenge_id = data.get('challenge_id')
    input = data.get('input')
    # Connect to solutions database and retrieve correct answer and explanation
    conn = sqlite3.connect(SOLUTIONS_DB_PATH)
    curs = conn.cursor()
    curs.execute("SELECT flag, explanation FROM solutions WHERE challenge_id = ?", (challenge_id,))
    row = curs.fetchone()
    conn.close()
    # Error handling if challenge number is not in database
    if not row:
        return jsonify({'error': 'Challenge not found'}), 404
    correctAns, explain = row
    # Compare user input with correct answer
    correct = input.strip() == correctAns.strip()
    return jsonify({
        'correct': correct,
        'feedback': 'Correct!' if correct else 'Try again.',
        'explanation': explain if not correct else None
    })



# -----LAST 2 LINES OF CODE FOR THE APP----- #
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
