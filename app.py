import dash
import layout
import callbacks
import dash_bootstrap_components as dbc


# Run the app
if __name__ == "__main__":
    app = dash.Dash(__name__)

    app.layout = layout.layout
    # callbacks.register_callbacks(app)
    # print(app.assets_url_path)
    app.run_server(debug=True, port=8050)
