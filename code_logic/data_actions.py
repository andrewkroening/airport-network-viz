"""Module for loading and actioning datasets"""

# imports
import pandas as pd
import networkx as nx


def load_tabular_edge_data():
    pass


def load_node_data():
    pass


def year_network(G, year):
    """Extract edges for a particular year from
    a MultiGraph. The edge is also populated with
    two attributes, weight and weight_inv where
    weight is the number of passengers and
    weight_inv the inverse of it.
    """
    year_network = nx.DiGraph()
    for edge in G.edges:
        source, target, edge_year = edge
        if edge_year == year:
            attr = G[source][target][edge_year]
            year_network.add_edge(
                source,
                target,
                weight=attr["PASSENGERS"],
                weight_inv=1 / (attr["PASSENGERS"] if attr["PASSENGERS"] != 0.0 else 1),
                airlines=attr["UNIQUE_CARRIER_NAME"],
            )
    return year_network


def load_airports_GPS_data(G, year):
    """Loads the GPS data for all airports in the US"""

    lat_long = pd.read_csv(
        "../00_data/GlobalAirportDatabase.txt", delimiter=":", header=None
    )

    lat_long.columns = [
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

    # get the year network
    pass_year_network = year_network(G, year)

    wanted_nodes = list(pass_year_network.nodes())

    us_airports = (
        lat_long.query("CODE3 in @wanted_nodes")
        .drop_duplicates(subset=["CODE3"])
        .set_index("CODE3")
    )

    no_gps = []
    for n, d in pass_year_network.nodes(data=True):
        try:
            pass_year_network.nodes[n]["longitude"] = us_airports.loc[n, "LONGITUDE"]
            pass_year_network.nodes[n]["latitude"] = us_airports.loc[n, "LATITUDE"]
            pass_year_network.nodes[n]["degree"] = pass_year_network.degree(n)

        # Some of the nodes are not represented
        except KeyError:
            no_gps.append(n)

    # Get subgraph of nodes that do have GPS coords
    has_gps = set(pass_year_network.nodes()).difference(no_gps)
    g = pass_year_network.subgraph(has_gps)

    return us_airports
    # us_airports
