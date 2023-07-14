import pandas as pd
import os
from dataclasses import dataclass
from copy import copy

DATA_PATH = os.path.join(os.getcwd(), "data")
NODE_PATH = os.path.join(DATA_PATH, "got_nodes.csv")
EDGE_PATH = os.path.join(DATA_PATH, "got_edges.csv")
FILE_PATH_FOR_IMAGES = "assets/portrait_images"


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

            self.graph_summary_table = pd.DataFrame(
                columns=["Field Description", "Value"]
            )

    def get_node_size(self, screentime):
        """
        We scale the nodes linearly in s (screentime) from node_size_min to node_size_max
        """
        node_size_min = 20
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
        nodes, edges = load_got()
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

        if new_params.node_types_to_include is not None:
            if len(new_params.node_types_to_include) > 0:
                self.filter_params.node_types_to_include = (
                    new_params.node_types_to_include
                )
            else:
                self.filter_params.node_types_to_include = (
                    self.graph_whole.nodes["gender"].drop_duplicates().to_list()
                )

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

        node_coloring = {"male": "#63748D", "female": "#CC5500"}

        def create_portrait_image_path(node):
            image_path = os.path.join(FILE_PATH_FOR_IMAGES, f"{node['id']}.png")

            if os.path.exists(image_path):
                return image_path
            else:
                return "https://e7.pngegg.com/pngimages/549/612/png-clipart-three-headed-dragon-illustration-daenerys-targaryen-tyrion-lannister-sansa-stark-house-targaryen-house-stark-throne-miscellaneous-dragon-thumbnail.png"

        nodes = [
            {
                "id": node["id"],
                "label": None,
                "image": create_portrait_image_path(node),
                "shape": "circularImage",
                "imagePadding": {"left": 200, "top": 100, "right": 80, "bottom": 20},
                "borderWidth": 10,
                "size": self.graph_whole.get_node_size(node["screentime"]),
                "color": node_coloring[node["gender"]],
                "font": {
                    "size": "20",
                    "face": "'Trajan Pro'",
                    "color": "white",
                },
                "title": f"""Name: {node["id"].replace("-", " ")} <br> Gender: {node['gender']} <br> Screentine: {node['screentime']}""",
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

    def create_datatable_to_display(self):
        """
        self.create_display_graph_from_node_neighborhood(
            node_id="Brandon-Stark", n_hops=1
        )
        """

        data_to_display = self.graph_display.graph_summary_table

        fields_to_display = [
            "Number of nodes",
            "Number of edges",
            "screentime_sum",
            "screentime_median",
            "weight_sum",
            "weight_median",
        ]
        mask = data_to_display["Field Description"].isin(fields_to_display)

        data_to_display = data_to_display[mask]
        data_to_display = data_to_display.to_dict("records")

        return data_to_display


# %%


def demo():
    return None
