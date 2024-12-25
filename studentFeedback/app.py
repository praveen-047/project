from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from textblob import TextBlob
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management


# Initialize database
def init_db():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    # Create feedback table for individual question ratings
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher TEXT,
        question_id TEXT,
        rating INTEGER,
        sentiment REAL
    )''')

    # Create users table for authentication (with admin role)
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user'  -- Added role column ('user' or 'admin')
    )''')

    conn.commit()
    conn.close()


# Route for the home page - login options
@app.route('/')
def index():
    return render_template('login_select.html')  # Render a page with both Admin and Student login options


# Admin and Student Login Selection
@app.route('/login_select', methods=['GET'])
def login_select():
    return render_template('login_select.html')  # Show login options for both admin and student


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # Check if the email is for admin registration (for example, based on email)
        is_admin = 'admin' if 'admin' in email else 'user'  # Basic check for admin, customize as needed

        try:
            conn = sqlite3.connect('feedback.db')
            cursor = conn.cursor()

            # Insert user into the users table with role either 'user' or 'admin'
            cursor.execute('INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
                           (username, email, password, is_admin))
            conn.commit()
            conn.close()
            return redirect(url_for('login_select'))  # Redirect to login after successful registration
        except sqlite3.IntegrityError:
            return "Username or email already exists. Please try again."

    return render_template('register.html')  # Render the registration form

# Login page
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('feedback.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]  # Store the user's role (admin or user)

            # Redirect based on the user's role
            if session['role'] == 'admin':
                return redirect(url_for('admin'))  # Admin page
            else:
                return redirect(url_for('feedback_form'))  # Feedback form for students (feedback_form.html)
        else:
            return "Invalid email or password. Please try again."

    return render_template('feedback_form.html')  # Render login page initially

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_select'))


# Submit feedback route (students)
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access'}), 403

    # Get feedback data from the request
    data = request.json
    teacher = data['teacher']
    ratings = data['ratings']  # Dictionary of question_id and rating
    feedback_text = data.get('feedback', '')  # Optional feedback text
    sentiment = TextBlob(feedback_text).sentiment.polarity if feedback_text else 0.0

    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    # Save each rating in the database
    for question_id, rating in ratings.items():
        cursor.execute(''' 
            INSERT INTO feedback (teacher, question_id, rating, sentiment) 
            VALUES (?, ?, ?, ?)
        ''', (teacher, question_id, int(rating), sentiment))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Feedback submitted successfully!'})


# Get rankings route (teacher average ratings)
@app.route('/get_rankings', methods=['GET'])
def get_rankings():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    # Calculate average rating per teacher
    cursor.execute(''' 
        SELECT teacher, ROUND(AVG(rating), 2) as avg_rating 
        FROM feedback 
        GROUP BY teacher 
        ORDER BY avg_rating DESC
    ''')
    rankings = cursor.fetchall()
    conn.close()

    return jsonify(rankings)


# Admin page - view rankings and feedback
# Admin page - view rankings and feedback
@app.route('/admin')
def admin():
    # Ensure the user is an admin
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login_select'))

    # Fetch all rankings
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()

    cursor.execute(''' 
        SELECT teacher, ROUND(AVG(rating), 2) as avg_rating 
        FROM feedback 
        GROUP BY teacher 
        ORDER BY avg_rating DESC
    ''')
    rankings = cursor.fetchall()

    # Fetch all feedback for review
    cursor.execute('SELECT * FROM feedback')
    feedback = cursor.fetchall()

    conn.close()

    return render_template('admin.html', rankings=rankings, feedback=feedback)


# Feedback form page for students
@app.route('/feedback_form', methods=['GET'])
def feedback_form():
    # Ensure the user is a student
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login_select'))

    return render_template('feedback_form.html')  # Show the feedback form for the student


if __name__ == '__main__':
    init_db()  # Initialize the database if not already created
    app.run(debug=True)
