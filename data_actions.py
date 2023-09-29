# usr/bin/env python3
"""Module for loading and actioning datasets"""

# imports
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl


def load_passenger_data():
    """Function to read the passenger data and create a graph

    Returns:
        passenger_graph: networkx graph
    """

    # load passenger data
    pass_air_data = pd.read_csv(
        "./00_data/passengers.csv",
    )

    # remove rows with 'SPB', 'SSB', 'AIK', 'PCA'
    pass_air_data = pass_air_data[
        ~pass_air_data["ORIGIN"].isin(["SPB", "SSB", "AIK", "PCA"])
    ]

    # remove rows with 'SPB', 'SSB', 'AIK', 'PCA'
    pass_air_data = pass_air_data[
        ~pass_air_data["DEST"].isin(["SPB", "SSB", "AIK", "PCA"])
    ]

    # create passenger graph
    passenger_graph = nx.from_pandas_edgelist(
        pass_air_data,
        source="ORIGIN",
        target="DEST",
        edge_key="YEAR",
        edge_attr=["PASSENGERS", "UNIQUE_CARRIER_NAME"],
        create_using=nx.MultiDiGraph(),
    )

    return passenger_graph


def load_airports_GPS_data():
    """Function to read the airport data and create a df

    Returns:
        us_airports: pandas dataframe
    """

    # load airport data
    all_airports = pd.read_csv(
        "./00_data/GlobalAirportDatabase.txt",
        delimiter=":",
        header=None,
    )

    # rename columns
    all_airports.columns = [
        "CODE4",
        "CODE3",
        "CITY",
        "PROVINCE",
        "COUNTRY",
        "UNKNOWN1",
        "UNKNOWN2",
        "UNKNOWN3",
        "UNKNOWN4",
        "UNKNOWN5",
        "UNKNOWN6",
        "UNKNOWN7",
        "UNKNOWN8",
        "UNKNOWN9",
        "LATITUDE",
        "LONGITUDE",
    ]

    # filter to only US airports
    all_airports = all_airports[all_airports["COUNTRY"] == "USA"]

    # filter to lat long in the continental US
    us_airports = all_airports.query(
        "LATITUDE > 20 and LATITUDE < 50 and LONGITUDE > -130 and LONGITUDE < -60"
    )

    # drop some columns
    us_airports = us_airports.drop(
        columns=[
            "UNKNOWN1",
            "UNKNOWN2",
            "UNKNOWN3",
            "UNKNOWN4",
            "UNKNOWN5",
            "UNKNOWN6",
            "UNKNOWN7",
            "UNKNOWN8",
            "UNKNOWN9",
        ]
    )

    us_airports = us_airports.sort_values(by="CODE3").reset_index(drop=True)

    return us_airports


def year_network(G, year):
    """Extract edges for a particular year from a MultiGraph. The edge is also populated with two attributes,
    weight and weight_inv where weight is the number of passengers and weight_inv the inverse of it.

    Args:
        G: MultiGraph
        year: int

    Returns:
        year_network: DiGraph"""

    # initialize empty DiGraph
    year_network_graph = nx.DiGraph()

    # loop through the edges and add them to the DiGraph
    for edge in G.edges:
        source, target, edge_year = edge

        # check if the edge is from the year we want
        if edge_year == year:
            # add edge to the DiGraph with inverse weight
            attr = G[source][target][edge_year]
            year_network_graph.add_edge(
                source,
                target,
                weight=attr["PASSENGERS"],
                weight_inv=1 / (attr["PASSENGERS"] if attr["PASSENGERS"] != 0.0 else 1),
                airlines=attr["UNIQUE_CARRIER_NAME"],
            )

    return year_network_graph


def clean_network(pass_network, airport_data):
    """Function to clean the network by removing nodes with no GPS coordinates or no edges

    Args:
        pass_network: DiGraph
        airport_data: pandas dataframe

    Returns:
        G_clean: DiGraph"""

    wanted_nodes = list(pass_network.nodes())

    airport_data = (
        airport_data.query("CODE3 in @wanted_nodes")
        .drop_duplicates(subset=["CODE3"])
        .set_index("CODE3")
    )

    # remove nodes with no GPS coordinates
    no_gps = []

    # loop the nodes
    for n, d in pass_network.nodes(data=True):
        try:
            pass_network.nodes[n]["longitude"] = airport_data.loc[n, "LONGITUDE"]
            pass_network.nodes[n]["latitude"] = airport_data.loc[n, "LATITUDE"]
            pass_network.nodes[n]["degree"] = pass_network.degree(n)
            pass_network.nodes[n]["city"] = airport_data.loc[n, "CITY"]

        # Some of the nodes are not represented
        except KeyError:
            no_gps.append(n)

    # Get a set of nodes that do have GPS coords
    has_gps = set(pass_network.nodes()).difference(no_gps)

    # turn into a subgraph
    G_clean = pass_network.subgraph(has_gps)

    return G_clean


def add_metrics(pass_network):
    """Add network metrics to the nodes and edges

    Args:
        pass_network: DiGraph

    Returns:
        pass_network: DiGraph"""

    # add page rank to the nodes weighted by weight_inv
    pr = nx.pagerank(pass_network, weight="weight_inv")
    nx.set_node_attributes(pass_network, pr, "page_rank")

    # add betweenness centrality to the nodes weighted by weight_inv
    bc = nx.betweenness_centrality(pass_network, weight="weight_inv")
    nx.set_node_attributes(pass_network, bc, "betweenness_centrality")

    # add eigenvector centrality to the nodes weighted by weight_inv
    ec = nx.eigenvector_centrality(pass_network, weight="weight_inv")
    nx.set_node_attributes(pass_network, ec, "eigenvector_centrality")

    # add edge betweenness centrality to the edges weighted by weight_inv
    ec = nx.edge_betweenness_centrality(pass_network, weight="weight_inv")
    nx.set_edge_attributes(pass_network, ec, "edge_betweenness_centrality")

    # add source lat and long to the edges from the nodes
    for source, target, d in pass_network.edges(data=True):
        pass_network.edges[source, target]["source_lat"] = pass_network.nodes[source][
            "latitude"
        ]
        pass_network.edges[source, target]["source_long"] = pass_network.nodes[source][
            "longitude"
        ]

        pass_network.edges[source, target]["target_lat"] = pass_network.nodes[target][
            "latitude"
        ]

        pass_network.edges[source, target]["target_long"] = pass_network.nodes[target][
            "longitude"
        ]

    return pass_network


def main_runner(year):
    """Main function to execute the initial build of the network

    Parameters
    ----------
    year : int
        Year to build the network for

    Returns"""

    # load passenger data
    passenger_graph = load_passenger_data()

    # load the airport network
    airport_data = load_airports_GPS_data()

    # create a network for the year
    year_graph = year_network(passenger_graph, year)

    # clean the year_graph
    year_graph_clean = clean_network(year_graph, airport_data)

    # add metrics to network
    year_graph_clean_metrics = add_metrics(year_graph_clean)

    # return the passenger graph
    return year_graph_clean_metrics


def unnormalize(x):
    """Function to unnormalize values

    Args:
        x: float

    Returns:
        hexcolor: color in hex format
    """

    # make an colormap for the nodes
    plot_cmap = plt.cm.Spectral

    # define ranges
    OldMin = 0
    OldMax = 1
    NewMin = 10
    NewMax = 255

    # define the old value
    OldValue = x

    # calculate the new value
    OldRange = OldMax - OldMin
    NewRange = NewMax - NewMin
    new_color = int((((OldValue - OldMin) * NewRange) / OldRange) + NewMin)

    # get the color from the colormap
    new_color = plot_cmap(new_color)

    # convert the node color to hex
    hexcolor = mpl.colors.rgb2hex(new_color)

    return hexcolor


def get_size(x):
    """Function to unnormalize values

    Args:
        x: float

    Returns:
        new_size: color in hex format
    """

    # define ranges
    OldMin = 0
    OldMax = 1
    NewMin = 1
    NewMax = 50

    # define the old value
    OldValue = x

    # calculate the new value
    OldRange = OldMax - OldMin
    NewRange = NewMax - NewMin
    new_size = int((((OldValue - OldMin) * NewRange) / OldRange) + NewMin)

    return new_size


def prep_plot_objs(pass_data):
    """converys the networkx graph into a list of nodes and edges for plotting

    Args:
        pass_data: DiGraph

    Returns:
        passenger_df_trim: pandas dataframe
        nodes_list: list
    """

    # make a list of all nodes and betweenness centrality
    nodes_list = list(pass_data.nodes())

    # sort the list by betweenness centrality
    nodes_list = sorted(
        nodes_list,
        key=lambda x: pass_data.nodes[x]["betweenness_centrality"],
        reverse=False,
    )

    pass_data = nx.to_pandas_edgelist(pass_data)

    # trim passenger data to only the top 2500 rows
    passenger_df_trim = pass_data.sort_values(by="weight", ascending=False).head(2500)

    return passenger_df_trim, nodes_list
