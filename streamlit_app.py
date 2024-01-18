# imports and set-up
import streamlit as st
import folium

from data_actions import main_runner, prep_plot_objs, unnormalize, get_size

# page config
st.set_page_config(
    page_title="Airport Network Analysis and Visualization",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Title
st.title("US Air Travel Network Visualization Tool")
st.subheader(
    "Interact with the visualization below to learn more about how the US air travel network has changed over time, and what happens when an airport is closed."
)
st.caption("Please be patient, it's doing a lot of math behind the scenes.")

# year
year = 2015

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

    pass_data = main_runner(year)
    passenger_df_trim, nodes_list = prep_plot_objs(pass_data)

col4, col5, col6 = st.columns([1, 8, 1])

with col5:
    # Create a map
    m = folium.Map(
        location=[39.8283, -98.5795],
        tiles="CartoDB positron",
        zoom_start=4,
        min_lat=20,
        max_lat=50,
        min_lon=-130,
        max_lon=-60,
        max_bounds=True,
        max_zoom=6,
        min_zoom=4,
    )

    # add the edges to the map from passenger df
    for edge in passenger_df_trim.iterrows():
        # create a line for the edge
        folium.PolyLine(
            locations=[
                [edge[1]["source_lat"], edge[1]["source_long"]],
                [edge[1]["target_lat"], edge[1]["target_long"]],
            ],
            color="darkgray",
            weight=0.3,
            opacity=0.3,
        ).add_to(m)

    # add the nodes to the map using the order from the nodes list
    for node in nodes_list:
        # if node is in the edge source list plot it
        if node in list(passenger_df_trim["source"].unique()):
            # get the node attributes
            node_attr = pass_data.nodes[node]

            # get the node coordinates
            lat = node_attr["latitude"]
            lon = node_attr["longitude"]

            # get the node color
            color = unnormalize(node_attr["betweenness_centrality"])

            # get size
            size = get_size(node_attr["betweenness_centrality"])

            # create a circle marker for the node
            folium.CircleMarker(
                location=[lat, lon],
                radius=size,
                color="black",
                fill=True,
                fill_color=color,
                fill_opacity=1,
                tooltip=f'AIRPORT: {node_attr["city"]}<br>CENTRALITY: {node_attr["betweenness_centrality"]:.2f}',
            ).add_to(m)

    # show the map
    st.write(m)

st.markdown(
    """
    ## Instructions
    * The map visualizes U.S. airport networks through a graph, with a selectable year via a slider.
    * It displays flights as edges (lines) connecting airport nodes.
    * Airport nodes' size and color indicate their betweenness centrality, reflecting importance in the network.
    * Betweenness centrality represents the count of shortest routes passing through an airport.
    * Adjusting the slider updates the graph to the chosen year.
    """
)
