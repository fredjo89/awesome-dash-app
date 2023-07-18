import dash
import layout
import callbacks

# external CSS stylesheets
external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/vis/4.20.1/vis.min.css",  # This stylesheet is needed to display node info on mouse hover
]

# Run the app
if __name__ == "__main__":
    app = dash.Dash(
        __name__,
        external_stylesheets=external_stylesheets,
    )

    app.layout = layout.layout
    callbacks.register_callbacks(app)
    app.run_server(debug=True, port=8050)
