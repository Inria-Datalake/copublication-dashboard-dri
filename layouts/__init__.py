from dash import html, dcc
import dash_bootstrap_components as dbc

from .filters_kpi import filters_row
from .main_charts import main_tab_layout
from .wordcloud_tab import wordcloud_tab_layout
from .network_tab import network_tab_layout
from .country_evolution_tab import country_evolution_tab_layout
from .share_tab import share_tab_layout
from style import PRIMARY, PRIMARY_LIGHT, BG

# ─── Couleurs ────────────────────────────────────────────────
BLUE   = "#317AC1"
NAVY   = "#1b2a4a"
OFF    = "#f7f9fc"
BORDER = "#e8ecf4"
MUTED  = "#8a96b0"
TEXT   = "#1e2b45"

PREFIX        = "/copublications-dashboard"
LOGO_INRIA    = f"{PREFIX}/assets/logo_inria.png"
LOGO_DATALAKE = f"{PREFIX}/assets/logo_datalake.png"
LOGO_DATA     = f"{PREFIX}/assets/logo_data.png"

# ─── Style icône dans le carré arrondi ───────────────────────
_ICON_BOX = {
    "width": "28px", "height": "28px",
    "background": "#eef2f8",
    "borderRadius": "8px",
    "display": "flex", "alignItems": "center",
    "justifyContent": "center",
    "flexShrink": "0",
}
_ICON_STYLE = {"fontSize": "13px", "color": BLUE}


# ─── Helpers sidebar ─────────────────────────────────────────

def _sb_divider():
    return html.Div(style={
        "height": "1px",
        "background": BORDER,
        "margin": "18px 0 14px",
    })


def _sb_label(title):
    return html.Div(title, style={
        "fontSize": "8px",
        "fontWeight": "700",
        "textTransform": "uppercase",
        "letterSpacing": "0.18em",
        "color": BLUE,
        "marginBottom": "10px",
    })


def _sb_meta_row(icon, label, value):
    """icon = composant html.I(className='bi bi-xxx') ou chaîne."""
    return html.Div(style={
        "display": "flex",
        "alignItems": "center",
        "gap": "10px",
        "marginBottom": "8px",
    }, children=[
        html.Div(icon, style=_ICON_BOX),
        html.Div([
            html.Div(label, style={
                "fontSize": "9px", "fontWeight": "600",
                "textTransform": "uppercase", "letterSpacing": "0.10em",
                "color": MUTED, "lineHeight": "1",
            }),
            html.Div(value, style={
                "fontSize": "11.5px", "fontWeight": "700",
                "color": TEXT, "marginTop": "2px",
            }),
        ]),
    ])


def _sb_credit_row(role, names):
    return html.Div(style={"marginBottom": "12px"}, children=[
        html.Div(role, style={
            "fontSize": "8px", "fontWeight": "700",
            "textTransform": "uppercase", "letterSpacing": "0.14em",
            "color": BLUE, "marginBottom": "3px",
        }),
        html.Div(names, style={
            "fontSize": "11.5px", "fontWeight": "500",
            "color": TEXT, "lineHeight": "1.55",
        }),
    ])


def _sb_btn(label, btn_id):
    """Bouton export — icône + texte, style PBI outline."""
    return html.Button(label, id=btn_id, style={
        "width": "100%",
        "padding": "9px 14px",
        "background": "white",
        "border": f"1.5px solid {BORDER}",
        "color": BLUE,
        "fontSize": "10px",
        "fontWeight": "700",
        "textTransform": "uppercase",
        "letterSpacing": "0.08em",
        "cursor": "pointer",
        "borderRadius": "8px",
        "textAlign": "left",
        "transition": "border-color 0.15s, background 0.15s",
        "marginBottom": "8px",
        "display": "flex",
        "alignItems": "center",
        "gap": "8px",
    })


def _sb_selection_chip():
    return html.Div(style={
        "display": "flex",
        "alignItems": "center",
        "gap": "8px",
        "padding": "8px 12px",
        "background": "#eef2f8",
        "borderRadius": "8px",
        "marginBottom": "6px",
    }, children=[
        html.I(className="bi bi-funnel", style={"fontSize": "13px", "color": BLUE}),
        html.Div([
            html.Div("Sélection active", style={
                "fontSize": "8px", "fontWeight": "700",
                "textTransform": "uppercase", "letterSpacing": "0.10em",
                "color": MUTED,
            }),
            html.Span(
                id="report-title",
                style={"fontSize": "11px", "fontWeight": "700", "color": TEXT},
            ),
        ]),
    ])


# ─── Layout principal ─────────────────────────────────────────

def create_layout(df):

    # ── Barre icône fixe gauche ───────────────────────────────
    icon_rail = html.Div(
        className="inria-sidebar",
        children=[
            dbc.Button(
                html.I(className="bi bi-list", style={"fontSize": "20px"}),
                id="sidebar-toggle",
                n_clicks=0,
                style={
                    "background": "transparent",
                    "border": "none",
                    "color": "rgba(255,255,255,0.85)",
                    "padding": "6px",
                    "cursor": "pointer",
                    "borderRadius": "8px",
                    "lineHeight": "1",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                },
            ),
        ],
    )

    # ── Top nav ───────────────────────────────────────────────
    topnav = html.Div(
        className="inria-topnav inria-anim",
        children=[
            html.Span("Tableau de bord", className="inria-topnav-brand"),
            html.Div(className="inria-topnav-sep"),
            html.Span("Groupe Datalake", className="inria-topnav-sub"),
            html.Div(className="inria-topnav-spacer"),
            dbc.Button(
                html.I(className="bi bi-moon", style={"fontSize": "13px"}),
                id="toggle-dark",
                n_clicks=0,
                size="sm",
                style={
                    "background": "transparent",
                    "border": f"1px solid {BORDER}",
                    "color": NAVY,
                    "padding": "4px 10px",
                    "borderRadius": "8px",
                    "cursor": "pointer",
                    "display": "flex",
                    "alignItems": "center",
                },
                title="Mode sombre",
            ),
        ],
    )

    # ── Hero ──────────────────────────────────────────────────
    hero = html.Div(
        className="inria-hero inria-anim inria-anim-2",
        children=[
            html.Div(className="inria-eyebrow"),
            html.H1("Copublications internationales"),
            html.P(
                "Analyse des copublications scientifiques des équipes Inria avec leurs partenaires "
                "internationaux. Données issues de HAL, enrichies avec des référentiels "
                "géographiques et institutionnels.",
                className="inria-hero-intro",
            ),
            html.Div([
                html.Span("HAL · Inria", style={
                    "fontSize": "9px", "fontWeight": "700", "padding": "4px 12px",
                    "background": BLUE, "color": "white", "borderRadius": "20px",
                    "textTransform": "uppercase", "letterSpacing": "0.08em",
                    "marginRight": "6px",
                }),
                html.Span("Copublications", style={
                    "fontSize": "9px", "fontWeight": "700", "padding": "4px 12px",
                    "background": NAVY, "color": "white", "borderRadius": "20px",
                    "textTransform": "uppercase", "letterSpacing": "0.08em",
                    "marginRight": "6px",
                }),
                html.Span("2017 – 2026", style={
                    "fontSize": "9px", "fontWeight": "700", "padding": "4px 12px",
                    "background": OFF, "color": NAVY,
                    "border": f"1.5px solid {BORDER}", "borderRadius": "20px",
                    "textTransform": "uppercase", "letterSpacing": "0.08em",
                }),
            ]),
        ],
    )

    # ── Filtres ───────────────────────────────────────────────
    filter_block = html.Div(
        className="inria-filter-block inria-anim inria-anim-2",
        children=[
            html.Div("Filtres", className="inria-filter-label"),
            filters_row(df),
        ],
    )

    # ── Carte + KPI ───────────────────────────────────────────
    map_kpi_row = dbc.Row(
        id="section-map-kpi",
        children=[
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Carte mondiale des copublications"),
                    dbc.CardBody(
                        dcc.Graph(
                            id="map",
                            style={"height": "400px", "minHeight": "400px"},
                            config={
                                "responsive": True,
                                "displaylogo": False,
                                "displayModeBar": True,
                                "scrollZoom": True,
                                "modeBarButtonsToAdd": [
                                    "zoomInMapbox", "zoomOutMapbox", "resetViewMapbox",
                                ],
                            },
                        ),
                        style={"padding": "0"},
                    ),
                ]),
                md=8, sm=12,
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Indicateurs clés"),
                    dbc.CardBody(html.Div(id="kpi-zone")),
                ]),
                md=4, sm=12,
            ),
        ],
        className="mb-3 mt-3 px-3",
    )

    # ── Onglet évolution ──────────────────────────────────────
    evolution_tab_content = html.Div(
        id="evolution-tab-container",
        children=[
            dbc.Card([
                dbc.CardHeader("À propos de cette page"),
                dbc.CardBody([
                    html.P("Les graphiques de cette page permettent l'analyse des copublications internationales.", className="mb-2"),
                    html.P("Ces visualisations sont plus lisibles avec un filtre resserré (un centre, une équipe…).", className="mb-2", style={"fontWeight": "600"}),
                    html.Hr(className="my-2"),
                    html.P("• Disque Centre–équipe–organisme : filtrez par pays, cliquez sur un centre pour voir les équipes.", className="mb-1"),
                    html.P("• Poids des domaines : proportion par domaine selon les filtres actifs.", className="mb-1"),
                    html.P("• Évolution des copublications : nombre par équipe au fil du temps.", className="mb-1"),
                    html.P("• Flux croisés : centre → pays → organisme.", className="mb-0"),
                ], className="small"),
            ], className="mb-3 mx-3 mt-3"),
            dbc.Row([
                dbc.Col(dcc.Graph(id="sunburst_collab", config={"responsive": True, "displaylogo": False}, style={"height": "55vh", "minHeight": "340px"}), md=6),
                dbc.Col(dcc.Graph(id="radar_centre",    config={"responsive": True, "displaylogo": False}, style={"height": "55vh", "minHeight": "340px"}), md=6),
            ], className="mb-3 px-3"),
            dbc.Row([
                dbc.Col(dcc.Graph(id="team_timeline", config={"responsive": True, "displaylogo": False}, style={"height": "55vh", "minHeight": "340px"}), md=7),
                dbc.Col(dcc.Graph(id="sankey_collab", config={"responsive": True, "displaylogo": False}, style={"height": "55vh", "minHeight": "340px"}), md=5),
            ], className="mb-3 px-3"),
            dbc.Row([dbc.Col(html.Div(id="story_evol", className="p-3"), md=12)], className="px-3"),
        ],
    )

    # ── Modal flow map ────────────────────────────────────────
    flowmap_modal = html.Div(
        id="flowmap-fullscreen-modal",
        style={
            "display": "none", "position": "fixed", "inset": "0",
            "background": "rgba(0,0,0,0.60)", "zIndex": "9999", "padding": "20px",
        },
        children=[
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.H5("Flux de copublications — Plein écran", className="fw-bold mb-0", style={"color": PRIMARY}),
                        dbc.Button("✕ Fermer", id="btn-flowmap-fullscreen-close", color="light", size="sm"),
                    ], className="d-flex justify-content-between align-items-center mb-2"),
                    dcc.Graph(
                        id="flow_map_fullscreen",
                        config={"scrollZoom": True, "displayModeBar": True},
                        style={"height": "calc(100vh - 120px)", "borderRadius": "10px"},
                    ),
                ]),
                style={"height": "100%", "borderRadius": "14px", "overflow": "hidden"},
            ),
        ],
    )

    # ── Onglets ───────────────────────────────────────────────
    tabs = dcc.Tabs(
        id="tabs",
        value="tab-main",
        className="custom-tabs",
        children=[
            dcc.Tab(label="Vue principale",           value="tab-main",              className="custom-tab", selected_className="custom-tab--selected", children=[html.Div(id="main-tab-container",      children=main_tab_layout(df))]),
            dcc.Tab(label="Mots-clés",                value="tab-wordcloud",         className="custom-tab", selected_className="custom-tab--selected", children=[html.Div(id="wordcloud-tab-container",  children=wordcloud_tab_layout())]),
            dcc.Tab(label="Réseau",                   value="tab-network",           className="custom-tab", selected_className="custom-tab--selected", children=[network_tab_layout()]),
            dcc.Tab(label="Évolution par pays",       value="tab-country-evolution", className="custom-tab", selected_className="custom-tab--selected", children=[country_evolution_tab_layout()]),
            dcc.Tab(label="Parts relatives",          value="tab-share",             className="custom-tab", selected_className="custom-tab--selected", children=[share_tab_layout()]),
            dcc.Tab(label="Évolution copublications", value="tab-evolution",         className="custom-tab", selected_className="custom-tab--selected", children=[evolution_tab_content]),
            dcc.Tab(
                label="Flux par centre", value="tab-flowmap",
                className="custom-tab", selected_className="custom-tab--selected",
                children=[
                    dbc.Card(dbc.CardBody([
                        html.Div([
                            html.H5("Flux de copublications par centre", className="fw-bold mb-0", style={"color": PRIMARY}),
                            html.Span("Arcs reliant chaque centre Inria à ses partenaires internationaux", className="text-muted small"),
                        ], className="mb-3"),
                        html.Div(
                            dbc.Button(
                                [html.I(className="bi bi-fullscreen", style={"marginRight": "6px"}), "Plein écran"],
                                id="btn-flowmap-fullscreen-open", color="light", size="sm", className="mb-2",
                            ),
                            className="d-flex justify-content-end",
                        ),
                        dcc.Graph(id="flow_map", config={"scrollZoom": True, "displayModeBar": True}, style={"height": "580px", "borderRadius": "10px"}),
                        html.Div(id="flowmap-legend-block"),
                    ]), className="shadow-sm mt-3", style={"borderRadius": "14px"}),
                ],
            ),
        ],
    )

    # ── Footer ────────────────────────────────────────────────
    footer = html.Footer(
        className="app-footer",
        children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "16px"}, children=[
                html.Img(src=LOGO_INRIA,    style={"height": "20px", "opacity": "0.70"}),
                html.Div(style={"width": "1px", "height": "16px", "background": BORDER}),
                html.Img(src=LOGO_DATALAKE, style={"height": "20px", "opacity": "0.70"}),
                html.Span("Rapport copublications – Inria · Groupe Datalake", style={"fontSize": "10px", "color": MUTED}),
            ]),
            html.Div(style={"display": "flex", "gap": "6px"}, children=[
                html.Span("HAL",   style={"fontSize": "9px", "fontWeight": "700", "padding": "3px 10px", "color": BLUE, "background": "#eef2f8", "borderRadius": "20px", "textTransform": "uppercase", "letterSpacing": "0.06em"}),
                html.Span("Inria", style={"fontSize": "9px", "fontWeight": "700", "padding": "3px 10px", "color": NAVY, "background": OFF, "border": f"1px solid {BORDER}", "borderRadius": "20px", "textTransform": "uppercase", "letterSpacing": "0.06em"}),
            ]),
        ],
    )

    # ── Sidebar off-canvas — style Power BI ──────────────────
    sidebar = html.Div(
        id="sidebar",
        style={"display": "none"},
        children=[
            # Backdrop
            html.Div(id="sidebar-backdrop", style={
                "position": "fixed", "inset": "0",
                "background": "rgba(14,26,48,0.35)",
                "zIndex": "1299",
                "backdropFilter": "blur(2px)",
            }),

            # Panneau blanc
            html.Div(style={
                "position": "fixed",
                "top": "0", "left": "52px", "bottom": "0",
                "width": "310px",
                "background": "white",
                "zIndex": "1300",
                "overflowY": "auto",
                "display": "flex",
                "flexDirection": "column",
                "boxShadow": "8px 0 40px rgba(14,26,48,0.14)",
                "borderRight": f"1px solid {BORDER}",
            }, children=[

                # En-tête
                html.Div(style={
                    "padding": "20px 20px 16px",
                    "borderBottom": f"1px solid {BORDER}",
                    "background": OFF,
                }, children=[
                    html.Div(style={
                        "display": "flex", "alignItems": "center",
                        "justifyContent": "space-between", "marginBottom": "14px",
                    }, children=[
                        html.Div(style={"display": "flex", "alignItems": "center", "gap": "12px"}, children=[
                            html.Img(src=LOGO_INRIA, style={
                                "height": "22px", "maxWidth": "100px",
                                "objectFit": "contain", "opacity": "1",
                            }),
                            html.Div(style={"width": "1px", "height": "20px", "background": BORDER}),
                            html.Img(src=LOGO_DATALAKE, style={
                                "height": "20px", "maxWidth": "100px",
                                "objectFit": "contain", "opacity": "1",
                            }),
                        ]),
                        html.Button(
                            html.I(className="bi bi-x-lg", style={"fontSize": "12px"}),
                            id="sidebar-close", n_clicks=0, style={
                                "background": "transparent",
                                "border": f"1px solid {BORDER}",
                                "color": MUTED,
                                "width": "28px", "height": "28px",
                                "cursor": "pointer",
                                "borderRadius": "8px",
                                "display": "flex", "alignItems": "center",
                                "justifyContent": "center", "padding": "0",
                                "flexShrink": "0",
                            },
                        ),
                    ]),

                    # Titre avec trait bleu
                    html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px"}, children=[
                        html.Div(style={
                            "width": "3px", "height": "32px",
                            "background": BLUE, "borderRadius": "2px", "flexShrink": "0",
                        }),
                        html.Div([
                            html.Div("Copublications Inria", style={
                                "fontSize": "14px", "fontWeight": "800",
                                "color": TEXT, "letterSpacing": "-0.01em", "lineHeight": "1.2",
                            }),
                            html.Div("Groupe Datalake", style={
                                "fontSize": "10.5px", "fontWeight": "400",
                                "color": MUTED, "marginTop": "2px",
                            }),
                        ]),
                    ]),
                ]),

                # Corps
                html.Div(style={"padding": "18px 20px 28px", "flex": "1"}, children=[

                    _sb_selection_chip(),

                    _sb_divider(),
                    _sb_label("Périmètre"),
                    _sb_meta_row(html.I(className="bi bi-database",  style=_ICON_STYLE), "Source des données", "HAL · Inria"),
                    _sb_meta_row(html.I(className="bi bi-calendar3", style=_ICON_STYLE), "Période couverte",   "2017 – 2026"),
                    _sb_meta_row(html.I(className="bi bi-globe2",    style=_ICON_STYLE), "Portée",             "International"),

                    _sb_divider(),
                    _sb_label("À propos"),
                    html.P(
                        "Le groupe Datalake travaille à rendre possible le croisement de données "
                        "entre HAL et divers référentiels, et à développer des outils d'analyse "
                        "pour les acteurs scientifiques et décisionnaires. "
                        "Constitué de 6 membres : data scientists, développeurs et documentalistes experts.",
                        style={"fontSize": "11px", "color": MUTED, "lineHeight": "1.65", "marginBottom": "0"},
                    ),

                    _sb_divider(),
                    _sb_label("Équipe"),
                    _sb_credit_row("Données & Analyses", "Kumar Guha · Daniel Da Silva · Andréa Nebot"),
                    _sb_credit_row("Visualisations",     "Andréa Nebot"),
                    _sb_credit_row("Groupe",             "Datalake · Inria"),

                    _sb_divider(),
                    _sb_label("Exports"),
                    dcc.Download(id="download-csv"),
                    _sb_btn(
                        html.Span([
                            html.I(className="bi bi-download", style={"fontSize": "12px"}),
                            html.Span("Exporter CSV", style={"marginLeft": "8px"}),
                        ]),
                        "btn-export-csv",
                    ),
                    _sb_btn(
                        html.Span([
                            html.I(className="bi bi-file-earmark-pdf", style={"fontSize": "12px"}),
                            html.Span("Exporter PDF", style={"marginLeft": "8px"}),
                        ]),
                        "export-pdf",
                    ),
                ]),
            ]),
        ],
    )

    # ── Assemblage final ──────────────────────────────────────
    return html.Div(
        id="page-wrapper",
        children=[
            dcc.Store(id="store-data"),
            icon_rail,
            html.Div(className="inria-main", children=[
                topnav,
                html.Div(className="inria-content-full", children=[
                    hero,
                    filter_block,
                    map_kpi_row,
                    html.Div(style={"height": "1px", "background": BORDER}),
                    tabs,
                    footer,
                ]),
            ]),
            sidebar,
            flowmap_modal,
        ],
    )
    
    return main_content