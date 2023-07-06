import dash
import layout
import callbacks

# external CSS stylesheets
external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/vis/4.20.1/vis.min.css",
]

# Run the app
if __name__ == "__main__":
    app = dash.Dash(
        __name__,
        external_stylesheets=external_stylesheets,
    )

    app.layout = layout.layout
    callbacks.register_callbacks(app)
    # print(app.assets_url_path)
    app.run_server(debug=True, port=8050)
