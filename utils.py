import requests
import pickle
import sqlite3
from bs4 import BeautifulSoup
from transformers import pipeline
import datetime
import hashlib  # ✅ Secure password hashing
import streamlit as st
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk


# ✅ TMDb API Key (Replace with your actual key)
TMDB_API_KEY = "405e24ac081a3821ebf21569e0739f5a"

# ✅ Load AI Summarization Model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# ✅ Load Movie Data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ✅ Database Connection
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Initialize the reviews table (if not exists)
def initialize_reviews_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER,
            review_text TEXT,
            user_id INTEGER,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# ✅ Secure password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ Function to update user account details
def update_account(old_username, new_username=None, new_password=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if new_username:
        cursor.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, old_username))

    if new_password:
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hash_password(new_password), old_username))

    conn.commit()
    conn.close()

# ✅ Function to fetch movie ratings from TMDb (Stars Format)
# ✅ Function to fetch movie ratings from TMDb (Convert 10-star to 5-star system)
def fetch_movie_rating(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        rating_out_of_10 = data.get("vote_average", 0)  # Default 0 if not available

        rating_out_of_5 = round(rating_out_of_10 / 2, 1)  # Convert to 5-star system
        full_stars = int(rating_out_of_5)  # Get full stars
        half_star = "½" if rating_out_of_5 - full_stars >= 0.5 else ""  # Check for half star

        return "⭐" * full_stars + half_star if rating_out_of_5 > 0 else "No Ratings"
    except requests.exceptions.RequestException:
        return "No Ratings"


# ✅ Function to Post Reviews Without Refresh
import sqlite3

def post_review(username, movie_title, review_text):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO reviews (username, movie_title, review) VALUES (?, ?, ?)",
                       (username, movie_title, review_text))
        conn.commit()
        conn.close()

        return True  # ✅ No refresh, just return success
    except Exception as e:
        print("Error posting review:", str(e))
        return False  # ✅ Handle failure gracefully



# ✅ Function to Display Last Review Message (Without Refresh)
def display_reviews(selected_movie):  # ✅ Accepts selected movie
    st.subheader(f"💬 User Reviews for {selected_movie}")

    # ✅ Fetch reviews from DB only if needed
    if "user_reviews" not in st.session_state or st.session_state["last_movie_reviewed"] != selected_movie:
        st.session_state["user_reviews"] = fetch_movie_reviews(selected_movie)
        st.session_state["last_movie_reviewed"] = selected_movie  # Track last reviewed movie

    # ✅ Display reviews
    if st.session_state["user_reviews"]:
        for user, review in st.session_state["user_reviews"]:
            st.write(f"**{user}**: {review}")
    else:
        st.write("No reviews yet. Be the first to review!")


# ✅ Function to Fetch Reviews for a Specific Movie
def fetch_movie_reviews(movie_title):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Fetch the `movie_id` from the `movies.pkl` file (since there's no movies table)
    movie_id = movies[movies['title'] == movie_title].iloc[0].movie_id

    # ✅ Fetch reviews directly from the `reviews` table
    cursor.execute("""
        SELECT r.review_text, u.username 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.movie_id = ?
    """, (movie_id,))

    reviews = cursor.fetchall()
    conn.close()

    return reviews if reviews else [("No reviews yet.", "Be the first to review!")]


# ✅ Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    names = [movies.iloc[i[0]].title for i in distances[1:6]]
    posters = [fetch_poster(movies.iloc[i[0]].movie_id) for i in distances[1:6]]
    return names, posters

# ✅ Function to fetch movie poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750?text=No+Image"

# ✅ Function to fetch Rotten Tomatoes reviews (Original Code Restored)
def fetch_rotten_tomatoes_reviews(movie_name):
    try:
        movie_slug = movie_name.lower().replace(" ", "_")
        url = f"https://www.rottentomatoes.com/m/{movie_slug}/reviews"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return [f"Error: Rotten Tomatoes page not found for {movie_name}"]

        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = [review.get_text(strip=True) for review in soup.find_all('p', class_='review-text')[:5]]
        return reviews if reviews else ["No reviews available."]
    except Exception as e:
        return [f"Error fetching reviews: {str(e)}"]

# ✅ Function to fetch movie synopsis
def fetch_movie_synopsis(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        synopsis = data.get("overview")

        if not synopsis:
            synopsis = fetch_wikipedia_summary(movies[movies['movie_id'] == movie_id].iloc[0].title)

        return ai_summarize(synopsis)
    except requests.exceptions.RequestException:
        return ai_summarize(fetch_wikipedia_summary(movies[movies['movie_id'] == movie_id].iloc[0].title))

# ✅ Function to fetch Wikipedia summary
def fetch_wikipedia_summary(movie_name):
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={movie_name}&format=json"
        search_response = requests.get(search_url).json()
        if "query" in search_response and "search" in search_response["query"]:
            correct_title = search_response["query"]["search"][0]["title"]
        else:
            return "Wikipedia summary not available."

        page_url = f"https://en.wikipedia.org/wiki/{correct_title.replace(' ', '_')}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(page_url, headers=headers)

        if response.status_code != 200:
            return "Wikipedia summary not available."

        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')

        for paragraph in paragraphs:
            text = paragraph.get_text(strip=True)
            if len(text) > 100:
                return text

        return "Wikipedia summary not available."
    except Exception:
        return "Wikipedia summary not available."

# ✅ Function to summarize text using AI
def ai_summarize(text):
    if text in ["Synopsis not available.", "Wikipedia summary not available."]:
        return "Summary not available."

    if len(text.split()) > 50:
        summary = summarizer(text, max_length=60, min_length=20, do_sample=False)
        return summary[0]['summary_text']

    return text


# Download necessary NLTK resources (one-time)
nltk.download('vader_lexicon')

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()


# ✅ Function to analyze sentiment of reviews
def analyze_sentiment(reviews):
    if not reviews or "Error" in reviews[0]:  # Handle errors
        return 0  # Neutral sentiment

    sentiment_scores = [sia.polarity_scores(review)['compound'] for review in reviews]

    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    return avg_sentiment  # Returns a sentiment score between -1 (negative) and +1 (positive)


# ✅ Enhanced Recommendation with Sentiment Analysis
def recommend_with_sentiment(movie):
    reviews = fetch_rotten_tomatoes_reviews(movie)
    sentiment_score = analyze_sentiment(reviews)

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    if sentiment_score > 0.2:  # Mostly positive sentiment
        st.write("😊 Reviews are positive! Recommending similar movies...")
        recommended_movies = [movies.iloc[i[0]].title for i in distances[1:6]]
    else:  # Neutral/Negative sentiment
        st.write("🤔 Reviews are mixed. Suggesting alternative movies...")
        alternative_movies = movies.sample(5)['title'].tolist()  # Pick random movies as alternatives
        recommended_movies = alternative_movies

    posters = [fetch_poster(movies[movies['title'] == name].iloc[0].movie_id) for name in recommended_movies]

    return recommended_movies, posters