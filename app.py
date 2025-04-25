import streamlit as st
from auth import login, signup
from test_functions import main_home_page
import importlib.util
import sys

st.set_page_config(page_title="Movie Recommender", layout="wide")

st.markdown("""
    <style>
        body {
            background-image: url('https://wallpapercave.com/wp/wp5437811.jpg');
            background-size: cover;
            background-position: center;
        }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("Welcome 🎬")

# ✅ Ensure session state is initialized
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# ✅ If user is logged in, show correct dashboard
if st.session_state["authenticated"]:
    if st.session_state["is_admin"]:
        # Admin Panel: Use importlib to dynamically load the admin panel
        if st.sidebar.button("Go to Admin Panel"):
            # Adjust path to where 1_admin.py is located
            file_path = "pages/1_admin.py"  # Change this if the path is different
            spec = importlib.util.spec_from_file_location("admin_panel", file_path)
            admin_panel = importlib.util.module_from_spec(spec)
            sys.modules["admin_panel"] = admin_panel
            spec.loader.exec_module(admin_panel)  # Executes the 1_admin.py file
    else:
        main_home_page()  # Load the User Panel
else:
    # ✅ Show login options
    page = st.sidebar.radio("Go to", ["User Login", "Admin Login", "Signup"])

    if page == "User Login":
        login(is_admin=False)
    elif page == "Admin Login":
        login(is_admin=True)
    else:
        signup()
