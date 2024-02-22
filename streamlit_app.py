# imports and set-up
import streamlit as st
import folium
import pandas as pd

from data_actions import (
    main_runner,
    prep_plot_objs,
    unnormalize,
    get_size,
    get_top_10,
    remove_airport,
    remove_route,
)

# page config
st.set_page_config(
    page_title="Airport Network Analysis and Visualization",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Title
st.title("US Air Travel Network")
st.subheader(
    "Interact with the visualization below to learn about how the US air travel network has changed over time, and what happens when an airport is closed."
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

    pass_data_orig = main_runner(year)
    passenger_df_trim_orig, nodes_list_orig = prep_plot_objs(pass_data_orig)
    pass_data_top10_air_orig, pass_data_top10_pass_orig = get_top_10(pass_data_orig)
    pass_data = pass_data_orig.copy()
    passenger_df_trim, nodes_list = prep_plot_objs(pass_data)
    pass_data_top10_air, pass_data_top10_pass = get_top_10(pass_data)


col4, col5, col6 = st.columns([1, 8, 1])

with col5:
    # add tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Map", "Instructions", "Most Important Airports", "Most Important Routes"]
    )

    # add map to tab1
    with tab1:
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

    # add instructions to tab2
    with tab2:
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

st.write("")
st.write("")
st.write("")

st.caption(
    "Use the tables below to view and compare the most important airports and routes."
)

tab3, tab4 = st.tabs(["Most Important Airports", "Most Important Routes"])

# most important airports
with tab3:
    # display the data as a row of text for each airport
    col7, col8, col9 = st.columns([1, 1, 1])
    with col7:
        st.write("Airport Code")
    with col8:
        st.write("Airport Name")
    with col9:
        st.write("Centrality")

    # display the data as a row of text for each airport
    for airport in pass_data_top10_air_orig.iterrows():
        airport = airport[1]
        (
            col7,
            col8,
            col9,
        ) = st.columns([1, 1, 1])
        with col7:
            st.write(airport["Airport"])
        with col8:
            st.write(airport["Airport Name"])
        with col9:
            st.write(airport["Centrality"])
        st.divider()

# most important routes
with tab4:
    # display the data as a row of text for each route
    col12, col13, col14 = st.columns([1, 1, 1])
    with col12:
        st.write("Origin Airport")
    with col13:
        st.write("Destination Airport")
    with col14:
        st.write("Route Centrality")

    # display the data as a row of text for each route
    for route in pass_data_top10_pass_orig.iterrows():
        route = route[1]
        (
            col12,
            col13,
            col14,
        ) = st.columns([1, 1, 1])
        with col12:
            st.write(route["Origin Airport"])
        with col13:
            st.write(route["Desination Airport"])
        with col14:
            st.write(route["Link Centrality"])
        st.divider()
