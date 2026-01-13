import pickle
import streamlit as st
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ================= 1. PAGE CONFIGURATION =================
st.set_page_config(
    page_title="VibeStream",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= 2. PROFESSIONAL CSS & ANIMATION =================
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
            gap: 10px;
        }
    }

    .movie-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .movie-card:hover {
        transform: scale(1.03);
        border-color: #8a2be2;
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.4);
    }

    .movie-card img {
        width: 100%;
        pointer-events: none;
    }

    .movie-title-card {
        padding: 8px 4px;
        font-size: 0.8rem;
        text-align: center;
        background: rgba(0,0,0,0.3);
    }

    /* Fixed Brand Title to remove auto-link */
    .brand-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(to right, #fff, #a2a2a2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 10px;
    }

    .subtitle {
        text-align: center;
        color: #b0b0b0;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)


# ================= 3. DATA LOADING =================
@st.cache_resource
def load_data():
    try:
        movies_df = pickle.load(open("movie_list.pkl", "rb"))

        if "tags" not in movies_df.columns:
            movies_df["tags"] = (
                movies_df["overview"].fillna("") + " " +
                movies_df["genres"].fillna("") + " " +
                movies_df["keywords"].fillna("")
            )

        cv = CountVectorizer(max_features=5000, stop_words="english")
        vectors = cv.fit_transform(movies_df["tags"]).toarray()
        similarity_matrix = cosine_similarity(vectors)

        return movies_df, similarity_matrix

    except Exception as e:
        st.error(f"Data loading error: {e}")
        return None, None


movies, similarity = load_data()


# ================= 4. API FUNCTIONS =================
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        # Using st.secrets or hardcoded key for stability
        api_key = "8265bd1679663a7ea12ac168da84d2e8"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        data = requests.get(url, timeout=3).json()
        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]
    except Exception:
        pass
    return "https://via.placeholder.com/500x750.png?text=No+Cover"


def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recs = []
    for i in distances[1:11]:
        movie_id = movies.iloc[i[0]].movie_id
        recs.append({
            "title": movies.iloc[i[0]].title,
            "poster": fetch_poster(movie_id)
        })
    return recs


# ================= 5. MAIN APP UI =================
# Brand title as Div to avoid auto-anchor links
st.markdown('<div class="brand-title">VIBESTREAM ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Stop doomscrolling. Start watching.</div>', unsafe_allow_html=True)

if movies is not None and similarity is not None:

    _, col_mid, _ = st.columns([0.5, 5, 0.5])

    with col_mid:
        selected_movie = st.selectbox(
            "Search",
            movies["title"].values,
            index=None,
            placeholder="Type a movie name...",
            label_visibility="collapsed",
        )

        btn = st.button(
            "Generate Recommendations",
            type="primary",
            use_container_width=True,
        )

    if btn and selected_movie:
        with st.spinner("Analyzing..."):
            results = recommend(selected_movie)
            st.write("---")

            # Building flat HTML string to fix the raw code block error
            html = '<div class="movie-grid">'
            for movie in results:
                html += f'<div class="movie-card">'
                html += f'<img src="{movie["poster"]}" alt="{movie["title"]}">'
                html += f'<div class="movie-title-card">{movie["title"]}</div>'
                html += f'</div>'
            html += "</div>"

            st.markdown(html, unsafe_allow_html=True)

    elif btn:
        st.warning("⚠️ Please select a movie first!")

else:
    st.error("⚠️ System Error: Data files not found.")