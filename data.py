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


df_nodes, df_edges = _load_got()


def get_node_screentime_range(df_nodes=df_nodes):
    return df_nodes["screentime"].min(), df_nodes["screentime"].max()


def _scale_node_size(s):
    """
    We scale the nodes linearly in s (screentime) from node_size_min to node_size_max
    """
    s_min, s_max = get_node_screentime_range()
    node_size_min = 5
    node_size_max = 50

    slope = (node_size_max - node_size_min) / (s_max - s_min)

    node_size = slope * (s - s_min) + node_size_min

    return node_size


def get_edge_weight_range(df_edges=df_edges):
    return df_edges["weight"].min(), df_edges["weight"].max()


def _scale_edge_size(w):
    """
    We scale the edge widths linearly in w (weight) from edge_width_min to edge_width_max
    """
    w_min, w_max = get_edge_weight_range()
    edge_width_min = 2
    edge_width_max = 15

    slope = (edge_width_max - edge_width_min) / (w_max - w_min)

    edge_width = slope * (w - w_min) + edge_width_min

    return edge_width


def create_visddc_network(dict_nodes, dict_edges):
    """
    Dockstring
    """
    if dict_nodes is None or dict_edges is None:
        graph_data = {"nodes": {}, "edges": {}}
        return graph_data

    node_coloring = {"male": "#7CBA36", "female": "#CC5500"}
    icon_url = "https://e7.pngegg.com/pngimages/549/612/png-clipart-three-headed-dragon-illustration-daenerys-targaryen-tyrion-lannister-sansa-stark-house-targaryen-house-stark-throne-miscellaneous-dragon-thumbnail.png"

    nodes = [
        {
            "id": node["id"],
            "label": node["id"],
            "image": icon_url,
            "shape": "circularImage",
            "borderWidth": 5,
            "size": _scale_node_size(node["screentime"]),
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
            "width": _scale_edge_size(edge["weight"]),
        }
        for edge in dict_edges
    ]

    graph_data = {"nodes": nodes, "edges": edges}

    return graph_data


def get_subgraph_from_name(my_name, num_hops):
    ids = {my_name}
    if num_hops == None:
        num_hops = 0

    # Expand Graph n hops
    for hop in range(num_hops):
        from_mask = df_edges["from"].isin(ids)
        to_mask = df_edges["to"].isin(ids)
        ids.update(df_edges[from_mask]["to"])
        ids.update(df_edges[to_mask]["from"])

    mask = (df_nodes["id"].isin(ids)) | (df_nodes["id"].isin(ids))
    df_nodes_subset = df_nodes[mask]

    mask = (df_edges["from"].isin(ids)) & (df_edges["to"].isin(ids))
    df_edges_subset = df_edges[mask]

    graph_data = create_visddc_network(
        df_nodes_subset.to_dict("records"), df_edges_subset.to_dict("records")
    )

    return graph_data


def _get_graph_union(graph_1, graph_2):
    """
    Returns the union of nodes and edges of the two input-graphs
    """
    nodes = graph_1["nodes"] + graph_2["nodes"]
    ids = {n["id"] for n in nodes}

    mask = df_nodes["id"].isin(ids)
    df_nodes_subset = df_nodes[mask]

    mask = (df_edges["from"].isin(ids)) & (df_edges["to"].isin(ids))
    df_edges_subset = df_edges[mask]

    graph_data = create_visddc_network(
        df_nodes_subset.to_dict("records"), df_edges_subset.to_dict("records")
    )

    return graph_data


def expand_subgraph_around_single_node(graph_data, expand_node_id):
    new_neighborhood = get_subgraph_from_name(expand_node_id, 1)

    expaned_graph = _get_graph_union(graph_data, new_neighborhood)
    return expaned_graph


def get_options_for_dropdown():
    options = [{"label": i, "value": i} for i in df_nodes["id"]]
    return options


def delete_node_from_graph(graph_data, node_name):
    nodes = [n for n in graph_data["nodes"] if n["id"] != node_name]
    edges = [
        e
        for e in graph_data["edges"]
        if e["from"] != node_name and e["to"] != node_name
    ]
    new_graph_data = {"nodes": nodes, "edges": edges}
    return new_graph_data


def my_super_awesome_filter(
    graph_data, filter_node_types, filter_node_screentime, filter_edge_weight
):
    ids = {n["id"] for n in graph_data["nodes"]}
    mask = df_nodes["id"].isin(ids)
    df_nodes_subset = df_nodes[mask]

    if filter_node_types is not None and len(filter_node_types) > 0:
        mask = df_nodes_subset["gender"].isin(filter_node_types)
        df_nodes_subset = df_nodes_subset[mask]
    if filter_node_screentime is not None:
        mask = df_nodes_subset["screentime"] >= filter_node_screentime
        df_nodes_subset = df_nodes_subset[mask]

    mask = (df_edges["from"].isin(df_nodes["id"])) & (
        df_edges["to"].isin(df_nodes["id"])
    )
    df_edges_subset = df_edges[mask]

    if filter_edge_weight is not None:
        mask = df_edges_subset["weight"] >= filter_edge_weight
        df_edges_subset = df_edges_subset[mask]

    filtered_graph_data = create_visddc_network(
        df_nodes_subset.to_dict("records"), df_edges_subset.to_dict("records")
    )

    return filtered_graph_data
