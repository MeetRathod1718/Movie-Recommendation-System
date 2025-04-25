import pickle
import streamlit as st
import sqlite3
from utils import (
    recommend_with_sentiment, fetch_rotten_tomatoes_reviews,
    fetch_movie_synopsis, fetch_wikipedia_summary, ai_summarize,
    post_review, fetch_movie_rating, update_account
)

# ✅ Establish database connection
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

def main_home_page():
    # ✅ Create a top bar layout with profile dropdown on the right
    top_col1, top_col2 = st.columns([0.9, 0.4])

    with top_col1:
        st.header(f'🎬 Movie Recommender System - Welcome {st.session_state["user"]}!')

    with top_col2:
        if "show_dropdown" not in st.session_state:
            st.session_state["show_dropdown"] = False

        if st.button("👤", key="profile_button"):
            st.session_state["show_dropdown"] = not st.session_state["show_dropdown"]

        if st.session_state["show_dropdown"]:
            with st.expander("Profile Options", expanded=True):
                if st.button("⚙️ Settings", key="settings_button"):
                    st.session_state["show_settings"] = not st.session_state.get("show_settings", False)
                    st.rerun()
                if st.button("🚪 Logout"):
                    st.session_state["authenticated"] = False
                    st.rerun()

    # ✅ Settings Form
    if "show_settings" in st.session_state and st.session_state["show_settings"]:
        with st.expander("Account Settings", expanded=True):
            st.subheader("Update Your Account Information")
            current_username = st.session_state["user"]
            st.write(f"**Username:** {current_username}")
            new_username = st.text_input("New Username", value=current_username)
            new_password = st.text_input("New Password", type="password")
            if st.button("Save Changes"):
                if new_username != current_username or new_password:
                    update_account(current_username, new_username, new_password)
                    st.success("Account updated successfully!")
                    st.session_state["show_settings"] = False
                    st.rerun()
                else:
                    st.warning("Provide a new username or password to update.")

    # ✅ Load movie data
    movies = pickle.load(open('movies.pkl', 'rb'))
    movie_list = movies['title'].values
    selected_movie = st.selectbox("🔍 Type or select a movie", movie_list)

    if st.button('🎥 Show Recommendation', key="show_recommendation"):
        recommended_movie_names, recommended_movie_posters = recommend_with_sentiment(selected_movie)
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])

        # ✅ Fetch & Display Movie Rating
        st.subheader("⭐ Movie Rating")
        movie_id = movies[movies['title'] == selected_movie].iloc[0].movie_id
        rating = fetch_movie_rating(movie_id)
        st.write(f"**Rating:** {rating}")

        # ✅ Rotten Tomatoes Reviews
        st.subheader("📝 Rotten Tomatoes Reviews")
        reviews = fetch_rotten_tomatoes_reviews(selected_movie)
        with st.expander("Click to view reviews"):
            for review in reviews:
                st.write(f"🔹 {review}")

        # ✅ Movie Synopsis & AI Summary
        st.subheader("📖 Movie Synopsis & AI Summary")
        synopsis = fetch_movie_synopsis(movie_id) or fetch_wikipedia_summary(selected_movie)
        summary = ai_summarize(synopsis)
        st.write(f"**AI-Generated Summary:** {summary}")

        # ✅ Post a Review (Using st.form to prevent refresh)
        st.subheader("💬 Post Your Review")
        with st.form("review_form", clear_on_submit=True):
            review_text = st.text_area("Write your review here:", key="review_input")
            submit_button = st.form_submit_button("Submit Review")

        if submit_button:
            if review_text.strip():
                success = post_review(st.session_state["user"], selected_movie, review_text)
                if success:
                    st.success("✅ Review posted successfully!")
                    if "reviews" not in st.session_state:
                        st.session_state["reviews"] = []
                    st.session_state["reviews"].insert(0, review_text)
                    st.rerun()
                else:
                    st.error("❌ Failed to submit review. Try again.")
            else:
                st.warning("⚠️ Please write a review before submitting.")

        # ✅ Display Reviews
        st.subheader("💬 User Reviews for This Movie")
        def get_reviews(movie_id):
            if "reviews" in st.session_state and st.session_state["reviews"]:
                return st.session_state["reviews"]
            conn = sqlite3.connect("users.db", check_same_thread=False)
            cursor = conn.cursor()
            query = "SELECT review_text FROM reviews WHERE movie_id = ? ORDER BY created_at DESC"
            cursor.execute(query, (movie_id,))
            reviews = [review[0] for review in cursor.fetchall()]
            conn.close()
            st.session_state["reviews"] = reviews
            return reviews

        reviews = get_reviews(selected_movie)
        if reviews:
            for review in reviews:
                st.write(f"- {review}")
        else:
            st.write("No reviews yet. Be the first to review!")

if __name__ == "__main__":
    main_home_page()
