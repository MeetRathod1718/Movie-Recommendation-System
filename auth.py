import sqlite3
import streamlit as st
import hashlib  # ✅ Secure password hashing
import datetime


# ✅ Function to log user login/logout sessions
def log_user_session(user_id, action):
    """ Logs user login/logout in the session_logs table """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if action == "login":
        cursor.execute("INSERT INTO session_logs (user_id, login_time) VALUES (?, ?)",
                       (user_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    elif action == "logout":
        cursor.execute(
            """UPDATE session_logs 
               SET logout_time = ?, 
                   duration = (julianday(logout_time) - julianday(login_time)) * 24 * 60 
               WHERE user_id = ? AND logout_time IS NULL""",
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))

    conn.commit()
    conn.close()


# ✅ Function to securely hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ✅ Database Connection
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn


# ✅ Admin & User Login Function
def login(is_admin=False):
    st.title("🔑 Admin Login" if is_admin else "🔑 User Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user:
            stored_password = user["password"]
            if stored_password == hash_password(password):  # ✅ Only check hashed passwords
                if is_admin and user["is_admin"] == 0:
                    st.error("❌ You are not an admin!")
                    return

                st.session_state["authenticated"] = True
                st.session_state["user"] = user["username"]
                st.session_state["is_admin"] = bool(user["is_admin"])

                # ✅ Log login session
                log_user_session(user["id"], "login")

                st.success(f"Welcome {'Admin' if is_admin else 'User'}! Redirecting...")
                st.rerun()
            else:
                st.error("❌ Invalid username or password!")
        else:
            st.error("❌ Invalid username or password!")


# ✅ User Signup Function (Prevents Duplicate Admins)
def signup():
    st.title("📝 Signup")

    username = st.text_input("Choose a Username", key="signup_username")
    password = st.text_input("Choose a Password", type="password", key="signup_password")

    if st.button("Signup", key="signup_button"):
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)",
                         (username, hash_password(password)))  # ✅ Store hashed password
            conn.commit()
            st.success("Signup successful! Please log in.")
        except sqlite3.IntegrityError:
            st.error("Username already exists! Try another.")
        finally:
            conn.close()


# ✅ Logout Function
def logout():
    if "user" in st.session_state:
        conn = get_db_connection()
        user_id = conn.execute("SELECT id FROM users WHERE username = ?", (st.session_state["user"],)).fetchone()
        conn.close()

        if user_id:
            # ✅ Log logout session
            log_user_session(user_id[0], "logout")

        st.session_state["authenticated"] = False
        st.session_state["is_admin"] = False
        st.session_state["user"] = None  # Clear user session
        st.rerun()  # Refresh UI after logout
