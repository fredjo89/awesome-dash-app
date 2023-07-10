# %%

import pandas as pd
import os


def _load_got():
    """
    Load the data into pandas dataframes
    """

    data_directory = os.path.join(os.getcwd(), "data")

    df_nodes = pd.read_csv(os.path.join(data_directory, "got_nodes.csv"))
    df_edges = pd.read_csv(os.path.join(data_directory, "got_edges.csv"))

    df_nodes = df_nodes.drop(columns=["node_image_url"])
    df_nodes = df_nodes.sort_values(by=["screentime"], ascending=False)
    df_edges = df_edges.sort_values(by=["weight"], ascending=False)

    return df_nodes, df_edges


######################################################################################
# dataclass...
######################################################################################


# %%
def _calculate_slope(x1, x2, y1, y2):
    slope = (y2 - y1) / (x2 - x1)
    return slope


from dataclasses import dataclass

df_nodes, df_edges = _load_got()


@dataclass
class GraphData:
    df_nodes: pd.DataFrame
    df_edges: pd.DataFrame

    df_nodes_display: pd.DataFrame
    df_edges_display: pd.DataFrame

    screentime_min: float
    screentime_max: float

    edge_weight_min: float
    edge_weight_max: float

    def __init__(self):
        df_nodes, df_edges = _load_got()
        self.df_nodes = df_nodes
        self.df_edges = df_edges

        self.df_nodes_display = None
        self.df_edges_display = None

        #
        self.screentime_min = df_nodes["screentime"].min()
        self.screentime_max = df_nodes["screentime"].max()
        #
        self.edge_weight_min = df_edges["weight"].min()
        self.edge_weight_max = df_edges["weight"].max()

    def get_node_size(self, screentime):
        """
        We scale the nodes linearly in s (screentime) from node_size_min to node_size_max
        """
        node_size_min = 5
        node_size_max = 50
        slope = _calculate_slope(
            self.screentime_min,
            self.screentime_max,
            node_size_min,
            node_size_max,
        )
        node_size = slope * (screentime - self.screentime_min) + node_size_min
        return node_size

    def get_edge_width(self, edge_weight):
        """
        We scale the edge widths linearly in w (weight) from edge_width_min to edge_width_max
        """
        edge_width_min = 2
        edge_width_max = 15
        slope = _calculate_slope(
            self.edge_weight_min,
            self.edge_weight_max,
            edge_width_min,
            edge_width_max,
        )
        edge_width = slope * (edge_weight - self.edge_weight_min) + edge_width_min
        return edge_width

    def create_neighborhood_around_node(self, node_id, n_hops):
        """
        Docstring...
        """
        # Initialise nodes
        mask = self.df_nodes["id"] == node_id
        nodes = self.df_nodes[mask]
        # Initialize edges
        edges = self.df_edges.drop(df_edges.index)
        # Initialize node_ids
        node_ids = set(nodes["id"])
        # Expand neighborhood by iterating n_hops
        for hop in range(n_hops):
            # Update edges
            mask = self.df_edges["from"].isin(node_ids) | self.df_edges["to"].isin(
                node_ids
            )
            edges = self.df_edges[mask]
            # Update node ids
            node_ids.update(edges["from"])
            node_ids.update(edges["to"])
            # Update nodes
            mask = self.df_nodes["id"].isin(node_ids)
            nodes = self.df_nodes[mask]

        return nodes, edges

    def _TEMPFUNK_update_displaygraph_1(self):
        node_id = "Luwin"
        n_hops = 1
        (
            self.df_nodes_display,
            self.df_edges_display,
        ) = self.create_neighborhood_around_node(node_id, n_hops)

    def add_subgraph_to_displaygraph(self, nodes, edges):
        self.df_nodes_display = pd.concat(
            [self.df_nodes_display, nodes], ignore_index=True
        ).drop_duplicates()
        self.df_edges_display = pd.concat(
            [self.df_edges_display, edges], ignore_index=True
        ).drop_duplicates()


graph = GraphData()

graph._TEMPFUNK_update_displaygraph_1()

node_id = "Catelyn-Stark"
n_hops = 1
nodes, edges = graph.create_neighborhood_around_node(node_id, n_hops)


graph.add_subgraph_to_displaygraph(nodes, edges)
print(nodes)

# graph.df_edges_display
