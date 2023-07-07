import dash
from dash import html
from dash.dependencies import Input, Output
from data import delete_node_from_graph, expand_subgraph_around_single_node, get_subgraph_from_name


def resolve_clicked_node(clicked_node):
    if (
        clicked_node is not None
        and clicked_node["nodes"] is not None
        and len(clicked_node["nodes"]) == 1
    ): 
        return clicked_node["nodes"][0]
    else: 
         return None

def _create_url_from_node_name(node_name):
    node_name = node_name.replace("-", "_")
    url = f"""https://gameofthrones.fandom.com/wiki/{node_name}"""
    return url


def get_javascript(triggered_id, interaction_value, clicked_node):
    javascript = ""
    node_name = resolve_clicked_node(clicked_node)
    if (
        triggered_id == "network_visualization" 
        and interaction_value == "node_wiki"
        and node_name is not None
        ):
            url = _create_url_from_node_name(node_name)
            javascript = f"""window.open('{url}')"""
    return javascript


def get_new_graph_data(triggered_id, interaction_value, graph_data, clicked_node, search_node_id, num_hops):
    new_graph_data = graph_data

    node_name = resolve_clicked_node(clicked_node)

    if (
        triggered_id == "network_visualization" 
        and interaction_value == "delete_node"
        and node_name is not None
        ):
            new_graph_data = delete_node_from_graph(graph_data, node_name)
    elif (
        triggered_id == "network_visualization" 
        and interaction_value == "expand_node"
        and node_name is not None
        ):
            new_graph_data = expand_subgraph_around_single_node(graph_data, node_name)
    elif triggered_id == "submit_button" and search_node_id is not None:
         new_graph_data = get_subgraph_from_name(search_node_id, num_hops)
    return new_graph_data

from data import my_super_awesome_filter


def filter_graph_data(triggered_id, graph_data, filter_node_types, filter_node_screentime, filter_edge_weight):
    filtered_graph_data = graph_data
    
    if triggered_id in ("submit_button", "network_visualization"):
        filtered_graph_data = my_super_awesome_filter(graph_data, filter_node_types, filter_node_screentime, filter_edge_weight)

    return filtered_graph_data

def callback_dev(app):
    @app.callback(
        [
            Output(component_id="network_visualization", component_property="data"),
            Output(component_id="network_visualization", component_property="run"),
        ],
        [
            Input(component_id="network_visualization", component_property="data"),
            Input(component_id="network_visualization", component_property="selection"),
            Input(component_id="graph_interaction_input", component_property="value"),
            #
            Input(component_id="search_node_id_input", component_property="value"),
            Input(component_id="expand_num_hops_input", component_property="value"),
            #
            Input(component_id="filter_node_type_input", component_property="value"),
            Input(component_id="filter_node_screentime_input", component_property="value"),
            Input(component_id="filter_edge_weight_input", component_property="value"),
            #
            Input(component_id="submit_button", component_property="n_clicks"),
        ],
    )
    def callback_dev(graph_data, clicked_node, interaction_value, search_node_id, num_hops, filter_node_types, filter_node_screentime, filter_edge_weight, n_clicks):
        triggered_id = dash.callback_context.triggered_id

        javascript = get_javascript(triggered_id, interaction_value, clicked_node)
        new_graph_data = get_new_graph_data(triggered_id, interaction_value, graph_data, clicked_node, search_node_id, num_hops)

        new_graph_data = filter_graph_data(triggered_id, new_graph_data, filter_node_types, filter_node_screentime, filter_edge_weight)

        return [new_graph_data, javascript]


def register_callbacks(app):
    callback_dev(app)
