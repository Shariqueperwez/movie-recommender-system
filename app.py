import streamlit as st
import bz2
import pickle
import pandas as pd
import requests
import plotly.express as px

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Cinematix AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CUSTOM CSS FOR PREMIUM LOOK
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div.stButton > button:first-child {
        background-color: #e50914;
        color: white;
        width: 100%;
        border-radius: 5px;
    }
    .movie-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. HELPER FUNCTIONS
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        # verify=False helps with SSL errors in local/university networks
        response = requests.get(url, verify=False)
        data = response.json()
        poster_path = data.get('poster_path')
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else "https://via.placeholder.com/500x750?text=No+Poster"
        return full_path, data.get('vote_average', 'N/A'), data.get('release_date', '0000')[:4]
    except:
        return "https://via.placeholder.com/500x750?text=Error", "N/A", "N/A"

# 4. LOAD DATA
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
#similarity = pickle.load(bz2.BZ2File('similarity.pkl.pbz2', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# 5. SIDEBAR
with st.sidebar:
    st.title("🎬 Cinematix AI")
    st.markdown("---")
    selected_movie_name = st.selectbox(
        'Type or select a movie:',
        movies['title'].values
    )
    search_button = st.button('Generate Recommendations')
    st.markdown("---")
    st.info("💡 **How it works:** This engine uses **Content-Based Filtering** and **Vector Space Modeling** to identify movies with high semantic similarity.")
    #st.info("This system uses AI to find movies with similar themes, cast, and genres.")

# 6. MAIN DISPLAY
st.title(f"Recommendations for: {selected_movie_name}")

if search_button:
    movie_index = movies[movies['title'] == selected_movie_name].index[0]
    distances = similarity[movie_index]
    # Get top 5 movies (excluding itself)
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    # Layout for movies
    cols = st.columns(5)
    rec_names = []
    rec_scores = []

    for i, (index, dist) in enumerate(movies_list):
        movie_id = movies.iloc[index].movie_id
        title = movies.iloc[index].title
        poster, rating, year = fetch_movie_details(movie_id)
        
        rec_names.append(title)
        rec_scores.append(round(dist, 2))

        with cols[i]:
            st.image(poster)
            st.markdown(f"**{title}**")
            st.caption(f"⭐ {rating} | 📅 {year}")

    # 7. ANALYTICS SECTION (The Unique Flex)
    st.write("---")
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.subheader("📊 Recommendation Confidence")
        fig = px.bar(
            x=rec_scores, 
            y=rec_names, 
            orientation='h',
            labels={'x': 'Similarity Score', 'y': ''},
            color=rec_scores,
            color_continuous_scale='Reds'
        )
        fig.update_layout(showlegend=False, height=300, margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("🧪 Technical Breakdown")
        with st.expander("How this works"):
            st.write("Using **Cosine Similarity**:")
            st.latex(r"\text{Sim} = \frac{A \cdot B}{\|A\| \|B\|}")
            st.write("We compare metadata vectors to find the closest match.")