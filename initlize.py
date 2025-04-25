import sqlite3

def initialize_db():
    conn = sqlite3.connect('users.db')  # Ensure correct path
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )
    ''')

    # Create reviews table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        movie_id INTEGER,
        review_text TEXT,
        created_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    # Ensure the users and reviews tables are created
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="users"')
    if cursor.fetchone():
        print("Users table is already created.")
    else:
        print("Creating users table...")

    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="reviews"')
    if cursor.fetchone():
        print("Reviews table is already created.")
    else:
        print("Creating reviews table...")

    conn.commit()
    conn.close()

initialize_db()
