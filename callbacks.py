import dash
from dash import html
from dash.dependencies import Input, Output


def _create_url_from_node_name(node_name):
    node_name = node_name.replace("-", "_")
    url = f"""https://gameofthrones.fandom.com/wiki/{node_name}"""
    return url


def callback_dev(app):
    @app.callback(
        [
            Output(component_id="network_visualization", component_property="data"),
            Output(component_id="network_visualization", component_property="run"),
        ],
        [
            Input(component_id="network_visualization", component_property="data"),
            Input(component_id="network_visualization", component_property="selection"),
        ],
    )
    def callback_dev(graph_data, selection):
        javascript = ""

        if (
            selection is not None
            and selection["nodes"] is not None
            and len(selection["nodes"]) == 1
        ):
            node_name = selection["nodes"][0]
            url = _create_url_from_node_name(node_name)
            javascript = f"""window.open('{url}')"""

        return [graph_data, javascript]


def register_callbacks(app):
    callback_dev(app)
