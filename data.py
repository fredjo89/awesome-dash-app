# %%

import pandas as pd
import os
from dataclasses import dataclass
from copy import copy


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
# Utilities
######################################################################################
def _calculate_slope(x1, x2, y1, y2):
    slope = (y2 - y1) / (x2 - x1)
    return slope


@dataclass
class GraphFilterParams:
    min_screentime: float
    min_edge_weight: float
    node_types_to_include: list()


######################################################################################
# DFGraph
######################################################################################
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

    def filter_graph(self, filter_params: GraphFilterParams):
        # Filter nodes based on screentime
        mask = self.nodes["screentime"] >= filter_params.min_screentime
        self.nodes = self.nodes[mask]
        # Filter nodes based on gender
        mask = self.nodes["gender"].isin(filter_params.node_types_to_include)
        self.nodes = self.nodes[mask]
        # Filter edges based on removed nodes
        mask = self.edges["from"].isin(self.nodes["id"]) | self.edges["to"].isin(
            self.nodes["id"]
        )
        self.edges = self.edges[mask]
        # Filter edges based on weight
        mask = self.edges["weight"] >= filter_params.min_edge_weight
        self.edges = self.edges[mask]

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


# %%
######################################################################################
# class GraphData:
######################################################################################
@dataclass
class GraphData:
    graph_whole: DFGraph
    graph_filtered: DFGraph
    graph_display: DFGraph

    filter_params: GraphFilterParams

    def __init__(self):
        nodes, edges = _load_got()
        self.graph_whole = DFGraph(nodes, edges)
        self.graph_filtered = DFGraph(nodes, edges)
        self.graph_display = DFGraph()

        node_types_to_include = nodes["gender"].drop_duplicates().to_list()
        self.filter_params = GraphFilterParams(0, 0, node_types_to_include)

    def __str__(self):
        s = (
            "graph_whole:    "
            + self.graph_whole.graph_size_to_str()
            + "\ngraph_filtered: "
            + self.graph_filtered.graph_size_to_str()
            + "\ngraph_display:  "
            + self.graph_display.graph_size_to_str()
        )
        return s

    def update_filter(self, new_params: GraphFilterParams):
        if new_params.min_screentime is not None:
            self.filter_params.min_screentime = new_params.min_screentime
        if new_params.min_edge_weight is not None:
            self.filter_params.min_edge_weight = new_params.min_edge_weight
        if (
            new_params.node_types_to_include is not None
            and len(new_params.node_types_to_include) > 0
        ):
            self.filter_params.node_types_to_include = new_params.node_types_to_include

        self.graph_filtered = copy(self.graph_whole)
        self.graph_filtered.filter_graph(self.filter_params)

    def create_display_graph_from_node_neighborhood(self, node_id, n_hops):
        """
        Docstring...
        """

        if n_hops is None:
            n_hops = 0
        self.graph_display = self.graph_filtered.get_neighborhood_around_node(
            node_id,
            n_hops,
        )

    def add_subgraph_to_displaygraph(self, input_graph: DFGraph):
        input_graph.filter_graph(self.filter_params)
        self.graph_display.append_graph(input_graph)

    def get_options_for_dropdown(self):
        return [{"label": i, "value": i} for i in self.graph_whole.nodes["id"]]

    def create_visddc_network(self):
        """
        Dockstring
        """
        if self.graph_display.nodes is None or self.graph_display.edges is None:
            graph_data = {"nodes": {}, "edges": {}}
            return graph_data

        dict_nodes = self.graph_display.nodes.to_dict("records")
        dict_edges = self.graph_display.edges.to_dict("records")

        node_coloring = {"male": "#7CBA36", "female": "#CC5500"}
        icon_url = "https://e7.pngegg.com/pngimages/549/612/png-clipart-three-headed-dragon-illustration-daenerys-targaryen-tyrion-lannister-sansa-stark-house-targaryen-house-stark-throne-miscellaneous-dragon-thumbnail.png"

        nodes = [
            {
                "id": node["id"],
                "label": node["id"],
                "image": icon_url,
                "shape": "circularImage",
                "borderWidth": 5,
                "size": self.graph_whole.get_node_size(node["screentime"]),
                "color": node_coloring[node["gender"]],
                "font": {
                    "size": "25",
                    "face": "'Trajan Pro', 'Times New Roman', serif",
                    "color": "#c4caca",
                },
                "title": f"Gender: {node['gender']} <br> Screentine: {node['screentime']}",
            }
            for node in dict_nodes
        ]

        edges = [
            {
                "id": edge["from"] + "__" + edge["to"],
                "from": edge["from"],
                "to": edge["to"],
                "width": self.graph_whole.get_edge_width(edge["weight"]),
            }
            for edge in dict_edges
        ]

        graph_data = {"nodes": nodes, "edges": edges}

        return graph_data

    def delete_node_from_display_graph(self, node_id):
        self.graph_display.delete_node_from_graph(node_id)


def demo():
    data = GraphData()

    data.create_display_graph_from_node_neighborhood(node_id="Brandon-Stark", n_hops=1)

    print(data)

    # display(data.graph_display.graph_summary_table)


# demo()
