import os
from dash import Dash, Output, Input
import dash_bootstrap_components as dbc

from data import load_data
from style import THEME
from layouts import create_layout
from callbacks import register_callbacks

# Chargement des données UNE SEULE FOIS au démarrage
df = load_data()

def create_app():
    external_scripts = [
        "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js",
    ]

    app = Dash(
        __name__,
        requests_pathname_prefix="/copublications-dashboard/",
        routes_pathname_prefix="/copublications-dashboard/",
        external_stylesheets=[THEME],
        external_scripts=external_scripts,
        suppress_callback_exceptions=True,
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
    app.title = "Copublications Inria"
    app.layout = create_layout(df)
    register_callbacks(app, df)

    app.clientside_callback(
        """
        function(n) {
            if (!n) {
                document.body.classList.remove("dark-mode");
                return "🌙";
            }
            if (n % 2 === 1) {
                document.body.classList.add("dark-mode");
                return "☀️";
            } else {
                document.body.classList.remove("dark-mode");
                return "🌙";
            }
        }
        """,
        Output("toggle-dark", "children"),
        Input("toggle-dark", "n_clicks"),
    )

    return app


app = create_app()
server = app.server

if __name__ == "__main__":
    app.run(debug=False)