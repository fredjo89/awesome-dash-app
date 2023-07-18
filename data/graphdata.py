import os
from copy import copy
from dataclasses import dataclass
from .utils import GraphFilterParams
from .dfgraph import DFGraph
from .load_data import load_got
from config import FILE_PATH_FOR_IMAGES


def create_portrait_image_path(node):
    image_path = os.path.join(FILE_PATH_FOR_IMAGES, f"{node['id']}.png")

    if os.path.exists(image_path):
        return image_path
    else:
        return "https://e7.pngegg.com/pngimages/549/612/png-clipart-three-headed-dragon-illustration-daenerys-targaryen-tyrion-lannister-sansa-stark-house-targaryen-house-stark-throne-miscellaneous-dragon-thumbnail.png"


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

        node_coloring = {"male": "#FCFEF0", "female": "#B9540C"}

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
