import streamlit as st
import pickle
import pandas as pd
import requests

# ------------------- Utility Functions -------------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=88c3e26c57529d0e137d6cc9394c9e58&append_to_response=videos"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster = "https://image.tmdb.org/t/p/w500" + data['poster_path'] if data.get('poster_path') else "https://via.placeholder.com/500"
        rating = data.get("vote_average", "N/A")
        genres = ", ".join([g["name"] for g in data.get("genres", [])])
        # fetch trailer if available
        trailer = None
        if "videos" in data and "results" in data["videos"]:
            for vid in data["videos"]["results"]:
                if vid["type"] == "Trailer" and vid["site"] == "YouTube":
                    trailer = f"https://www.youtube.com/watch?v={vid['key']}"
                    break
        return poster, rating, genres, trailer
    except:
        return "https://via.placeholder.com/500", "N/A", "N/A", None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_ratings = []
    recommended_movies_genres = []
    recommended_movies_trailers = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].id
        poster, rating, genres, trailer = fetch_poster(movie_id)
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(poster)
        recommended_movies_ratings.append(rating)
        recommended_movies_genres.append(genres)
        recommended_movies_trailers.append(trailer)

    return recommended_movies, recommended_movies_posters, recommended_movies_ratings, recommended_movies_genres, recommended_movies_trailers

# ------------------- Load Data -------------------
movies_dict = pickle.load(open('movie.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ------------------- Page Config -------------------
st.set_page_config(
    page_title="🎬 Movie Recommender",
    page_icon="🎥",
    layout="wide"
)

# ------------------- Custom Styling -------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #1f1c2c, #928dab, #0f2027, #2c5364);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: white;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    h1 {
        text-align: center;
        color: #00f5d4;
        font-size: 3em;
        text-shadow: 0px 0px 20px #00f5d4;
        margin-bottom: 30px;
    }
    .movie-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        text-align: center;
        transition: transform 0.3s ease;
    }
    .movie-card:hover {
        transform: scale(1.05);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.7);
    }
    .movie-title {
        font-size: 16px;
        font-weight: bold;
        color: #ffb703;
        margin-top: 10px;
    }
    label {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        text-shadow: 0px 0px 10px #00f5d4;
        background-color: rgba(0, 0, 0, 0.3);
        padding: 8px 12px;
        border-radius: 8px;
        display: inline-block;
    }
    button[kind="primary"] {
        background-color: #00f5d4 !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        box-shadow: 0px 0px 10px #00f5d4;
        transition: transform 0.2s ease;
        width: 200px;
        height: 45px;
        font-size: 18px;
        margin-top: 20px;
        margin-bottom: 30px;
    }
    button[kind="primary"]:hover {
        transform: scale(1.05);
        box-shadow: 0px 0px 15px #00f5d4;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------- Main Title -------------------
st.markdown("<h1>🚀 PBL Project : Movie Recommendation System</h1>", unsafe_allow_html=True)

# ------------------- Movie Selection -------------------
selected_movie_name = st.selectbox('🎥 Choose a movie you like:', movies['title'].values)

# ------------------- Recommendation Button -------------------
if st.button('Recommend'):
    names, posters, ratings, genres, trailers = recommend(selected_movie_name)

    st.subheader(f"✨ Top 5 Recommendations for **{selected_movie_name}**")
    cols = st.columns(5)

    for idx, col in enumerate(cols):
        with col:
            st.markdown(f"""
                <div class="movie-card">
                    <div class="movie-title">{names[idx]}</div>
                    <p>⭐ Rating: {ratings[idx]}</p>
                    <p>🎭 Genres: {genres[idx]}</p>
                </div>
            """, unsafe_allow_html=True)
            st.image(posters[idx], use_container_width=True)
            if trailers[idx]:
                st.video(trailers[idx])