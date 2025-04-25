import streamlit as st
from auth import login, signup
from test_functions import main_home_page
from utils import initialize_reviews_table
import base64
import os

# ✅ Initialize database
initialize_reviews_table()

# ✅ Set the page config
st.set_page_config(page_title="Movie Recommender", layout="wide")

# ✅ Function to Set Background Image
def set_background(image_path):
    if os.path.exists(image_path):  # ✅ Check if file exists
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()

        css = f"""
            <style>
                .stApp {{
                    background: url("data:image/png;base64,{encoded_string}") no-repeat center center fixed;
                    background-size: cover;
                }}
            </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    else:
        st.error("❌ Background image not found! Check the file path.")

# ✅ Set Background Image
set_background("assets/back.jpg")

# ✅ Fix Dropdowns, Inputs & Rotten Tomatoes Expander
st.markdown("""
    <style>
        /* Force Blue Background for Reviews */
        div.stExpander {
            background-color: rgb(14, 17, 23) !important; /* Blue Background */
            border-radius: 10px !important; /* Rounded corners */
            padding: 10px !important;
        }

        div.stExpander p, div.stExpander span, div.stExpander h2 {
            color: white !important; /* Make text white for readability */
        }
    </style>
""", unsafe_allow_html=True)


# ✅ Maintain session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"

# ✅ Sidebar
st.sidebar.title("Welcome 🎬")

# ✅ Show Navigation Based on Login Status
if st.session_state["authenticated"]:
    if st.session_state["is_admin"]:
        st.sidebar.markdown("🔹 **Admin Panel**")
        st.switch_page("pages/1_admin.py")
    else:
        main_home_page()

else:
    if st.sidebar.button("User Login"):
        st.session_state["current_page"] = "user_login"
    if st.sidebar.button("Admin Login"):
        st.session_state["current_page"] = "admin_login"
    if st.sidebar.button("Signup"):
        st.session_state["current_page"] = "signup"

    if st.session_state["current_page"] == "user_login":
        login(is_admin=False)
    elif st.session_state["current_page"] == "admin_login":
        login(is_admin=True)
    elif st.session_state["current_page"] == "signup":
        signup()
    else:
        st.markdown('<div class="main-content">Please select your login method from the sidebar!</div>', unsafe_allow_html=True)
