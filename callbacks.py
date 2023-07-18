# %%
import dash
from dash import html
from dash.dependencies import Input, Output
from data.graphdata import GraphData
from data.utils import GraphFilterParams

data = GraphData()


def resolve_clicked_node(clicked_node):
    if (
        clicked_node is not None
        and clicked_node["nodes"] is not None
        and len(clicked_node["nodes"]) == 1
    ):
        return clicked_node["nodes"][0]
    else:
        return None


def create_url_from_node_name(node_name):
    node_name = node_name.replace("-", "_")
    url = f"""https://gameofthrones.fandom.com/wiki/{node_name}"""
    return url


def create_javascript_for_character_url(triggered_id, interaction_value, clicked_node):
    javascript = ""
    node_name = resolve_clicked_node(clicked_node)
    if (
        triggered_id == "network_visualization"
        and interaction_value == "node_wiki"
        and node_name is not None
    ):
        url = create_url_from_node_name(node_name)
        javascript = f"""window.open('{url}')"""
    return javascript


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
                component_id="filter_node_screentime_input_input",
                component_property="value",
            ),
            Input(
                component_id="filter_edge_weight_input_input",
                component_property="value",
            ),
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

        if triggered_id not in ("submit_button", "network_visualization"):
            return graph_data
        elif triggered_id == "submit_button":
            filter_params = GraphFilterParams(
                filter_node_screentime,
                filter_edge_weight,
                filter_node_types,
            )
            data.update_filter(filter_params)
            data.create_display_graph_from_node_neighborhood(search_node_id, num_hops)
        elif triggered_id == "network_visualization":
            if interaction_value == "expand_node":
                node_egonet = GraphData()
                node_egonet.create_display_graph_from_node_neighborhood(clicked_node, 1)
                data.add_subgraph_to_displaygraph(node_egonet.graph_display)
            elif interaction_value == "delete_node":
                data.delete_node_from_display_graph(clicked_node)

        return data.create_visddc_network()


def callback_sync_screentime_input(app):
    @app.callback(
        [
            Output(
                component_id="filter_node_screentime_slider_input",
                component_property="value",
            ),
            Output(
                component_id="filter_node_screentime_input_input",
                component_property="value",
            ),
        ],
        [
            Input(
                component_id="filter_node_screentime_slider_input",
                component_property="value",
            ),
            Input(
                component_id="filter_node_screentime_input_input",
                component_property="value",
            ),
        ],
    )
    def callback_screentime_input(
        slider_value,
        input_value,
    ):
        triggered_id = dash.callback_context.triggered_id
        if triggered_id == "filter_node_screentime_slider_input":
            return [slider_value, slider_value]
        elif triggered_id == "filter_node_screentime_input_input":
            return [input_value, input_value]
        else:
            return [slider_value, input_value]


def callback_sync_edge_weight_input(app):
    @app.callback(
        [
            Output(
                component_id="filter_edge_weight_slider_input",
                component_property="value",
            ),
            Output(
                component_id="filter_edge_weight_input_input",
                component_property="value",
            ),
        ],
        [
            Input(
                component_id="filter_edge_weight_slider_input",
                component_property="value",
            ),
            Input(
                component_id="filter_edge_weight_input_input",
                component_property="value",
            ),
        ],
    )
    def callback_edge_weight_input(
        slider_value,
        input_value,
    ):
        triggered_id = dash.callback_context.triggered_id
        if triggered_id == "filter_edge_weight_slider_input":
            return [slider_value, slider_value]
        elif triggered_id == "filter_edge_weight_input_input":
            return [input_value, input_value]
        else:
            return [slider_value, input_value]


def callback_graph_summary_table(app):
    @app.callback(
        Output(component_id="graph_summary_table_table", component_property="data"),
        [
            Input(component_id="network_visualization", component_property="data"),
        ],
    )
    def callback_graph_summary_table(_):
        graph_summary_table = data.graph_display.graph_summary_table.to_dict("records")

        graph_summary_table = data.create_datatable_to_display()

        return graph_summary_table


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
        return create_javascript_for_character_url(
            triggered_id, interaction_value, clicked_node
        )


def register_callbacks(app):
    callback_network_visualization(app)
    callback_sync_screentime_input(app)
    callback_sync_edge_weight_input(app)
    callback_graph_summary_table(app)
    callback_open_url_on_node_click(app)
