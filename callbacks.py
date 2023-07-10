import dash
from dash import html
from dash.dependencies import Input, Output
from data import (
    delete_node_from_graph,
    expand_subgraph_around_single_node,
    get_subgraph_from_name,
)


######################################################################################
# Helper functions
######################################################################################
def resolve_clicked_node(clicked_node):
    if (
        clicked_node is not None
        and clicked_node["nodes"] is not None
        and len(clicked_node["nodes"]) == 1
    ):
        return clicked_node["nodes"][0]
    else:
        return None


######################################################################################
# callback_network_visualization
######################################################################################
def update_graph_after_submit(graph_data, search_node_id, num_hops):
    if search_node_id is None or num_hops is None:
        return graph_data
    else:
        return get_subgraph_from_name(search_node_id, num_hops)


######################################################################################
from data import my_super_awesome_filter


def filter_graph_data(
    triggered_id,
    graph_data,
    filter_node_types,
    filter_node_screentime,
    filter_edge_weight,
):
    filtered_graph_data = graph_data

    if triggered_id in ("submit_button", "network_visualization"):
        filtered_graph_data = my_super_awesome_filter(
            graph_data, filter_node_types, filter_node_screentime, filter_edge_weight
        )

    return filtered_graph_data


def callback_network_visualization(app):
    @app.callback(
        Output(component_id="network_visualization", component_property="data"),
        [
            # Input related to interactive network functionality
            Input(component_id="network_visualization", component_property="data"),
            Input(component_id="network_visualization", component_property="selection"),
            Input(component_id="graph_interaction_input", component_property="value"),
            # Input related to node search id and neighborhood expantion
            Input(component_id="search_node_id_input", component_property="value"),
            Input(component_id="expand_num_hops_input", component_property="value"),
            # Input related to network filtering
            Input(component_id="filter_node_type_input", component_property="value"),
            Input(
                component_id="filter_node_screentime_input", component_property="value"
            ),
            Input(component_id="filter_edge_weight_input", component_property="value"),
            # Input related to the submit button
            Input(component_id="submit_button", component_property="n_clicks"),
        ],
    )
    def callback_network_visualization(
        graph_data,
        clicked_node,
        interaction_value,
        search_node_id,
        num_hops,
        filter_node_types,
        filter_node_screentime,
        filter_edge_weight,
        n_clicks,
    ):
        triggered_id = dash.callback_context.triggered_id
        clicked_node = resolve_clicked_node(clicked_node)

        new_graph_data = graph_data

        if triggered_id is None:
            print("triggered_id is None. Nothing is supposed to happen")
            return graph_data
        elif triggered_id == "submit_button":
            print(
                'triggered_id == "submit_button". Use the inputs to visualize the subgraph.'
            )
            new_graph_data = update_graph_after_submit(
                graph_data, search_node_id, num_hops
            )
        elif triggered_id == "network_visualization":
            print('triggered_id == "network_visualization". Delete or expand node')
            if interaction_value == "expand_node":
                print("YOLO2_1", interaction_value)
                new_graph_data = expand_subgraph_around_single_node(
                    graph_data, clicked_node
                )
            elif interaction_value == "delete_node":
                print("YOLO2_2", interaction_value)
                new_graph_data = delete_node_from_graph(graph_data, clicked_node)
            else:
                return graph_data

        new_graph_data = filter_graph_data(
            triggered_id,
            new_graph_data,
            filter_node_types,
            filter_node_screentime,
            filter_edge_weight,
        )

        return new_graph_data


######################################################################################
# callback_open_url_on_node_click
######################################################################################
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


def callback_open_url_on_node_click(app):
    @app.callback(
        Output(component_id="network_visualization", component_property="run"),
        [
            # Input related to interactive network functionality
            Input(component_id="network_visualization", component_property="selection"),
            Input(component_id="graph_interaction_input", component_property="value"),
        ],
    )
    def callback_open_url_on_node_click(
        clicked_node,
        interaction_value,
    ):
        triggered_id = dash.callback_context.triggered_id
        return get_javascript(triggered_id, interaction_value, clicked_node)


######################################################################################
# register_callbacks()
######################################################################################
def register_callbacks(app):
    callback_network_visualization(app)
    callback_open_url_on_node_click(app)
