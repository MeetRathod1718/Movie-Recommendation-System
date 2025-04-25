import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ✅ Database Connection
def get_db_connection():
    conn = sqlite3.connect("users.db")  # Ensure the database path is correct
    conn.row_factory = sqlite3.Row
    return conn


# ✅ Function to Fetch Session Data
def get_session_data():
    conn = sqlite3.connect("users.db")

    query = """
        SELECT u.username, s.login_time, s.logout_time
        FROM session_logs s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.login_time ASC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


# ✅ AI Feature: Generate Site Visits Graph
def generate_site_visits_graph():
    """ Generate a graph of site visits over time """
    df = get_session_data()

    if df.empty:
        st.warning("🚨 No data available for AI reports yet. Try after some users log in and out.")
        return

    # Convert timestamps to datetime format
    df["login_time"] = pd.to_datetime(df["login_time"])
    df["logout_time"] = pd.to_datetime(df["logout_time"])

    # Create a simple bar chart
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["login_time"], range(len(df)), marker="o", linestyle="-", label="Logins", color="blue")

    # ✅ Annotate each point with the corresponding username
    for i in range(len(df)):
        ax.text(df["login_time"][i], i, df["username"][i], fontsize=10, ha="right", color="blue")
    ax.set_xlabel("Time")
    ax.set_ylabel("Sessions")
    ax.set_title("📊 User Session Activity")
    ax.legend()

    st.pyplot(fig)


# ✅ Admin Panel: Display All Users
def display_all_users():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    st.subheader("All Users")
    if users:
        for user in users:
            st.write(f"**Username:** {user['username']} - **Admin:** {'Yes' if user['is_admin'] else 'No'}")

            if st.button(f"❌ Delete {user['username']}", key=f"delete_{user['username']}"):
                delete_user(user['username'])
                st.rerun()  # Refresh after deletion
    else:
        st.write("No users available.")


# ✅ Function to Delete User
def delete_user(username):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        st.success(f"User {username} has been deleted.")
    except sqlite3.OperationalError as e:
        st.error(f"Error deleting user: {e}")
    finally:
        conn.close()


# ✅ Display & Delete Movie Reviews
def display_movie_reviews():
    conn = get_db_connection()
    try:
        reviews = conn.execute("SELECT * FROM reviews").fetchall()
    except sqlite3.OperationalError as e:
        st.error(f"Error fetching reviews: {e}")
        conn.close()
        return
    conn.close()

    st.subheader("Movie Reviews")
    if reviews:
        for review in reviews:
            st.write(f"**Review ID:** {review['id']} - **Review:** {review['review_text']}")

            if st.button(f"🗑 Delete Review {review['id']}", key=f"delete_{review['id']}"):
                delete_review(review['id'])
                st.rerun()
    else:
        st.write("No reviews available.")


# ✅ Function to Delete Review
def delete_review(review_id):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
        conn.commit()
        st.success(f"Review {review_id} has been deleted.")
    except sqlite3.OperationalError as e:
        st.error(f"Error deleting review: {e}")
    finally:
        conn.close()


# ✅ System Statistics
def display_system_statistics():
    conn = get_db_connection()
    try:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_reviews = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    except sqlite3.OperationalError as e:
        st.error(f"Error fetching statistics: {e}")
        conn.close()
        return
    conn.close()

    st.subheader("📊 System Statistics")
    st.write(f"👤 **Total Users:** {total_users}")
    st.write(f"💬 **Total Reviews:** {total_reviews}")


# ✅ Update Admin Settings
def update_admin_settings(username):
    conn = get_db_connection()

    new_username = st.text_input("New Username", value=username)
    new_password = st.text_input("New Password", type="password")

    if st.button("💾 Save Changes"):
        if new_username != username:
            conn.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, username))
        if new_password:
            conn.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))

        conn.commit()
        conn.close()
        st.success("✅ Admin account updated successfully!")
        st.session_state["user"] = new_username  # Update session state
        st.rerun()  # Refresh app


# ✅ Reset User Password
def reset_user_password():
    conn = get_db_connection()
    username_to_reset = st.text_input("Enter username to reset password")
    new_password = st.text_input("Enter new password", type="password")

    if st.button("🔑 Reset Password"):
        try:
            conn.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username_to_reset))
            conn.commit()
            st.success(f"🔄 Password for {username_to_reset} has been reset successfully.")
        except sqlite3.OperationalError as e:
            st.error(f"Error resetting password: {e}")
        finally:
            conn.close()


# ✅ Main Admin Panel
def main_admin_panel():
    # ✅ Profile Dropdown in Admin Panel
    top_col1, top_col2 = st.columns([0.9, 0.1])

    with top_col1:
        st.title("🎬 Admin Panel")

    with top_col2:
        if "show_dropdown" not in st.session_state:
            st.session_state["show_dropdown"] = False

        if st.button("👤", key="profile_button"):
            st.session_state["show_dropdown"] = not st.session_state["show_dropdown"]

        if st.session_state["show_dropdown"]:
            with st.expander("⚙️ Profile Options", expanded=True):
                if st.button("Setting", key="settings_btn"):
                    st.session_state["show_settings"] = not st.session_state.get("show_settings", False)
                    st.rerun()
                if st.button("Logout", key="logout_btn"):
                    st.session_state["authenticated"] = False
                    st.session_state["is_admin"] = False
                    st.session_state["user"] = None
                    st.rerun()

    # Admin Settings Section
    if "show_settings" in st.session_state and st.session_state["show_settings"]:
        with st.expander("⚙️ Admin Account Settings", expanded=True):
            st.subheader("Update Admin Information")
            current_username = st.session_state["user"]
            st.write(f"**Current Username:** {current_username}")
            update_admin_settings(current_username)
            reset_user_password()
            display_system_statistics()

    # ✅ AI Site Visit Reports
    st.subheader("📈 View AI Reports")
    generate_site_visits_graph()

    # ✅ Admin Actions
    option = st.selectbox("📌 Choose an Action", ["View All Users", "View & Delete Movie Reviews"])

    if option == "View All Users":
        display_all_users()
    elif option == "View & Delete Movie Reviews":
        display_movie_reviews()


# ✅ Run Admin Panel
if __name__ == "__main__":
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

    if "authenticated" in st.session_state and st.session_state["authenticated"] and st.session_state["is_admin"]:
        main_admin_panel()
    else:
        st.error("❌ You are not authorized to view the Admin Panel.")
