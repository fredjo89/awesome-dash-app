import pandas as pd
from config import NODE_PATH, EDGE_PATH


def load_got():
    """
    Load the data into pandas dataframes
    """

    nodes = pd.read_csv(NODE_PATH)
    edges = pd.read_csv(EDGE_PATH)

    nodes = nodes.sort_values(by=["screentime"], ascending=False)
    edges = edges.sort_values(by=["weight"], ascending=False)

    return nodes, edges


nodes, edges = load_got()
