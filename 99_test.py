import dash
from dash import html


# Create the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div(
    [
        html.Div(
            className="fredrik",
            children="Hello Header!",
        ),
        html.Div(
            className="kropp",
            children="Hello Body!",
        ),
    ]
)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
