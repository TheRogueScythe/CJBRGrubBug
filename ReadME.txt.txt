Grubbug Documentation 

 

Project Overview 

Grubbug is an intentionally vulnerable web application designed for instruction, practice, and evaluation of cybersecurity students. It provides hands-on experience with real-world vulnerabilities while giving instructors a measurable way to track student performance. It features ten challenges based on the OWASP Top Ten list. The current set of challenges is based on the 2021 OWASP Top Ten list. 

 

Core Features 

Vulnerability Randomizer: Each student will be assigned a random challenge 

Progress Tracking: Completion flags are stored per user to prevent repeated challenges and allow instructors to view student progress. 

Dynamic Solutions: Submitted answers are validated against a separate solutions database for completion and feedback. 

Administrator Features: Admin users can be manually created to manage content and monitor student activity 

 

Technologies Used 

Python: Core scripting and backend 

Flask: Web framework for routing and API endpoints 

SQLite: Database framework for user progress and challenge solutions 

bcrypt: Password hashing for user authentication 

HTML/CSS: Frontend templates and UI 

 

Setup Instructions 

How to Install Dependencies 

Install the required Python packages: 

pip install flask flask_sqlalchemy python-dotenv bcrypt 

 

How To Initialize Databases 

Grubbug uses two databases: users.db and solutions.db. The databases are separated for security reasons. 

users.db stores usernames, passwords, and challenge completion progress. To initialize users.db run:  

python init_db.py 

solutions.db stores correct answers and explanations for each challenge. To initialize solutions.db run: 

python init_solutions.py 

 

How to Run App Locally 

flask run --host=0.0.0.0 --port=5000 

 

Database Schemas 

Tables in users.db and solutions.db 

users.db: Stores usernames, hashed passwords, and challenge completion flags.  

solutions.db: Stores correct answers and explanations for each challenge. Maps each challenge ID to its correct solution and explanation. 

Column Definitions 

users.db 

Column 

Type 

Description 

Id 

INTEGER 

Primary key 

Username 

TEXT UNIQUE 

Unique identifier for each user 

password 

TEXT 

Hashed password 

Tag 

TEXT 

Based on assigned role: student or admin 

Current_Challenge 

INTEGER 

1-10 based on current challenge 

A01_2021_done 

INTEGER 

1 if complete, 0 or NULL if incomplete 

A02_2021_done 

INTEGER 

Same as above, follows pattern through A10_2021_done 

 

solutions.db 

Column 

Type 

Description 

challenge_id 

TEXT 

Primary key, A01_2021 through A10_2021 

correct_answer 

TEXT 

Challenge flag or answer string 

explanation 

TEXT 

Explanation shown if answer is incorrect 

 

How Challenge Progress is Tracked 

When a user correctly solves a challenge, the app updates the corresponding AXX_2021_done to 1. 

 

The chooseRandom function in vulnRandomizer.py uses these flags to avoid showing a challenge that has already been seen 

 

Core Logic 

How Challenge Assignment Works 

Challenges are randomly assigned by the chooseRandom function in vulnRandomizer.py. This function is designed to assign challenges that the user has not seen or completed yet.  

The vulnerability randomizer checks all challenge flags for a user, identifies completed challenges, randomly selects one of the remaining challenges, and returns the selected challenge to the user on the frontend. 

 

How Challenges are Validated 

Answer validation is handled by the dynamicSolution route in app.py. This checks a user’s answer against the stored answer in solutions.db. 

("SELECT correct_answer, explanation FROM solutions WHERE challenge_id = ?", (challenge_id,)) 

This will compare the user input to the correct answer and will return with “Correct” if correct or “Try again” with feedback. 

 

How Admin Users are Added 

Admin users are created by using AddAdminToDB.py. This will insert the admin user with into users.db. Passwords are hashed securely by using bcrypt. 

 

File Structure 

Scripts and Purpose 

File Name 

Description 

app.py 

Main Flask application. Handles app routes, user interactions, core functions. 

init_db.py 

Creates the users database and challenge columns. 

init_solutions.py 

Creates and populates solutions table. 

AddAdminToDB.py 

Allows an admin user to be created and added to the user database. 

vulnRandomizer.py 

Contains functions for the vulnerability randomizer and progress tracking. 

 

Templates, Static Files, and Data 

Challenge template pages, teacher pages, login pages, and the home page can all be found in the templates folder. Static files such as images, JavaScript files, and CSS files can all be found in the static folder. The users database can be found the data folder. 

 

Common Tasks 

How to Add a New Challenge 

Follow these steps to add a new challenge to Gubbug: 

Create the challenge page in the templates folder (Example: AXX_2021.html) 

Add route logic to app.py 

@app.route('/AXX_2021') 

def AXX_2021(): 

    if 'username' not in session: 

        return redirect(url_for('home')) 

 

     

    return render_template('AXX_2021/AXX_2021.html') 

@app.route('/AXX_2021_Flag') 

def AXX_2021_Flag(): 

    if 'username' not in session: 

        return redirect(url_for('home')) 

    mark_challenge_complete(session['username'], 2) 

    return render_template('AXX_2021/AXX_2021_Flag.html') 

 

Update solutions.db with the correct answer and explanation 

Update users.db to include a new progress flag (SQL: ALTER TABLE users ADD COLUMN A11_2021_done INTEGER DEFAULT 0;) 

 

How to Reset User Progress 

To reset user progress, use the reset function found in vulnRandomizer.py 

 

How to Update a Solution or Explanation 

To update an existing challenge’s solution and/or explanation, manually update solutions.db. 

 

Security Notes 

Password Hashing 

Grubbug uses bcrypt to securely hash stored passwords in users.db. This hash is stored in the password column of users.db. This ensures that all passwords will have unique hashes. 

hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) 

 

Separation of User and Solution Data 

Grubbug uses two separate databases, users.db and solutions.db. These databases contain information that is only visible to admin users. These databases are separate because they contain different information. It also reduces the risk of accidental exposure  

 

Ownership and Contact Info 

Who Are the Developers? 

Grubbug was built by Brady Peer and Connor Lindsey for the CNMT 480 capstone project. 

Contact Info for Questions 

Brady Peer – bpeer108@uwsp.edu 

Connor Lindsey – clind773@uwsp.edu 