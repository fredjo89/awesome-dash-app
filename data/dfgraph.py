from dataclasses import dataclass
import pandas as pd
from .utils import calculate_slope, GraphFilterParams


@dataclass
class DFGraph:
    nodes: pd.DataFrame
    edges: pd.DataFrame

    graph_summary_table: pd.DataFrame

    screentime_min: float
    screentime_max: float
    edge_weight_min: float
    edge_weight_max: float

    def __init__(self, nodes=None, edges=None):
        if nodes is not None and edges is not None:
            self.nodes = nodes
            self.edges = edges
            self.update_graph(self)
        else:
            self.nodes = None
            self.edges = None
            self.screentime_min = 0
            self.screentime_max = 0

            self.edge_weight_min = 0
            self.edge_weight_max = 0

            self.graph_summary_table = pd.DataFrame(
                columns=["Field Description", "Value"]
            )

    def get_node_size(self, screentime):
        """
        We scale the nodes linearly in s (screentime) from node_size_min to node_size_max
        """
        node_size_min = 20
        node_size_max = 50
        slope = calculate_slope(
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
        slope = calculate_slope(
            self.edge_weight_min,
            self.edge_weight_max,
            edge_width_min,
            edge_width_max,
        )
        edge_width = slope * (edge_weight - self.edge_weight_min) + edge_width_min
        return edge_width

    def update_graph(self, graph):
        self.nodes = (
            graph.nodes.drop_duplicates()
            .sort_values(by="screentime", ascending=False)
            .reset_index(drop=True)
        )

        self.edges = (
            graph.edges.drop_duplicates()
            .sort_values(by="weight", ascending=False)
            .reset_index(drop=True)
        )

        self.screentime_min = self.nodes["screentime"].min()
        self.screentime_max = self.nodes["screentime"].max()

        self.edge_weight_min = self.edges["weight"].min()
        self.edge_weight_max = self.edges["weight"].max()

        self.create_graph_summary_table()

    def append_graph(self, input_graph):
        """
        Docstring
        """
        nodes = pd.concat([self.nodes, input_graph.nodes])
        edges = pd.concat([self.edges, input_graph.edges])
        graph = DFGraph()
        graph = DFGraph(nodes, edges)
        self.update_graph(graph)

    def get_neighborhood_around_node(self, node_id, n_hops):
        """
        Docstring...
        """
        # Initialise nodes
        mask = self.nodes["id"] == node_id
        nodes = self.nodes[mask]
        # Initialize edges
        edges = self.edges.drop(self.edges.index)
        # Initialize node_ids
        node_ids = set(nodes["id"])
        # Expand neighborhood by iterating n_hops
        for hop in range(n_hops):
            # Update edges
            mask = self.edges["from"].isin(node_ids) | self.edges["to"].isin(node_ids)
            edges = self.edges[mask]
            # Update node ids
            node_ids.update(edges["from"])
            node_ids.update(edges["to"])
            # Update nodes
            mask = self.nodes["id"].isin(node_ids)
            nodes = self.nodes[mask]

        return DFGraph(nodes, edges)

    def _remove_edges_with_invalid_node_ids(self):
        # Filter edges to retain only those with valid 'from' and 'to' node IDs
        # This happens when nodes are filtered out, and promts the need to remove edges that are no longer valid.
        mask = self.edges["from"].isin(self.nodes["id"]) & self.edges["to"].isin(
            self.nodes["id"]
        )
        self.edges = self.edges[mask]

    def _filter_edges_using_weight(self, min_edge_weight):
        mask = self.edges["weight"] >= min_edge_weight
        self.edges = self.edges[mask]

    def _filter_nodes_using_screentime(self, min_screentime):
        mask = self.nodes["screentime"] >= min_screentime
        self.nodes = self.nodes[mask]
        self._remove_edges_with_invalid_node_ids()

    def _filter_nodes_using_node_types(self, node_types_to_include):
        mask = self.nodes["gender"].isin(node_types_to_include)
        self.nodes = self.nodes[mask]
        self._remove_edges_with_invalid_node_ids()

    def filter_graph(self, filter_params: GraphFilterParams):
        self._filter_nodes_using_screentime(filter_params.min_screentime)
        self._filter_nodes_using_node_types(filter_params.node_types_to_include)
        self._filter_edges_using_weight(filter_params.min_edge_weight)

        self.update_graph(self)

    def delete_node_from_graph(self, node_id):
        mask = ~(self.nodes["id"] == node_id)
        self.nodes = self.nodes[mask]

        mask = ~((self.edges["from"] == node_id) | (self.edges["to"] == node_id))
        self.edges = self.edges[mask]

    def __str__(self):
        display(self.nodes)
        display(self.edges)
        return ""

    def graph_size_to_str(self):
        if self.nodes is None:
            num_nodes = 0
        else:
            num_nodes = self.nodes.shape[0]
        if self.edges is None:
            num_edges = 0
        else:
            num_edges = self.edges.shape[0]
        return f"Number of nodes: {num_nodes}, Number of edges: {num_edges}"

    def create_graph_summary_table(self):
        nodes = self.nodes
        edges = self.edges

        num_nodes = nodes.shape[0]
        num_edges = edges.shape[0]

        screentime_sum = nodes["screentime"].sum()
        screentime_mean = nodes["screentime"].mean()
        screentime_median = nodes["screentime"].median()

        weight_sum = edges["weight"].sum()
        weight_mean = edges["weight"].mean()
        weight_median = edges["weight"].median()

        self.graph_summary_table = pd.DataFrame(
            columns=[
                "Field Description",
                "Value",
            ],
            data=[
                ["Number of nodes", num_nodes],
                ["Number of edges", num_edges],
                ["screentime_sum", screentime_sum],
                ["screentime_mean", screentime_mean],
                ["screentime_median", screentime_median],
                ["weight_sum", weight_sum],
                ["weight_mean", weight_mean],
                ["weight_median", weight_median],
            ],
        )
