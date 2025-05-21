import sqlite3

# Function to connect to SQLite database
# Use this in your Flask routes

def get_db_connection():
    conn = sqlite3.connect('skhokho.db')
    conn.row_factory = sqlite3.Row
    return conn

# One-time script to initialize the DB with schema.sql
if __name__ == '__main__':
    connection = sqlite3.connect('skhokho.db')

    with open('schema.sql') as f:
        connection.executescript(f.read())

    connection.commit()
    connection.close()
    print("Database initialized with schema.sql")
