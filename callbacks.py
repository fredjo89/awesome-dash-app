import dash
from dash import html
from dash.dependencies import Input, Output

from data import GraphFilterParams, DFGraph, GraphData

data = GraphData()


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

        if triggered_id == "submit_button":
            print(
                'triggered_id == "submit_button". Use the inputs to visualize the subgraph.'
            )

            filter_params = GraphFilterParams(
                filter_node_screentime,
                filter_edge_weight,
                filter_node_types,
            )

            data.update_filter(filter_params)

            data.create_display_graph_from_node_neighborhood(search_node_id, num_hops)
            new_graph_data = data.create_visddc_network()

        elif triggered_id == "network_visualization":
            print('triggered_id == "network_visualization". Delete or expand node')
            if interaction_value == "expand_node":
                print("YOLO2_1", interaction_value)

                node_egonet = GraphData()
                node_egonet.create_display_graph_from_node_neighborhood(clicked_node, 1)
                data.add_subgraph_to_displaygraph(node_egonet.graph_display)

                new_graph_data = data.create_visddc_network()
            elif interaction_value == "delete_node":
                print("YOLO2_2", interaction_value)
                data.delete_node_from_display_graph(clicked_node)
                new_graph_data = data.create_visddc_network()

        print(data)

        return new_graph_data


######################################################################################
# callback_graph_summary_table
######################################################################################
def callback_graph_summary_table(app):
    @app.callback(
        Output(component_id="graph_summary_table_table", component_property="data"),
        [
            Input(component_id="graph_summary_table_table", component_property="data"),
            # Input related to interactive network functionality
            Input(component_id="submit_button", component_property="n_clicks"),
        ],
    )
    def callback_graph_summary_table(
        graph_summary_table,
        n_clicks,
    ):
        triggered_id = dash.callback_context.triggered_id
        if triggered_id != "submit_button":
            return graph_summary_table

        graph_summary_table = data.graph_display.graph_summary_table.to_dict("records")

        return graph_summary_table


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
    # callback_graph_summary_table(app)
    callback_open_url_on_node_click(app)
