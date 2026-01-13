import pickle
import streamlit as st
import requests

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
    /* --- REMOVE DEFAULT STREAMLIT PADDING --- */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }

    /* --- ANIMATED AURORA BACKGROUND --- */
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

    /* --- RESPONSIVE MOVIE GRID --- */
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

    /* --- MOVIE CARD --- */
    .movie-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
    }

    .movie-card:hover {
        transform: scale(1.03);
        border-color: #8a2be2;
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.4);
        z-index: 10;
    }

    .movie-card img {
        width: 100%;
        height: auto;
        display: block;
        pointer-events: none;
    }

    .movie-title-card {
        padding: 8px 4px;
        font-size: 0.8rem;
        font-weight: 600;
        text-align: center;
        color: #e0e0e0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        background: rgba(0, 0, 0, 0.3);
    }

    /* --- HEADER STYLING (Anchor link removed) --- */
    .brand-title {
        text-align: center;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
        font-size: 2.2rem !important;
        text-transform: uppercase;
        background: linear-gradient(to right, #ffffff, #a2a2a2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Source Sans Pro', sans-serif;
    }

    .subtitle {
        text-align: center;
        color: #b0b0b0;
        font-size: 0.9rem;
        font-weight: 300;
        margin-top: 0px;
        margin-bottom: 20px;
    }

    /* --- HIDE STREAMLIT DEFAULT UI --- */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    </style>
    """,
    unsafe_allow_html=True
)


# ================= 3. DATA LOADING =================
@st.cache_resource
def load_data():
    try:
        movies = pickle.load(open("movie_list.pkl", "rb"))
        return movies
    except FileNotFoundError:
        return None


movies = load_data()


# ================= 4. API FUNCTIONS =================
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8"
        response = requests.get(url, timeout=3)
        data = response.json()
        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]
    except Exception:
        pass
    return "https://via.placeholder.com/500x750.png?text=No+Cover"


def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommendations = []
    for i in distances[1:11]:
        movie_id = movies.iloc[i[0]].movie_id
        recommendations.append({
            "title": movies.iloc[i[0]].title,
            "poster": fetch_poster(movie_id),
        })
    return recommendations


# ================= 5. MAIN APP UI =================
# Brand title as Div to avoid anchor links
st.markdown('<div class="brand-title">VIBESTREAM ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Stop doomscrolling. Start watching.</div>', unsafe_allow_html=True)

if movies is not None:
    col_left, col_mid, col_right = st.columns([0.5, 5, 0.5])

    with col_mid:
        selected_movie = st.selectbox(
            "Search for a movie...",
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
            recommendations = recommend(selected_movie)
            st.write("---")

            # Building HTML string without indentation to prevent "Code Block" bug
            html = '<div class="movie-grid">'
            for movie in recommendations:
                html += f'<div class="movie-card">'
                html += f'<img src="{movie["poster"]}" alt="{movie["title"]}">'
                html += f'<div class="movie-title-card">{movie["title"]}</div>'
                html += f'</div>'
            html += "</div>"

            st.markdown(html, unsafe_allow_html=True)

    elif btn and not selected_movie:
        st.warning("⚠️ Please select a movie first!")

else:
    st.error("⚠️ System Error: Data files not found.")