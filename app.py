import pickle
import requests
import streamlit as st
import streamlit.components.v1 as components

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ================= 1. PAGE CONFIG =================
st.set_page_config(
    page_title="VibeStream",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ================= 2. STYLES =================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }

    .stApp {
        background: linear-gradient(-45deg, #000000, #1a0b2e, #110f16, #2d1b4e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: white;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .movie-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 15px;
        padding: 10px 0;
    }

    @media (max-width: 768px) {
        .movie-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    .movie-card {
        background: rgba(255,255,255,0.08);
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }

    .movie-card:hover {
        transform: scale(1.03);
        box-shadow: 0 0 15px rgba(138,43,226,0.4);
    }

    .movie-card img {
        width: 100%;
        display: block;
        pointer-events: none;
    }

    .movie-title {
        text-align: center;
        padding: 8px;
        font-size: 0.8rem;
        background: rgba(0,0,0,0.4);
        color: #e0e0e0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .brand-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        text-transform: uppercase;
        background: linear-gradient(to right, #fff, #aaa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        text-align: center;
        color: #b0b0b0;
        margin-bottom: 20px;
    }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ================= 3. LOAD DATA =================
@st.cache_resource
def load_data():
    movies = pickle.load(open("movie_list.pkl", "rb"))

    if "tags" not in movies.columns:
        movies["tags"] = (
            movies["overview"].fillna("")
            + " "
            + movies["genres"].fillna("")
            + " "
            + movies["keywords"].fillna("")
        )

    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(movies["tags"]).toarray()
    similarity = cosine_similarity(vectors)

    return movies, similarity


movies, similarity = load_data()

# ================= 4. POSTER FETCH =================
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={st.secrets['TMDB_API_KEY']}"
        data = requests.get(url, timeout=5).json()
        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]
    except:
        pass
    return "https://via.placeholder.com/500x750.png?text=No+Image"


def recommend(movie):
    idx = movies[movies["title"] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1]
    )

    results = []
    for i in distances[1:11]:
        mid = movies.iloc[i[0]].movie_id
        results.append(
            {
                "title": movies.iloc[i[0]].title,
                "poster": fetch_poster(mid),
            }
        )
    return results


# ================= 5. UI =================
st.markdown('<div class="brand-title">VIBESTREAM ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Stop doomscrolling. Start watching.</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.5, 5, 0.5])
with col2:
    selected_movie = st.selectbox(
        "",
        movies["title"].values,
        index=None,
        placeholder="Search a movie...",
        label_visibility="collapsed",
    )
    btn = st.button("Generate Recommendations", use_container_width=True)

if btn and selected_movie:
    recs = recommend(selected_movie)

    html = '<div class="movie-grid">'
    for m in recs:
        html += (
            f'<div class="movie-card">'
            f'<img src="{m["poster"]}">'
            f'<div class="movie-title">{m["title"]}</div>'
            f'</div>'
        )
    html += "</div>"

    components.html(html, height=900, scrolling=False)

elif btn:
    st.warning("Please select a movie first ⚠️")
