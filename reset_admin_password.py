import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# 🔥 Change 'admin' to your actual admin username
new_password = hash_password("admin123")  # Change this to your new password
cursor.execute("UPDATE users SET password = ? WHERE username = 'admin'", (new_password,))

conn.commit()
conn.close()

print("✅ Admin password updated! Try logging in again.")
