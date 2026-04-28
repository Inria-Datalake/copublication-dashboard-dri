from dash import dcc, html
import dash_bootstrap_components as dbc
import numpy as np


# Couleur accent INRIA pour les labels
_LABEL_STYLE = {
    "color": "#27348b",
    "fontWeight": "700",
    "fontSize": "0.76rem",
    "letterSpacing": "0.04em",
    "textTransform": "uppercase",
    "marginBottom": "4px",
}

_DROPDOWN_STYLE = {
    "fontSize": "0.82rem",
    "borderRadius": "8px",
}


def _make_dropdown(id_, label, options):
    """Fabrique un dropdown stylé à partir d'une liste d'options."""
    opts = sorted({str(o) for o in options if str(o) != "nan"})

    return dbc.Col(
        [
            html.Label(label, className="mb-1", style=_LABEL_STYLE),
            dcc.Dropdown(
                id=id_,
                options=[{"label": o, "value": o} for o in opts],
                multi=True,
                placeholder=f"Tous…",
                className="dcc-dropdown",
                style=_DROPDOWN_STYLE,
            ),
        ],
        xs=12,
        sm=6,
        md=4,
        lg=2,
        className="mb-2",
    )


def filters_row(df):
    """
    Renvoie une ligne de filtres horizontaux avec les IDs :
      centre, equipe, pays, ville, org, annee
    """

    return html.Div(
        [
            dbc.Row(
                [
                    _make_dropdown("centre", "Centre",   df["Centre"].unique()),
                    _make_dropdown("equipe", "Équipe",   df["Equipe"].unique()),
                    _make_dropdown("pays",   "Pays",     df["Pays"].unique()),
                    _make_dropdown("ville",  "Ville",    df["Ville"].unique()),
                    _make_dropdown(
                        "org",
                        "Organisme",
                        df["Organisme_copubliant"].unique(),
                    ),
                    # Dropdown Année
                    dbc.Col(
                        [
                            html.Label("Année", className="mb-1", style=_LABEL_STYLE),
                            dcc.Dropdown(
                                id="annee",
                                options=[
                                    {"label": int(a), "value": int(a)}
                                    for a in sorted(
                                        df["Année"].dropna().unique().astype(int)
                                    )
                                ],
                                multi=True,
                                placeholder="Toutes…",
                                className="dcc-dropdown",
                                style=_DROPDOWN_STYLE,
                            ),
                        ],
                        xs=12,
                        sm=6,
                        md=4,
                        lg=2,
                        className="mb-2",
                    ),
                ],
                className="g-2 justify-content-center",
                style={"alignItems": "flex-end"},
            )
        ],
        style={"maxWidth": "100%"},
    )