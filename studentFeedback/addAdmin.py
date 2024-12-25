import sqlite3
from werkzeug.security import generate_password_hash

# Connect to the SQLite database
conn = sqlite3.connect('feedback.db')
cursor = conn.cursor()

# Admin details
username = 'principal1'
password = '321'
email = 'principal1@gmail.com'
password = '123'  # Change this to the password you want
role = 'admin'  # Admin role

# Generate hashed password
hashed_password = generate_password_hash(password)

# Insert the admin user into the database
cursor.execute('''INSERT INTO users (username, email, password, role)VALUES (?, ?, ?, ?)''', (username, email, hashed_password, role))

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Admin user {username} has been added.")
