from dash import dcc, html
import visdcc
from data import get_options_for_dropdown

from data import get_edge_weight_range, get_node_screentime_range
edge_weight_min, edge_weight_max  = get_edge_weight_range()
node_screentime_min, node_screentime_max = get_node_screentime_range()

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

## ------------------------------------------------------------------------------- ##
graph_interaction_header = html.Div(
    id="graph_interaction_header",
    children="Graph Interaction",
    className="header menu_header",
)

graph_interaction_input = dcc.Dropdown(
    id="graph_interaction_input",
    options=[
        {"label": "Expand Node", "value": "expand_node"},
        {"label": "Delete Node", "value": "delete_node"},
        {"label": "Node Wiki", "value": "node_wiki"},
        {"label": "None", "value": "none"},
    ],
    multi=False,
    placeholder="Enter graph interaction here...",
    className="header field_description",
)

## ------------------------------------------------------------------------------- ##
menu_header = html.Div(
    id="menu_header",
    children="Search Menu",
    className="header menu_header",
)

# search_node_id
search_node_id_header = html.Div(
    id="search_node_id_header",
    children="Node ID",
    className="header field_description",
)

search_node_id_input = dcc.Dropdown(
    id="search_node_id_input",
    options=get_options_for_dropdown(),
    multi=False,
    placeholder="Enter node ID here...",
    className="header field_description",
)

# expand_num_hops_header
expand_num_hops_header = html.Div(
    id="expand_num_hops_header",
    children="Number of Hops",
    className="header field_description",
)

expand_num_hops_input = dcc.Dropdown(
    id="expand_num_hops_input",
    options=[0, 1, 2, 3, 4, 5],
    multi=False,
    placeholder="Enter number of hops here...",
    className="header field_description",
)

# filter_node_type
filter_node_type_header = html.Div(
    id="filter_node_type_header",
    children="Node Type",
    className="header field_description",
)

filter_node_type_input = dcc.Dropdown(
    id="filter_node_type_input",
    options=[
        {"label": "Male", "value": "male"},
        {"label": "Female", "value": "female"},
    ],
    multi=True,
    placeholder="Enter node types here...",
    className="header field_description",
)

# filter_node_screentime
filter_node_screentime_header = html.Div(
    id="filter_node_screentime_header",
    children="Minimum Node Screentime",
    className="header field_description",
)

filter_node_screentime_input = dcc.Slider(
        id="filter_node_screentime_input",
        min = node_screentime_min, 
        max = node_screentime_max, 
        value=node_screentime_min,
        className="header field_description",
    )

# filter_edge_weight
filter_edge_weight_header = html.Div(
    id="filter_edge_weight_header",
    children="Minimum Edge Weight",
    className="header field_description",
)

filter_edge_weight_input = dcc.Slider(
        id="filter_edge_weight_input",
        min = edge_weight_min, 
        max = edge_weight_max, 
        value=edge_weight_min,
        className="header field_description",
    )

# submit_button
submit_button = html.Button(
    id="submit_button",
    children="Submit",
    n_clicks=0,
    className="header field_description submit_button",
)

## ------------------------------------------------------------------------------- ##
# search_result
search_result_header = html.Div(
    id="search_result_header",
    children="Search Result",
    className="header menu_header",
)

search_result_output = html.Div(
    id="search_result_output",
    children="Search Result....",
    className="header field_description",
)


menu_section = html.Div(
    children=[
        graph_interaction_header, 
        graph_interaction_input, 
        html.Hr(className="horizontal-line"),
        menu_header,
        search_node_id_header,
        search_node_id_input,
        expand_num_hops_header, 
        expand_num_hops_input, 
        filter_node_type_header, 
        filter_node_type_input, 
        filter_node_screentime_header, 
        filter_node_screentime_input, 
        filter_edge_weight_header, 
        filter_edge_weight_input, 
        submit_button, 
        html.Hr(className="horizontal-line"),
        search_result_header, 
        search_result_output, 
    ],
    className="menu_section",
)


## ------------------------------------------------------------------------------- ##
## Graph Section  ##
## ------------------------------------------------------------------------------- ##

network_component = visdcc.Network(
    id="network_visualization",
    data={"nodes": [], "edges": []},
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
