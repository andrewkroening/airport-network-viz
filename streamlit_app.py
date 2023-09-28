# imports and set-up
import streamlit as st

# import pandas as pd
import folium

# page config
st.set_page_config(
    page_title="Airport Network Analysis and Visualization",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Title
st.title("US Air Travellers Rely Heavily on a Few Airports")
st.subheader(
    "The Majority of Major US Aviation Hubs are Located Near Each Other, Making Them Eaily Disrupted by Weather Events"
)

# add a two tab layout to the page
tab1, tab2 = st.tabs(["Airport Network", "Instructions"])

with tab1:
    # add a map section
    m = folium.Map(
        location=[39.8283, -98.5795],
        tiles="CartoDB dark_matter",
        zoom_start=4,
        min_lat=20,
        max_lat=50,
        min_lon=-130,
        max_lon=-60,
        max_bounds=True,
        max_zoom=6,
        min_zoom=4,
    )

    st.write(m)

with tab2:
    st.write("Instructions")

# add a 1-3-1 column layout
col1, col2, col3 = st.columns([1, 3, 1])

# add a slider scale from 1990 to 2015 to col 2
with col2:
    year = st.slider(
        "Select Year",
        1990,
        2015,
        2015,
        1,
    )
