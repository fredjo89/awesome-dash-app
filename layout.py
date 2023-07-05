from dash import dcc, html
import visdcc

## ------------------------------------------------------------------------------- ##
## header  ##
## ------------------------------------------------------------------------------- ##
header = html.Header(
    id="header",
    children="Game of Thrones Network",
    className="header",
)


## ------------------------------------------------------------------------------- ##
## Menu Section  ##
## ------------------------------------------------------------------------------- ##

menu_section = html.Div(
    children="Menu Section",
    className="menu_section",
)


## ------------------------------------------------------------------------------- ##
## Graph Section  ##
## ------------------------------------------------------------------------------- ##

from data import get_subgraph_from_name

network_component = visdcc.Network(
    id="network_visualization",
    # data={"nodes": [], "edges": []},
    data=get_subgraph_from_name("Jon-Snow", 2),
    options=dict(
        physics={
            "enabled": True,
            # "solver": "barnesHut",
            "solver": "repulsion",
        },
        interaction={"hover": True},
    ),
)

graph_section = html.Div(
    children=[
        network_component,
    ],
    className="graph_section",
)


## ------------------------------------------------------------------------------- ##
## Dashboard Section  ##
## ------------------------------------------------------------------------------- ##

dashboard_section = html.Div(
    id="dashboard",
    children=[
        menu_section,
        graph_section,
    ],
    className="dashboard_section",
)

## ------------------------------------------------------------------------------- ##
## Layout  ##
## ------------------------------------------------------------------------------- ##

layout = html.Div(
    children=[
        header,
        dashboard_section,
    ],
)
