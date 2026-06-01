from dash import dcc, html
import dash_bootstrap_components as dbc


def main_tab_layout(df):
    """
    Mise en page de l'onglet 'Vue principale'

    - Ligne 1 : explication + évolution annuelle
    - Ligne 2 : Top 10 pays / Top 10 villes / Top 10 organismes
    """

    # ---- Fabrique de cartes graphiques classiques ----
    def card_graph(graph_id: str, title: str) -> dbc.Card:
        return dbc.Card(
            [
                dbc.CardHeader(
                    title,
                    className="fw-semibold small text-uppercase",
                    style={
                        "backgroundColor": "transparent",
                        "borderBottom": "none",
                        "padding": "0.5rem 0.75rem 0 0.75rem",
                    },
                ),
                dbc.CardBody(
                    dcc.Graph(
                        id=graph_id,
                        style={"height": "340px"},
                        config={
                            "displayModeBar": True,
                            "scrollZoom": True,
                            "displaylogo": False,
                            "modeBarButtonsToAdd": [
                                "zoomInMapbox",
                                "zoomOutMapbox",
                                "resetViewMapbox",
                            ],
                        },
                    ),
                    className="main-graph-card",
                    style={"padding": "0.25rem"},
                ),
            ],
            className="shadow-sm mb-3",
            style={"borderRadius": "18px", "height": "100%"},
        )

    # ---- Carte texte simple (explications) ----
    def card_text(title: str, children) -> dbc.Card:
        return dbc.Card(
            [
                dbc.CardHeader(
                    title,
                    className="fw-semibold small text-uppercase",
                    style={
                        "backgroundColor": "transparent",
                        "borderBottom": "none",
                        "padding": "0.5rem 0.75rem 0 0.75rem",
                    },
                ),
                dbc.CardBody(
                    children,
                    className="small",
                    style={"padding": "0.75rem"},
                ),
            ],
            className="shadow-sm mb-3",
            style={"borderRadius": "18px", "height": "100%"},
        )

    return dbc.Container(
        [
            # ---------- Ligne 1 : Explication + évolution annuelle ----------
            dbc.Row(
                [
                    dbc.Col(
                        card_text(
                            "À propos du graphique",
                            [
                                html.P(
                                    "Ce graphique montre l'évolution du nombre de "
                                    "copublications par année dans le périmètre "
                                    "défini par les filtres.",
                                    className="mb-2",
                                ),
                                html.P(
                                    "Utilisez ce visuel pour repérer les années "
                                    "fortes, les tendances de croissance ou de "
                                    "stagnation.",
                                    className="mb-0",
                                ),
                            ],
                        ),
                        md=4,
                        sm=12,
                    ),
                    dbc.Col(
                        card_graph(
                            "bar_annee",
                            "Nombre de publications par année",
                        ),
                        md=8,
                        sm=12,
                    ),
                ],
                className="mb-3",
            ),

            # ---------- Ligne 2 : Top 10 ----------
            dbc.Row(
                [
                    dbc.Col(
                        card_graph(
                            "top_pays",
                            "Top 10 des pays",
                        ),
                        md=4,
                        sm=12,
                    ),
                    dbc.Col(
                        card_graph(
                            "top_villes",
                            "Top 10 des villes",
                        ),
                        md=4,
                        sm=12,
                    ),
                    dbc.Col(
                        card_graph(
                            "top_orgs",
                            "Top 10 des organismes copubliants",
                        ),
                        md=4,
                        sm=12,
                    ),
                ],
                className="mb-3",
            ),
        ],
        fluid=True,
        className="mt-2",
    )