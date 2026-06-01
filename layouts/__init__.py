from dash import html, dcc
import dash_bootstrap_components as dbc

from .filters_kpi import filters_row
from .main_charts import main_tab_layout
from .wordcloud_tab import wordcloud_tab_layout
from .network_tab import network_tab_layout
from .country_evolution_tab import country_evolution_tab_layout
from .share_tab import share_tab_layout
from style import PRIMARY, PRIMARY_LIGHT, BG

# ─── Couleurs INRIA ───────────────────────────────────────────
RED    = "#e63312"
NAVY   = "#1b2a4a"
OFF    = "#f8f8f6"
BORDER = "#e4e4e0"
MUTED  = "#888880"

LOGO_INRIA    = "https://raw.githubusercontent.com/Inria-Datalake/copublications-dashboard/refs/heads/main/assets/logo_inria.png"
LOGO_DATALAKE = "https://raw.githubusercontent.com/Inria-Datalake/copublications-dashboard/refs/heads/main/assets/logo_datalake.png"
LOGO_DATA     = "https://raw.githubusercontent.com/Inria-Datalake/copublications-dashboard/refs/heads/main/assets/logo_data.png"


def _sb_section(title):
    return html.Div(
        title,
        style={
            "fontSize": "8px",
            "fontWeight": "700",
            "textTransform": "uppercase",
            "letterSpacing": "0.14em",
            "color": "rgba(255,255,255,0.55)",
            "borderTop": "1px solid rgba(255,255,255,0.18)",
            "paddingTop": "14px",
            "marginTop": "6px",
            "marginBottom": "8px",
        },
    )


def _sb_meta(dot_color, label, value):
    return html.Div(
        style={"display": "flex", "alignItems": "flex-start", "gap": "8px",
               "fontSize": "11px", "color": "rgba(255,255,255,0.75)",
               "marginBottom": "6px", "lineHeight": "1.5"},
        children=[
            html.Span(style={
                "width": "5px", "height": "5px", "borderRadius": "50%",
                "background": dot_color, "flexShrink": "0", "marginTop": "5px",
            }),
            html.Span([
                label,
                html.Span(value, style={"fontWeight": "700", "color": "white"}),
            ]),
        ],
    )


def _sb_credit(role, names):
    return html.Div(
        style={"marginBottom": "10px"},
        children=[
            html.Div(role, style={
                "fontSize": "7.5px", "fontWeight": "700",
                "textTransform": "uppercase", "letterSpacing": "0.14em",
                "color": RED, "marginBottom": "2px",
            }),
            html.Div(names, style={
                "fontSize": "11px", "fontWeight": "600",
                "color": "white", "lineHeight": "1.5",
            }),
        ],
    )


def _sb_btn(label, btn_id, extra_style=None):
    base = {
        "width": "100%",
        "padding": "7px 14px",
        "background": "rgba(255,255,255,0.10)",
        "border": "1.5px solid rgba(255,255,255,0.28)",
        "color": "white",
        "fontSize": "10px",
        "fontWeight": "700",
        "textTransform": "uppercase",
        "letterSpacing": "0.08em",
        "cursor": "pointer",
        "borderRadius": "0",
        "textAlign": "left",
        "transition": "background 0.15s",
        "marginBottom": "6px",
    }
    if extra_style:
        base.update(extra_style)
    return html.Button(label, id=btn_id, style=base)


def create_layout(df):

    # ── Barre latérale rouge fixe (44 px) ─────────────────────
    red_sidebar = html.Div(
        className="inria-sidebar",
        children=[
            dbc.Button(
                "☰",
                id="sidebar-toggle",
                n_clicks=0,
                style={
                    "background": "transparent",
                    "border": "none",
                    "color": "white",
                    "fontSize": "20px",
                    "padding": "0",
                    "cursor": "pointer",
                },
            ),
        ],
    )

    # ── Top nav ────────────────────────────────────────────────
    topnav = html.Div(
        className="inria-topnav inria-anim",
        children=[
            html.Span("Tableau de bord ", className="inria-topnav-brand"),
            html.Div(className="inria-topnav-sep"),
            html.Span("Groupe Datalake", className="inria-topnav-sub"),
            html.Div(className="inria-topnav-spacer"),
            dbc.Button(
                "🌙",
                id="toggle-dark",
                n_clicks=0,
                size="sm",
                style={
                    "background": "transparent",
                    "border": f"1px solid {BORDER}",
                    "color": NAVY,
                    "fontSize": "14px",
                    "padding": "2px 8px",
                    "borderRadius": "0",
                    "cursor": "pointer",
                },
                title="Mode sombre",
            ),
        ],
    )

    # ── Hero ───────────────────────────────────────────────────
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
                    "fontSize": "9px", "fontWeight": "700", "padding": "3px 10px",
                    "background": RED, "color": "white",
                    "textTransform": "uppercase", "letterSpacing": "0.08em",
                    "marginRight": "5px",
                }),
                html.Span("Copublications", style={
                    "fontSize": "9px", "fontWeight": "700", "padding": "3px 10px",
                    "background": NAVY, "color": "white",
                    "textTransform": "uppercase", "letterSpacing": "0.08em",
                    "marginRight": "5px",
                }),
                html.Span("2017 – 2026", style={
                    "fontSize": "9px", "fontWeight": "700", "padding": "3px 10px",
                    "background": OFF, "color": NAVY,
                    "border": f"1.5px solid {BORDER}",
                    "textTransform": "uppercase", "letterSpacing": "0.08em",
                }),
            ]),
        ],
    )

    # ── Bloc filtres ───────────────────────────────────────────
    filter_block = html.Div(
        className="inria-filter-block inria-anim inria-anim-2",
        children=[
            html.Div("Filtres", className="inria-filter-label"),
            filters_row(df),
        ],
    )

    # ── Carte mondiale + KPI ───────────────────────────────────
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

    # ── Onglet Évolution copublications ────────────────────────
    evolution_tab_content = html.Div(
        id="evolution-tab-container",
        children=[
            dbc.Card([
                dbc.CardHeader("À propos de cette page"),
                dbc.CardBody([
                    html.P(
                        "Les graphiques de cette page permettent l'analyse des copublications internationales.",
                        className="mb-2",
                    ),
                    html.P(
                        "Ces visualisations sont plus lisibles avec un filtre resserré (un centre, une équipe…).",
                        className="mb-2",
                        style={"fontWeight": "600"},
                    ),
                    html.Hr(className="my-2"),
                    html.P("• Disque Centre–équipe–organisme : filtrez par pays, cliquez sur un centre pour voir les équipes.", className="mb-1"),
                    html.P("• Poids des domaines : proportion par domaine selon les filtres actifs.", className="mb-1"),
                    html.P("• Évolution des copublications : nombre par équipe au fil du temps.", className="mb-1"),
                    html.P("• Flux croisés : centre → pays → organisme.", className="mb-0"),
                ], className="small"),
            ], className="mb-3 mx-3 mt-3"),

            dbc.Row([
                dbc.Col(
                    dcc.Graph(
                        id="sunburst_collab",
                        config={"responsive": True, "displaylogo": False},
                        style={"height": "55vh", "minHeight": "340px"},
                    ),
                    md=6,
                ),
                dbc.Col(
                    dcc.Graph(
                        id="radar_centre",
                        config={"responsive": True, "displaylogo": False},
                        style={"height": "55vh", "minHeight": "340px"},
                    ),
                    md=6,
                ),
            ], className="mb-3 px-3"),

            dbc.Row([
                dbc.Col(
                    dcc.Graph(
                        id="team_timeline",
                        config={"responsive": True, "displaylogo": False},
                        style={"height": "55vh", "minHeight": "340px"},
                    ),
                    md=7,
                ),
                dbc.Col(
                    dcc.Graph(
                        id="sankey_collab",
                        config={"responsive": True, "displaylogo": False},
                        style={"height": "55vh", "minHeight": "340px"},
                    ),
                    md=5,
                ),
            ], className="mb-3 px-3"),

            dbc.Row([
                dbc.Col(
                    html.Div(id="story_evol", className="p-3"),
                    md=12,
                ),
            ], className="px-3"),
        ],
    )

    # ── Modal plein écran flow map ─────────────────────────────
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
                        html.H5(
                            "Flux de copublications — Plein écran",
                            className="fw-bold mb-0",
                            style={"color": PRIMARY},
                        ),
                        dbc.Button(
                            "✕ Fermer",
                            id="btn-flowmap-fullscreen-close",
                            color="light",
                            size="sm",
                        ),
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

    # ── Onglets ────────────────────────────────────────────────
    tabs = dcc.Tabs(
        id="tabs",
        value="tab-main",
        className="custom-tabs",
        children=[
            dcc.Tab(
                label="Vue principale",
                value="tab-main",
                className="custom-tab",
                selected_className="custom-tab--selected",
                children=[html.Div(id="main-tab-container", children=main_tab_layout(df))],
            ),
            dcc.Tab(
                label="Mots-clés",
                value="tab-wordcloud",
                className="custom-tab",
                selected_className="custom-tab--selected",
                children=[html.Div(id="wordcloud-tab-container", children=wordcloud_tab_layout())],
            ),
            dcc.Tab(
                label="Réseau",
                value="tab-network",
                className="custom-tab",
                selected_className="custom-tab--selected",
                children=[network_tab_layout()],
            ),
            dcc.Tab(
                label="Évolution par pays",
                value="tab-country-evolution",
                className="custom-tab",
                selected_className="custom-tab--selected",
                children=[country_evolution_tab_layout()],
            ),
            dcc.Tab(
                label="Parts relatives",
                value="tab-share",
                className="custom-tab",
                selected_className="custom-tab--selected",
                children=[share_tab_layout()],
            ),
            dcc.Tab(
                label="Évolution copublications",
                value="tab-evolution",
                className="custom-tab",
                selected_className="custom-tab--selected",
                children=[evolution_tab_content],
            ),
            dcc.Tab(
                label="🗺 Flux par centre",
                value="tab-flowmap",
                className="custom-tab",
                selected_className="custom-tab--selected",
                children=[
                    dbc.Card(
                        dbc.CardBody([
                            # ── En-tête ──────────────────────────────────
                            html.Div([
                                html.H5(
                                    "Flux de copublications par centre",
                                    className="fw-bold mb-0",
                                    style={"color": PRIMARY},
                                ),
                                html.Span(
                                    "Arcs reliant chaque centre Inria à ses partenaires internationaux",
                                    className="text-muted small",
                                ),
                            ], className="mb-3"),
                            # ── Bouton plein écran ────────────────────────
                            html.Div(
                                dbc.Button(
                                    "⛶ Plein écran",
                                    id="btn-flowmap-fullscreen-open",
                                    color="light",
                                    size="sm",
                                    className="mb-2",
                                ),
                                className="d-flex justify-content-end",
                            ),
                            # ── Carte ─────────────────────────────────────
                            dcc.Graph(
                                id="flow_map",
                                config={"scrollZoom": True, "displayModeBar": True},
                                style={"height": "580px", "borderRadius": "10px"},
                            ),
                            # ── Bloc légende/aide ─────────────────────────
                            html.Div(id="flowmap-legend-block"),
                        ]),
                        className="shadow-sm mt-3",
                        style={"borderRadius": "14px"},
                    ),
                ],
            ),
        ],
    )

    # ── Footer ─────────────────────────────────────────────────
    footer = html.Footer(
        className="app-footer",
        children=[
            html.Div(
                style={"display": "flex", "alignItems": "center", "gap": "12px"},
                children=[
                    html.Img(src=LOGO_INRIA,    style={"height": "18px", "opacity": 0.55}),
                    html.Img(src=LOGO_DATALAKE, style={"height": "18px", "opacity": 0.55}),
                    html.Span(
                        "Rapport copublications – Inria · Groupe Datalake",
                        style={"fontSize": "9.5px", "color": MUTED},
                    ),
                ],
            ),
            html.Div(
                style={"display": "flex", "gap": "4px"},
                children=[
                    html.Span("HAL", style={
                        "fontSize": "8.5px", "fontWeight": "700", "padding": "2px 8px",
                        "color": NAVY, "background": OFF, "border": f"1px solid {BORDER}",
                        "textTransform": "uppercase", "letterSpacing": "0.06em",
                    }),
                    html.Span("Inria", style={
                        "fontSize": "8.5px", "fontWeight": "700", "padding": "2px 8px",
                        "color": NAVY, "background": OFF, "border": f"1px solid {BORDER}",
                        "textTransform": "uppercase", "letterSpacing": "0.06em",
                    }),
                ],
            ),
        ],
    )

    # ── Sidebar off-canvas ─────────────────────────────────────
    sidebar = html.Div(
        id="sidebar",
        style={"display": "none"},
        children=[
            html.Div(
                id="sidebar-backdrop",
                style={
                    "position": "fixed", "inset": "0",
                    "background": "rgba(0,0,0,0.40)",
                    "zIndex": "1299",
                },
            ),
            html.Div(
                style={
                    "position": "fixed",
                    "top": "0", "left": "44px",
                    "bottom": "0",
                    "width": "300px",
                    "background": f"linear-gradient(170deg, {NAVY} 0%, #27348b 55%, #1067a3 100%)",
                    "zIndex": "1300",
                    "overflowY": "auto",
                    "padding": "0",
                    "boxShadow": "4px 0 28px rgba(0,0,0,0.40)",
                    "display": "flex",
                    "flexDirection": "column",
                },
                children=[
                    html.Div(
                        style={
                            "display": "flex", "justifyContent": "flex-end",
                            "padding": "12px 14px 0",
                        },
                        children=[
                            html.Button(
                                "✕",
                                id="sidebar-close",
                                n_clicks=0,
                                style={
                                    "background": "rgba(255,255,255,0.12)",
                                    "border": "1px solid rgba(255,255,255,0.25)",
                                    "color": "white", "fontSize": "14px",
                                    "width": "30px", "height": "30px",
                                    "cursor": "pointer", "borderRadius": "0",
                                    "display": "flex", "alignItems": "center",
                                    "justifyContent": "center", "padding": "0",
                                    "flexShrink": "0",
                                },
                            ),
                        ],
                    ),
                    html.Div(
                        style={"padding": "16px 22px 28px", "flex": "1"},
                        children=[
                            html.Div(
                                style={
                                    "display": "flex", "alignItems": "center",
                                    "gap": "14px", "marginBottom": "18px",
                                    "paddingBottom": "16px",
                                    "borderBottom": "1px solid rgba(255,255,255,0.15)",
                                },
                                children=[
                                    html.Img(
                                        src=LOGO_INRIA,
                                        style={
                                            "height": "18px", "maxWidth": "120px",
                                            "objectFit": "contain",
                                            "filter": "brightness(0) invert(1)",
                                            "opacity": "0.55", "flexShrink": "0",
                                        },
                                    ),
                                    html.Div(style={
                                        "width": "1px", "height": "24px",
                                        "background": "rgba(255,255,255,0.28)",
                                        "flexShrink": "0",
                                    }),
                                    html.Img(
                                        src=LOGO_DATALAKE,
                                        style={
                                            "height": "18px", "maxWidth": "110px",
                                            "objectFit": "contain",
                                            "filter": "brightness(0) invert(1)",
                                            "opacity": "0.55", "flexShrink": "0",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "borderLeft": f"3px solid {RED}",
                                    "paddingLeft": "12px",
                                    "marginBottom": "20px",
                                },
                                children=[
                                    html.Div("COPUBLICATIONS  INRIA", style={
                                        "fontSize": "14px", "fontWeight": "700",
                                        "fontFamily": "'Source Serif 4', Georgia, serif",
                                        "color": "white", "letterSpacing": "0.02em",
                                        "lineHeight": "1.2", "marginBottom": "4px",
                                    }),
                                    html.Div("Groupe Datalake", style={
                                        "fontSize": "10.5px",
                                        "color": "rgba(255,255,255,0.58)",
                                    }),
                                ],
                            ),
                            _sb_section("Périmètre"),
                            _sb_meta(RED, "Données\u00a0: ", "HAL · Inria"),
                            _sb_meta(RED, "Période\u00a0: ", "2017 – 2026"),
                            html.Div(
                                style={
                                    "display": "flex", "alignItems": "flex-start",
                                    "gap": "8px", "fontSize": "11px",
                                    "color": "rgba(255,255,255,0.72)",
                                    "marginBottom": "6px", "lineHeight": "1.55",
                                },
                                children=[
                                    html.Span(style={
                                        "width": "5px", "height": "5px",
                                        "borderRadius": "50%", "background": RED,
                                        "flexShrink": "0", "marginTop": "5px",
                                    }),
                                    html.Span([
                                        "Sélection\u00a0: ",
                                        html.Span(
                                            id="report-title",
                                            style={
                                                "fontWeight": "700",
                                                "color": "white",
                                                "fontSize": "10.5px",
                                            },
                                        ),
                                    ]),
                                ],
                            ),
                            _sb_section("À propos"),
                            html.P(
                                "Le groupe Datalake, créé en 2022 au sein de la Direction de la culture et de l'information scientifique d'Inria,"
                                "travaille à rendre possible le croisement de données entre HAL et divers référentiels, "
                                "et de développer des outils d'analyse "
                                "pour les acteurs scientifiques et décisionnaires."
                                "Il est constitué de 6 membres : data scientists, développeurs et documentalistes experts."
                                "Le présent outil a été développé à la demande et en collaboration"
                                "avec deux scientifiques membres du réseau Direction des relations internationales (DRI),"
                                "Luigi Liquori (Sophia) et Maria Kazolea (Bordeaux)."
                                "Il a ensuite été amélioré à la demande de la DRI.",
                                style={
                                    "fontSize": "10.5px",
                                    "color": "rgba(255,255,255,0.72)",
                                    "lineHeight": "1.65", "marginBottom": "0",
                                },
                            ),
                            _sb_section("Équipe"),
                            _sb_credit("Données & Analyses",
                                       "Kumar Guha · Daniel Da Silva · Andréa Nebot"),
                            _sb_credit("Visualisations", "Andréa Nebot"),
                            _sb_credit("Groupe", "Datalake · Inria"),
                            _sb_section("Exports"),
                            dcc.Download(id="download-csv"),
                            _sb_btn("↓ Exporter les données CSV", "btn-export-csv"),
                            _sb_btn("↓ Exporter en PDF", "export-pdf"),
                        ],
                    ),
                ],
            ),
        ],
    )

    # ── Assemblage final ───────────────────────────────────────
    main_content = html.Div(
        id="page-wrapper",
        children=[
            dcc.Store(id="store-data"),
            red_sidebar,
            html.Div(
                className="inria-main",
                children=[
                    topnav,
                    html.Div(
                        className="inria-content-full",
                        children=[
                            hero,
                            filter_block,
                            map_kpi_row,
                            html.Div(style={"height": "1px", "background": BORDER}),
                            tabs,
                            footer,
                        ],
                    ),
                ],
            ),
            sidebar,
            flowmap_modal,   # ← modal rendu au niveau racine de la page
        ],
    )

    return main_content