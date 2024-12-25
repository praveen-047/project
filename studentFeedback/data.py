import sqlite3

# Connect to the SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect('feedback.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Execute a SELECT query to retrieve all feedback data
cursor.execute('select * from users')
# Fetch all rows from the result of the query
rows = cursor.fetchall()

# Print the rows
for row in rows:
    print(row)

# Close the connection
conn.close()
