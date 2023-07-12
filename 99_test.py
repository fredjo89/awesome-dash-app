import dash
import dash_html_components as html
import dash_table
import pandas as pd

# Sample DataFrame
df = pd.DataFrame(
    {
        "Name": ["John", "Alice", "Bob"],
        "Age": [25, 30, 35],
        "City": ["New York", "London", "Paris"],
    }
)

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=["styles.css"])

# Define the layout
app.layout = html.Div(
    [
        html.Div(
            className="my-datatable",
            children=[
                dash_table.DataTable(
                    data=df.to_dict("records"),
                    columns=None,
                    # columns=[{"name": i, "id": i} for i in df.columns],
                )
            ],
        )
    ]
)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
