import base64
import io
import numpy as np
import pandas as pd
import dash
from dash import Output, Input, State, no_update, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import networkx as nx
from dash.exceptions import PreventUpdate
import json
import math

from data import filter_df
from style import (
    GRAPH_TEMPLATE,
    PRIMARY,
    PRIMARY_LIGHT,
    ACCENT,
    DARK,
    CYAN_SCALE,
    QUAL_PALETTE,
    CENTRE_COLOR_MAP,
    get_centre_color,
)

# ============================================================
#  Coordonnées des centres Inria
# ============================================================
CENTER_COORDS = {
    "Inria Univ. Cote Azur":                   (43.6160, 7.0678),
    "Inria Univ. Côte d'Azur":                 (43.6160, 7.0678),
    "Inria Univ. Côte Azur":                   (43.6160, 7.0678),
    "Inria Univ Cote Azur":                    (43.6160, 7.0678),
    "Sophia":                                  (43.6160, 7.0678),
    "Sophia Antipolis":                        (43.6160, 7.0678),
    "Inria Sophia":                            (43.6160, 7.0678),
    "Inria Sophia Antipolis":                  (43.6160, 7.0678),
    "Inria Sophia Antipolis - Méditerranée":   (43.6160, 7.0678),
    "Inria Sophia Antipolis Méditerranée":     (43.6160, 7.0678),
    "Inria Saclay":                            (48.7136, 2.2122),
    "Inria Saclay - Île-de-France":            (48.7136, 2.2122),
    "Inria Saclay Ile-de-France":              (48.7136, 2.2122),
    "Inria Saclay IPP":                        (48.7136, 2.2122),
    "Inria Saclay UPS":                        (48.7136, 2.2122),
    "Saclay":                                  (48.7136, 2.2122),
    "Inria Univ. Rennes":                      (48.1147, -1.6387),
    "Inria Univ Rennes":                       (48.1147, -1.6387),
    "Rennes":                                  (48.1147, -1.6387),
    "Inria Rennes":                            (48.1147, -1.6387),
    "Inria Rennes - Bretagne Atlantique":      (48.1147, -1.6387),
    "Inria Rennes Bretagne Atlantique":        (48.1147, -1.6387),
    "Inria Paris":                             (48.8474, 2.3842),
    "Inria de Paris":                          (48.8474, 2.3842),
    "Paris":                                   (48.8474, 2.3842),
    "CRI Paris":                               (48.8474, 2.3842),
    "Inria Paris Sorbonne":                    (48.8468, 2.3544),
    "Inria Paris - Sorbonne":                  (48.8468, 2.3544),
    "Inria Sorbonne":                          (48.8468, 2.3544),
    "Inria Univ. Grenoble":                    (45.2095, 5.8346),
    "Inria Univ Grenoble":                     (45.2095, 5.8346),
    "Grenoble":                                (45.2095, 5.8346),
    "Inria Grenoble":                          (45.2095, 5.8346),
    "Inria Grenoble - Rhône-Alpes":            (45.2095, 5.8346),
    "Inria Grenoble Rhône-Alpes":              (45.2095, 5.8346),
    "Inria Univ. Lorraine":                    (48.6656, 6.1550),
    "Inria Univ Lorraine":                     (48.6656, 6.1550),
    "Nancy":                                   (48.6656, 6.1550),
    "Inria Nancy":                             (48.6656, 6.1550),
    "Inria Nancy - Grand Est":                 (48.6656, 6.1550),
    "Inria Nancy Grand Est":                   (48.6656, 6.1550),
    "Grand Est":                               (48.6656, 6.1550),
    "Inria Lille":                             (50.6078, 3.1311),
    "Inria Lille - Nord Europe":               (50.6078, 3.1311),
    "Inria Lille Nord Europe":                 (50.6078, 3.1311),
    "Lille":                                   (50.6078, 3.1311),
    "Inria Univ. Bordeaux":                    (44.8084, -0.5954),
    "Inria Univ Bordeaux":                     (44.8084, -0.5954),
    "Bordeaux":                                (44.8084, -0.5954),
    "Inria Bordeaux":                          (44.8084, -0.5954),
    "Inria Bordeaux - Sud-Ouest":              (44.8084, -0.5954),
    "Inria Bordeaux Sud-Ouest":                (44.8084, -0.5954),
    "Inria Lyon":                              (45.7826, 4.8791),
    "Lyon":                                    (45.7826, 4.8791),
    "Inria siege":                             (48.8243, 2.0996),
    "Inria siège":                             (48.8243, 2.0996),
    "Inria Siege":                             (48.8243, 2.0996),
    "Inria Siège":                             (48.8243, 2.0996),
    "Inria siege social":                      (48.8243, 2.0996),
    "Montpellier":                             (43.6324, 3.8618),
    "Inria Montpellier":                       (43.6324, 3.8618),
}


# ============================================================
#  Fonctions utilitaires arcs courbés + glow
# ============================================================
def curved_arc(lat1, lon1, lat2, lon2, curvature=0.20, steps=22):
    lat_c = (lat1 + lat2) / 2 + (lat2 - lat1) * curvature
    lon_c = (lon1 + lon2) / 2 - (lon2 - lon1) * curvature
    t = np.linspace(0, 1, steps)
    lat_curve = (1 - t) ** 2 * lat1 + 2 * (1 - t) * t * lat_c + t**2 * lat2
    lon_curve = (1 - t) ** 2 * lon1 + 2 * (1 - t) * t * lon_c + t**2 * lon2
    return lat_curve, lon_curve


def add_glow_arc(fig, lat_curve, lon_curve, rgb="39,52,139"):
    for width, color in [(10, f"rgba({rgb},0.04)"), (8, f"rgba({rgb},0.07)"), (6, f"rgba({rgb},0.10)")]:
        fig.add_trace(go.Scattermapbox(
            lat=lat_curve, lon=lon_curve, mode="lines",
            line=dict(width=width, color=color),
            hoverinfo="skip", showlegend=False,
        ))


# ============================================================
#  REGISTER CALLBACKS
# ============================================================
def register_callbacks(app, df_base):

    # ========================================================
    # 0a — Titre dynamique du rapport
    # ========================================================
    @app.callback(
        Output("report-title", "children"),
        [
            Input("centre", "value"),
            Input("equipe", "value"),
            Input("pays",   "value"),
            Input("ville",  "value"),
            Input("org",    "value"),
            Input("annee",  "value"),
        ],
    )
    def update_report_title(centres, equipes, pays, villes, orgs, annees):
        txt_centre = ("centre Inria " + centres[0]) if centres and len(centres) == 1 else \
                     ("centres Inria " + ", ".join(centres)) if centres else "tous les centres Inria"
        txt_eq     = ("équipe " + equipes[0]) if equipes and len(equipes) == 1 else \
                     ("équipes " + ", ".join(equipes)) if equipes else "toutes les équipes"
        txt_ville  = ("ville " + villes[0]) if villes and len(villes) == 1 else \
                     ("villes " + ", ".join(villes)) if villes else "toutes les villes"
        txt_pays   = ("pays " + pays[0]) if pays and len(pays) == 1 else \
                     ("pays " + ", ".join(pays)) if pays else "tous les pays"
        if annees:
            try:
                an_min, an_max = min(annees), max(annees)
                txt_periode = f"année {an_min}" if an_min == an_max else f"période {an_min}–{an_max}"
            except Exception:
                txt_periode = "période sélectionnée"
        else:
            txt_periode = "toutes les années"
        return (f"Copublications internationales – {txt_centre}, "
                f"{txt_eq}, {txt_ville}, {txt_pays} ({txt_periode})")

    # ========================================================
    # 0 — SIDEBAR
    # ========================================================
    @app.callback(
        Output("sidebar", "style"),
        [Input("sidebar-toggle", "n_clicks"), Input("sidebar-close", "n_clicks")],
        State("sidebar", "style"),
        prevent_initial_call=True,
    )
    def toggle_sidebar(open_clicks, close_clicks, current_style):
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_style or {"display": "none"}
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "sidebar-toggle":
            if current_style and current_style.get("display") == "block":
                return {"display": "none"}
            return {"display": "block"}
        return {"display": "none"}

    # ========================================================
    # 0bis — Export CSV
    # ========================================================
    @app.callback(
        Output("download-csv", "data"),
        Input("btn-export-csv", "n_clicks"),
        [
            State("centre", "value"), State("equipe", "value"),
            State("pays",   "value"), State("ville",  "value"),
            State("org",    "value"), State("annee",  "value"),
            State("store-data", "data"),
        ],
        prevent_initial_call=True,
    )
    def export_csv(n_clicks, centres, equipes, pays, villes, orgs, annees, stored_data):
        if not n_clicks:
            return no_update
        df  = pd.DataFrame(stored_data) if stored_data is not None else df_base
        dff = filter_df(df, centres, equipes, pays, villes, orgs, annees)
        return dcc.send_data_frame(dff.to_csv, "copublications_export.csv", index=False)

    # ========================================================
    # 0ter — FILTRES EN CASCADE
    # ========================================================
    def _as_list(x):
        if x is None: return []
        return x if isinstance(x, list) else [x]

    def _build_options(series):
        if series is None: return []
        vals = sorted([v for v in series.dropna().unique() if str(v).strip() != ""])
        return [{"label": str(v), "value": v} for v in vals]

    def _filter_except(df, centres, equipes, pays, villes, orgs, annees, except_key):
        dff = df.copy()
        if except_key != "centre"  and centres   and "Centre"               in dff.columns: dff = dff[dff["Centre"].isin(_as_list(centres))]
        if except_key != "equipe"  and equipes   and "Equipe"               in dff.columns: dff = dff[dff["Equipe"].isin(_as_list(equipes))]
        if except_key != "pays"    and pays      and "Pays"                 in dff.columns: dff = dff[dff["Pays"].isin(_as_list(pays))]
        if except_key != "ville"   and villes    and "Ville"                in dff.columns: dff = dff[dff["Ville"].isin(_as_list(villes))]
        if except_key != "org"     and orgs      and "Organisme_copubliant" in dff.columns: dff = dff[dff["Organisme_copubliant"].isin(_as_list(orgs))]
        if except_key != "annee"   and annees    and "Année"                in dff.columns: dff = dff[dff["Année"].isin(_as_list(annees))]
        return dff

    @app.callback(
        Output("centre", "options"), Output("equipe", "options"),
        Output("pays",   "options"), Output("ville",  "options"),
        Output("org",    "options"), Output("annee",  "options"),
        Input("centre", "value"),    Input("equipe", "value"),
        Input("pays",   "value"),    Input("ville",  "value"),
        Input("org",    "value"),    Input("annee",  "value"),
        Input("store-data", "data"),
    )
    def update_filter_dropdowns_soft(centres, equipes, pays, villes, orgs, annees, stored_data):
        df = pd.DataFrame(stored_data) if stored_data is not None else df_base
        dff_c = _filter_except(df, centres, equipes, pays, villes, orgs, annees, "centre")
        dff_e = _filter_except(df, centres, equipes, pays, villes, orgs, annees, "equipe")
        dff_p = _filter_except(df, centres, equipes, pays, villes, orgs, annees, "pays")
        dff_v = _filter_except(df, centres, equipes, pays, villes, orgs, annees, "ville")
        dff_o = _filter_except(df, centres, equipes, pays, villes, orgs, annees, "org")
        dff_a = _filter_except(df, centres, equipes, pays, villes, orgs, annees, "annee")
        return (
            _build_options(dff_c["Centre"])               if "Centre"               in dff_c.columns else [],
            _build_options(dff_e["Equipe"])               if "Equipe"               in dff_e.columns else [],
            _build_options(dff_p["Pays"])                 if "Pays"                 in dff_p.columns else [],
            _build_options(dff_v["Ville"])                if "Ville"                in dff_v.columns else [],
            _build_options(dff_o["Organisme_copubliant"]) if "Organisme_copubliant" in dff_o.columns else [],
            _build_options(dff_a["Année"])                if "Année"                in dff_a.columns else [],
        )

    # ========================================================
    # 1 — KPI + GRAPHIQUES PRINCIPAUX + CARTE + FLOW MAP
    # ========================================================
    @app.callback(
        [
            Output("kpi-zone",    "children"),
            Output("bar_annee",   "figure"),
            Output("top_pays",    "figure"),
            Output("top_villes",  "figure"),
            Output("top_orgs",    "figure"),
            Output("map",         "figure"),
            Output("flow_map",    "figure"),
        ],
        [
            Input("centre", "value"), Input("equipe", "value"),
            Input("pays",   "value"), Input("ville",  "value"),
            Input("org",    "value"), Input("annee",  "value"),
            Input("store-data", "data"),
        ],
    )
    def update_main(centres, equipes, pays, villes, orgs, annees, stored_data):
        df  = pd.DataFrame(stored_data) if stored_data is not None else df_base
        dff = filter_df(df, centres, equipes, pays, villes, orgs, annees)

        def kpi_card(label, value, color):
            return dbc.Col(dbc.Card(dbc.CardBody([
                html.Div(label, className="small text-muted"),
                html.H3(value, className="fw-bold mb-0", style={"color": color}),
            ]), className="shadow-sm",
                style={"borderRadius": "14px", "border": f"1px solid {color}20"}),
                md=4, sm=6, xs=12)

        def _fmt_n(n):
            return f"{int(n):,}".replace(",", "\u202f")

        kpi_global = dbc.Row([
            kpi_card("Publications",  _fmt_n(dff["HalID"].nunique()),               PRIMARY),
            kpi_card("Villes",        _fmt_n(dff["Ville"].nunique()),                PRIMARY_LIGHT),
            kpi_card("Pays",          _fmt_n(dff["Pays"].nunique()),                 ACCENT),
            kpi_card("Équipes",       _fmt_n(dff["Equipe"].nunique()),               PRIMARY_LIGHT),
            kpi_card("Auteurs Inria", _fmt_n(dff["Auteurs_FR"].nunique()),           PRIMARY),
            kpi_card("Copubliants",   _fmt_n(dff["Auteurs_copubliants"].nunique()),  PRIMARY_LIGHT),
        ], className="g-2")

        centre_counts = dff.groupby("Centre", observed=True)["HalID"].nunique().sort_values(ascending=False)
        centre_badges = [
            dbc.Badge(f"{c}\u00a0: {_fmt_n(n)}", pill=True, className="me-1 mb-1",
                      style={"backgroundColor": get_centre_color(c, i), "color": "white", "fontSize": "0.8rem"})
            for i, (c, n) in enumerate(centre_counts.items())
        ]
        kpis = html.Div([kpi_global, html.Hr(),
                         html.Div([html.Div("Publications par centre", className="fw-bold small text-muted mb-1"),
                                   html.Div(centre_badges, className="d-flex flex-wrap")])])

        pubs_by_year  = dff.groupby("Année", observed=True)["HalID"].nunique().reset_index(name="Publications")
        years_present = sorted(pubs_by_year["Année"].dropna().astype(int).unique().tolist())
        fig_year = px.bar(pubs_by_year, x="Année", y="Publications", color="Année",
                          color_discrete_sequence=QUAL_PALETTE)
        fig_year.update_layout(template=GRAPH_TEMPLATE, showlegend=False,
                               margin=dict(l=10, r=10, t=60, b=40),
                               xaxis=dict(type="category", tickmode="array",
                                          tickvals=years_present,
                                          ticktext=[str(y) for y in years_present],
                                          title="Année"))

        def top_bar_rounded(df_group, label, legend_below=False):
            if df_group.empty:
                return go.Figure().update_layout(template=GRAPH_TEMPLATE, showlegend=True,
                                                 margin=dict(l=10, r=10, t=10, b=10))
            df_top = df_group.sort_values("Publications", ascending=True).tail(10).reset_index(drop=True)
            colors = [QUAL_PALETTE[i % len(QUAL_PALETTE)] for i in range(len(df_top))]
            fig = go.Figure(go.Pie(labels=df_top[label], values=df_top["Publications"],
                                   hole=0.55, sort=False, direction="clockwise",
                                   marker=dict(colors=colors), textinfo="percent",
                                   hovertemplate=f"{label} : %{{label}}<br>Publications : %{{value}}<extra></extra>",
                                   showlegend=True))
            fig.update_layout(template=GRAPH_TEMPLATE, title=None, showlegend=True,
                              margin=dict(l=10, r=10, t=10, b=10))
            if legend_below:
                fig.update_layout(legend=dict(orientation="h", x=0.5, xanchor="center",
                                              y=-0.15, yanchor="top", font=dict(size=9)),
                                  margin=dict(l=10, r=10, t=10, b=90))
            else:
                fig.update_layout(legend=dict(orientation="v", y=0.5, yanchor="middle",
                                              x=1.02, xanchor="left"))
            return fig

        fig_pays   = top_bar_rounded(dff.groupby("Pays", observed=True)["HalID"].nunique().reset_index(name="Publications"), "Pays")
        fig_villes = top_bar_rounded(dff.groupby("Ville", observed=True)["HalID"].nunique().reset_index(name="Publications"), "Ville")
        fig_orgs   = top_bar_rounded(dff.groupby("Organisme_copubliant", observed=True)["HalID"].nunique().reset_index(name="Publications"), "Organisme_copubliant", legend_below=True)

        map_df = (dff.dropna(subset=["Latitude", "Longitude"])
                  .groupby(["Ville", "Pays", "Latitude", "Longitude"], observed=True)["HalID"]
                  .nunique().reset_index(name="Publications")
                  .sort_values("Publications", ascending=False).head(600))

        if map_df.empty:
            fig_map = go.Figure().update_layout(template=GRAPH_TEMPLATE,
                                                title="Carte mondiale des copublications (aucune donnée)",
                                                height=400, margin=dict(l=0, r=0, t=50, b=0))
        else:
            fig_map = px.scatter_mapbox(map_df, lat="Latitude", lon="Longitude",
                                        size="Publications", size_max=50, color="Pays",
                                        hover_name="Ville",
                                        hover_data={"Pays": True, "Publications": True},
                                        zoom=1, title="Carte mondiale des copublications")
            fig_map.update_layout(mapbox=dict(style="open-street-map",
                                              center=dict(lat=25, lon=5), zoom=1),
                                  height=400, margin=dict(l=0, r=0, t=50, b=0),
                                  autosize=False, uirevision="LOCK",
                                  legend=dict(orientation="v", x=1.02, xanchor="left", y=1,
                                              yanchor="top", font=dict(size=10),
                                              bgcolor="rgba(255,255,255,0.85)",
                                              bordercolor="rgba(0,0,0,0.1)", borderwidth=0.5))

        def hex_to_rgb(hex_color):
            h = hex_color.lstrip("#")
            if len(h) == 3: h = "".join([c * 2 for c in h])
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        def _lookup_centre_coords(centre_name, flow_df_fallback):
            if centre_name in CENTER_COORDS: return CENTER_COORDS[centre_name]
            c_low = centre_name.lower()
            for key, coords in CENTER_COORDS.items():
                if key.lower() in c_low or c_low in key.lower(): return coords
            return (float(flow_df_fallback["Latitude"].mean()), float(flow_df_fallback["Longitude"].mean()))

        centres_sel = [str(c) for c in centres if c is not None and str(c).strip() != ""] if centres else \
                      sorted(dff["Centre"].dropna().astype(str).unique().tolist())
        centres_sel = centres_sel[:8]

        fig_flow = go.Figure()
        origins, all_dest_lats, all_dest_lons = [], [], []

        if centres_sel:
            centre_color_map = {c: get_centre_color(c, i) for i, c in enumerate(centres_sel)}
            for centre_sel in centres_sel:
                flow_raw = dff[dff["Centre"].astype(str) == centre_sel].dropna(subset=["Latitude", "Longitude"])
                if flow_raw.empty: continue
                flow_df = (flow_raw.groupby(["Ville", "Pays", "Latitude", "Longitude"], observed=True)
                           .agg(Publications=("HalID", "nunique"),
                                UE_flag=("UE/Non_UE", lambda x: "UE" if (x == "UE").sum() >= (x != "UE").sum() else "Non_UE"))
                           .reset_index().sort_values("Publications", ascending=False).head(40))
                if flow_df.empty: continue
                origin_lat, origin_lon = _lookup_centre_coords(centre_sel, flow_df)
                origins.append((origin_lat, origin_lon))
                centre_hex = centre_color_map[centre_sel]
                r, g, b    = hex_to_rgb(centre_hex)
                centre_rgb = f"{r},{g},{b}"
                max_pub    = float(flow_df["Publications"].max()) or 1
                total_pubs = int(flow_df["Publications"].sum())
                p75 = float(flow_df["Publications"].quantile(0.75))
                p50 = float(flow_df["Publications"].quantile(0.50))
                for _, row in flow_df.iterrows():
                    pub    = float(row["Publications"])
                    is_ue  = row["UE_flag"] == "UE"
                    lw     = 5.5 if pub >= p75 else (3.0 if pub >= p50 else 1.5)
                    alpha  = 0.95 if pub >= p75 else (0.75 if pub >= p50 else 0.50)
                    dest_lat, dest_lon = float(row["Latitude"]), float(row["Longitude"])
                    all_dest_lats.append(dest_lat); all_dest_lons.append(dest_lon)
                    lat_c, lon_c = curved_arc(origin_lat, origin_lon, dest_lat, dest_lon)
                    tooltip = (f"<b>{centre_sel}</b> → <b>{row['Ville']}</b><br>"
                               f"Pays : {row['Pays']}<br>Publications : <b>{int(pub)}</b><br>"
                               f"Zone : {'🇪🇺 UE' if is_ue else '🌍 Hors UE'}")
                    fig_flow.add_trace(go.Scattermapbox(lat=list(lat_c)+[None], lon=list(lon_c)+[None],
                        mode="lines", line=dict(width=lw+6, color=f"rgba({centre_rgb},0.07)"),
                        hoverinfo="skip", showlegend=False))
                    fig_flow.add_trace(go.Scattermapbox(lat=list(lat_c)+[None], lon=list(lon_c)+[None],
                        mode="lines", line=dict(width=lw, color=f"rgba({centre_rgb},{alpha})"),
                        hoverinfo="text", text=[tooltip]*(len(lat_c)+1), showlegend=False))
                    tip_idx = int(len(lat_c) * 0.90)
                    fig_flow.add_trace(go.Scattermapbox(lat=[float(lat_c[tip_idx])], lon=[float(lon_c[tip_idx])],
                        mode="markers", marker=dict(size=6+4*(pub/max_pub), color=centre_hex, opacity=alpha+0.05),
                        hoverinfo="text", text=[tooltip], showlegend=False))
                for sz, op in [(52, 0.10), (34, 0.20)]:
                    fig_flow.add_trace(go.Scattermapbox(lat=[origin_lat], lon=[origin_lon], mode="markers",
                        marker=dict(size=sz, color=f"rgba({centre_rgb},{op})"), hoverinfo="skip", showlegend=False))
                fig_flow.add_trace(go.Scattermapbox(lat=[origin_lat], lon=[origin_lon], mode="markers+text",
                    marker=dict(size=20, color=centre_hex, opacity=1.0),
                    text=[centre_sel], textposition="bottom right",
                    textfont=dict(size=11, color="#111111"), name=centre_sel, showlegend=True,
                    hovertemplate=(f"<b>Centre Inria {centre_sel}</b><br>"
                                   f"Destinations : {len(flow_df)}<br>"
                                   f"Publications totales : {total_pubs}<br><extra></extra>")))

            if origins and all_dest_lats:
                all_lats = [o[0] for o in origins] + all_dest_lats
                all_lons = [o[1] for o in origins] + all_dest_lons
                lat_c2   = (min(all_lats) + max(all_lats)) / 2
                lon_c2   = (min(all_lons) + max(all_lons)) / 2
                span     = max(max(all_lats)-min(all_lats), max(all_lons)-min(all_lons))
                auto_zoom = 1 if span > 120 else (2 if span > 60 else (3 if span > 30 else 4))
            else:
                lat_c2, lon_c2, auto_zoom = 25, 5, 1

            fig_flow.update_layout(
                paper_bgcolor="white", plot_bgcolor="white", font=dict(color="#1e293b"),
                mapbox=dict(style="open-street-map", center=dict(lat=lat_c2, lon=lon_c2), zoom=auto_zoom),
                margin=dict(l=0, r=0, t=0, b=0),
                legend=dict(orientation="v", x=0.01, xanchor="left", y=0.99, yanchor="top",
                            bgcolor="rgba(255,255,255,0.88)", bordercolor="rgba(0,0,0,0.12)",
                            borderwidth=1, font=dict(size=11, color="#1e293b"),
                            title=dict(text="Centres Inria", font=dict(size=12, color="#27348b"))),
                hoverlabel=dict(bgcolor="#1e293b", font_size=12, font_color="#f1f5f9",
                                bordercolor="rgba(0,0,0,0.2)"),
                uirevision="flow_map_stable")

        return kpis, fig_year, fig_pays, fig_villes, fig_orgs, fig_map, fig_flow

    # ========================================================
    # 1bis — FLOW MAP plein écran
    # ========================================================
    @app.callback(
        Output("flowmap-fullscreen-modal", "style"),
        [Input("btn-flowmap-fullscreen-open", "n_clicks"), Input("btn-flowmap-fullscreen-close", "n_clicks")],
        State("flowmap-fullscreen-modal", "style"),
        prevent_initial_call=True,
    )
    def toggle_flowmap_fullscreen(open_clicks, close_clicks, current_style):
        ctx = dash.callback_context
        if not ctx.triggered: return current_style
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        return {"display": "block"} if trigger == "btn-flowmap-fullscreen-open" else {"display": "none"}

    @app.callback(
        Output("flow_map_fullscreen", "figure"),
        Input("flow_map", "figure"),
        prevent_initial_call=True,
    )
    def sync_flowmap_fullscreen(fig):
        return fig if fig is not None else no_update

    # ========================================================
    # 2 — WORDCLOUD
    # ========================================================
    @app.callback(
        [Output("wordcloud", "src"), Output("wordcloud-top-table", "children")],
        [Input("centre", "value"), Input("equipe", "value"), Input("pays", "value"),
         Input("ville",  "value"), Input("org",    "value"), Input("annee", "value"),
         Input("tabs", "value"),   Input("store-data", "data")],
    )
    def update_wordcloud(centres, equipes, pays, villes, orgs, annees, tab, stored_data):
        if tab != "tab-wordcloud":
            return no_update, no_update

        df  = pd.DataFrame(stored_data) if stored_data is not None else df_base
        dff = filter_df(df, centres, equipes, pays, villes, orgs, annees)

        VALEURS_EXCLUES = {"nan", "none", "n/a", "na", "", "null"}
        STOPWORDS_FR = {
            "le","la","les","de","du","des","un","une","et","en","à","au","aux","que","qui",
            "quoi","dont","où","par","pour","sur","sous","dans","avec","sans","est","sont",
            "été","être","avoir","nous","vous","ils","elles","on","ce","se","sa","son","ses",
            "mon","ma","mes","ton","ta","tes","lui","leur","leurs","tout","tous","toute","toutes",
            "plus","très","bien","ainsi","donc","comme","mais","ou","ni","car","si","puis","cet",
            "cette","ces","l","d","j","s","m","n","y","qu","c","a","il","je","tu","nous","lors",
            "selon","entre","après","avant","aussi","même","autres","autre","peut","fait","font",
            "faire","the","of","and","in","to","is","for","this","that","are","with","as","an",
            "on","by","from","be","or","not","at","it","its","we","our","they","which","have",
            "has","been","can","more","also","than","these","two","new","one","into","both",
            "their","such","show","used","using","based","paper","propose","presents","presented",
            "proposed","approach","different","within","between","while","however","here","first",
            "second","three","four","five","via","i.e","e.g","al","et",
        }

        mots_series = dff["Resume"].dropna().astype(str).str.strip()
        mots_series = mots_series[~mots_series.str.lower().isin(VALEURS_EXCLUES)]
        empty_table = html.P("Aucun résumé disponible.", className="text-muted small p-2")
        if mots_series.empty:
            return "", empty_table

        import re
        sample     = mots_series.sample(min(len(mots_series), 3000), random_state=42)
        mots_liste = []
        for resume in sample:
            for mot in re.split(r"[\s\W]+", resume):
                mot = mot.strip().lower()
                if len(mot) >= 3 and mot not in STOPWORDS_FR and mot not in VALEURS_EXCLUES and not mot.isdigit():
                    mots_liste.append(mot)

        if not mots_liste:
            return "", empty_table

        text = " ".join(mots_liste)
        wc   = WordCloud(width=900, height=400, background_color="white", colormap="tab10").generate(text)
        buf  = io.BytesIO()
        wc.to_image().save(buf, format="PNG")
        img_src = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

        counts = pd.Series([m.lower() for m in mots_liste]).value_counts()
        total  = counts.sum()
        top20  = counts.head(20).reset_index()
        top20.columns = ["Mot-clé", "Occurrences"]
        top20["Pourcentage"] = (top20["Occurrences"] / total * 100).round(2)
        max_pct    = top20["Pourcentage"].max()
        bar_colors = [PRIMARY, PRIMARY_LIGHT, ACCENT, DARK,
                      "#00CC96","#AB63FA","#FFA15A","#19D3F3","#FF6692","#B6E880",
                      "#636EFA","#EF553B","#00a5cc","#27348b","#a60f79","#1067a3",
                      "#FF97FF","#FECB52","#4dc0db","#0e2c5e"]

        rows = []
        for i, row in top20.iterrows():
            pct   = row["Pourcentage"]
            color = bar_colors[i % len(bar_colors)]
            bw    = f"{pct/max_pct*100:.1f}%" if max_pct > 0 else "0%"
            rows.append(html.Tr([
                html.Td(f"{i+1}", style={"width":"24px","color":"#9ca3af","fontSize":"0.73rem","fontWeight":"700","textAlign":"right","paddingRight":"8px","verticalAlign":"middle"}),
                html.Td(row["Mot-clé"], style={"fontSize":"0.82rem","fontWeight":"500","maxWidth":"140px","overflow":"hidden","textOverflow":"ellipsis","whiteSpace":"nowrap","verticalAlign":"middle","paddingRight":"10px"}),
                html.Td(html.Div([
                    html.Div(html.Div(style={"width":bw,"height":"100%","backgroundColor":color,"borderRadius":"3px"}),
                             style={"width":"90px","height":"8px","backgroundColor":"rgba(0,0,0,0.07)","borderRadius":"3px","overflow":"hidden","flexShrink":"0"}),
                    html.Span(f"{pct:.2f}%", style={"fontSize":"0.73rem","color":"#374151","marginLeft":"7px","fontWeight":"600","minWidth":"42px"}),
                ], style={"display":"flex","alignItems":"center"}), style={"verticalAlign":"middle"}),
                html.Td(f"{int(row['Occurrences'])}", style={"fontSize":"0.73rem","color":"#9ca3af","textAlign":"right","verticalAlign":"middle","paddingLeft":"8px"}),
            ], style={"borderBottom":"1px solid rgba(0,0,0,0.05)"}))

        table = html.Table([
            html.Thead(html.Tr([
                html.Th("#",         style={"width":"24px","fontSize":"0.70rem","color":"#9ca3af","textAlign":"right","paddingRight":"8px","paddingBottom":"6px"}),
                html.Th("Mot-clé",   style={"fontSize":"0.70rem","color":"#9ca3af","paddingBottom":"6px"}),
                html.Th("Fréquence", style={"fontSize":"0.70rem","color":"#9ca3af","paddingBottom":"6px"}),
                html.Th("N",         style={"fontSize":"0.70rem","color":"#9ca3af","textAlign":"right","paddingLeft":"8px","paddingBottom":"6px"}),
            ], style={"borderBottom":"2px solid rgba(0,0,0,0.10)"})),
            html.Tbody(rows),
        ], style={"width":"100%","borderCollapse":"collapse"})

        return img_src, table

    # ========================================================
    # 3 — RÉSEAU
    # ========================================================
    @app.callback(
        [Output("network", "figure"), Output("network-fullscreen", "figure"), Output("network-graph-data", "data")],
        [Input("centre", "value"), Input("equipe", "value"), Input("pays", "value"),
         Input("ville",  "value"), Input("org",    "value"), Input("annee", "value"),
         Input("tabs", "value"),   Input("store-data", "data"),
         Input("network-max-pubs", "value"), Input("network-max-nodes", "value"),
         Input("toggle-dark", "n_clicks"),   Input("network-anonymize", "n_clicks")],
    )
    def update_network(centres, equipes, pays, villes, orgs, annees, tab, stored_data,
                       max_pubs, max_nodes, dark_clicks, anonymize_clicks):
        if tab != "tab-network":
            return no_update, no_update, no_update

        df  = pd.DataFrame(stored_data) if stored_data is not None else df_base
        dff = filter_df(df, centres, equipes, pays, villes, orgs, annees)

        if dff.empty or "HalID" not in dff.columns:
            fig_empty = go.Figure().update_layout(
                template=GRAPH_TEMPLATE,
                title="Réseau de copublications (aucune donnée pour les filtres actuels)",
                xaxis=dict(visible=False), yaxis=dict(visible=False),
                paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                hovermode="closest", margin=dict(l=10, r=10, t=60, b=10))
            return fig_empty, fig_empty, {}

        halids = dff["HalID"].dropna().unique().tolist()
        if max_pubs is None: max_pubs = 1500
        if len(halids) > max_pubs:
            halids_keep = pd.Series(halids).sample(max_pubs, random_state=42).tolist()
            dff_small   = dff[dff["HalID"].isin(halids_keep)].copy()
        else:
            dff_small = dff.copy()

        import re as _re
        centres_stats = {}; fr_stats = {}; foreign_stats = {}; edge_weights = {}
        fr_to_foreign = {}; fr_to_centres = {}; fg_to_fr = {}

        VALEURS_VIDES = {"nan", "none", "n/a", "na", "", "null"}
        def _clean(v):
            s = str(v or "").strip()
            return "" if s.lower() in VALEURS_VIDES else s

        for _, row in dff_small.iterrows():
            centre_name = _clean(row.get("Centre")) or "Centre Inria"
            centre_id   = f"centre::{centre_name}"
            halid       = row.get("HalID")
            country     = _clean(row.get("Pays"))    or "Pays inconnu"
            city        = _clean(row.get("Ville"))   or ""
            org         = _clean(row.get("Organisme_copubliant")) or ""

            c_stats = centres_stats.setdefault(centre_id, {
                "type":"centre","label":centre_name,"pubs":set(),"fr_authors":set(),
                "foreign_authors":set(),"countries":set(),"cities":set(),"orgs":set()})
            if pd.notna(halid): c_stats["pubs"].add(halid)
            if country: c_stats["countries"].add(country)
            if city:    c_stats["cities"].add(city)
            if org:     c_stats["orgs"].add(org)

            fr_list = [a.strip() for a in _clean(row.get("Auteurs_FR","")).split(";") if a.strip()]
            co_list = [b.strip() for b in _clean(row.get("Auteurs_copubliants","")).split(";") if b.strip()]

            for a in fr_list:
                fr_id = f"fr::{a}"
                st = fr_stats.setdefault(fr_id, {"type":"fr","label":a,"pubs":set(),"countries":set()})
                if pd.notna(halid): st["pubs"].add(halid)
                if country: st["countries"].add(country)
                c_stats["fr_authors"].add(fr_id)
                d = fr_to_centres.setdefault(fr_id, {})
                d[centre_id] = d.get(centre_id, 0) + 1
                key = (centre_id, fr_id)
                edge_weights[key] = edge_weights.get(key, 0) + 1

            for b in co_list:
                fg_id = f"foreign::{b}"
                st = foreign_stats.setdefault(fg_id, {
                    "type":"foreign","label":b,"pubs":set(),"country":country,"city":city,"org":org})
                if pd.notna(halid): st["pubs"].add(halid)
                if not st.get("org") and org:   st["org"]  = org
                if not st.get("city") and city: st["city"] = city
                c_stats["foreign_authors"].add(fg_id)
                for a in fr_list:
                    fr_id = f"fr::{a}"
                    d  = fg_to_fr.setdefault(fg_id, {})
                    d[fr_id] = d.get(fr_id, 0) + 1
                    d2 = fr_to_foreign.setdefault(fr_id, {})
                    d2[fg_id] = d2.get(fg_id, 0) + 1
                    key = (fr_id, fg_id)
                    edge_weights[key] = edge_weights.get(key, 0) + 1

        for cid, st in centres_stats.items():
            st["pubs"] = len(st["pubs"]); st["nb_fr"] = len(st["fr_authors"])
            st["nb_foreign"] = len(st["foreign_authors"]); st["nb_countries"] = len(st["countries"])
            st["nb_cities"] = len(st["cities"]); st["nb_orgs"] = len(st["orgs"])
            st["countries_list"] = sorted(st["countries"])
        for st in fr_stats.values():
            st["pubs"] = len(st["pubs"]); st["nb_countries"] = len(st["countries"])
        for st in foreign_stats.values():
            st["pubs"] = len(st["pubs"])

        node_attrs = {}
        node_attrs.update(centres_stats); node_attrs.update(fr_stats); node_attrs.update(foreign_stats)
        filtered_edges = {(u,v):w for (u,v),w in edge_weights.items() if u in node_attrs and v in node_attrs}

        G = nx.Graph()
        for nid, attr in node_attrs.items(): G.add_node(nid, **attr)
        for (u,v), w in filtered_edges.items(): G.add_edge(u, v, weight=w)

        if G.number_of_nodes() == 0:
            fig_empty = go.Figure().update_layout(template=GRAPH_TEMPLATE,
                title="Réseau de copublications (trop filtré / aucune donnée)",
                xaxis=dict(visible=False), yaxis=dict(visible=False),
                paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
            return fig_empty, fig_empty, {}

        k   = 0.45 + 0.02 * math.log(G.number_of_nodes() + 1)
        pos = nx.spring_layout(G, k=k, iterations=30, seed=42)
        coords  = np.array(list(pos.values()))
        max_abs = np.abs(coords).max()
        if max_abs > 0: coords = coords / max_abs
        rng     = np.random.RandomState(42)
        coords  = coords + 0.01 * rng.normal(size=coords.shape)
        max_abs = np.abs(coords).max()
        if max_abs > 0: coords = coords / max_abs
        for nid, c in zip(pos.keys(), coords): pos[nid] = c

        is_dark = bool(dark_clicks) and (dark_clicks % 2 == 1)
        if is_dark:
            BG_NET="$0f1117"; EDGE_COLOR="rgba(148,163,184,0.18)"; LEGEND_BG="rgba(10,12,20,0.88)"
            LEGEND_FG="#cbd5e1"; LEGEND_BORDER="rgba(255,255,255,0.10)"; HALO_A=[0.05,0.12,0.22]
            DISC_A=0.88; HOVER_BG="#1e293b"; HOVER_FG="#f1f5f9"
            LABEL_FR_COLOR="#e2e8f0"; LABEL_FG_COLOR="#94a3b8"; BG_NET="#0f1117"
        else:
            BG_NET="#f0f4f8"; EDGE_COLOR="rgba(100,116,139,0.14)"; LEGEND_BG="rgba(255,255,255,0.92)"
            LEGEND_FG="#334155"; LEGEND_BORDER="rgba(0,0,0,0.10)"; HALO_A=[0.04,0.10,0.20]
            DISC_A=0.90; HOVER_BG="white"; HOVER_FG="#1e293b"
            LABEL_FR_COLOR="#1e293b"; LABEL_FG_COLOR="#334155"

        centre_names     = sorted({a["label"] for a in node_attrs.values() if a["type"] == "centre"})
        centre_color_map = {n: get_centre_color(n, i) for i, n in enumerate(centre_names)}

        def _hex_rgb(h):
            h = h.lstrip("#")
            return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        def _rgba(hex_c, alpha):
            r,g,b = _hex_rgb(hex_c)
            return f"rgba({r},{g},{b},{alpha})"

        fr_to_centre = {}
        for cid, cstats in centres_stats.items():
            for frid in cstats.get("fr_authors", set()):
                fr_to_centre[frid] = cstats["label"]

        cx=[]; cy=[]; csz=[]; cout=[]; clbl=[]; ccd=[]
        frx=[]; fry=[]; frsz=[]; frcol=[]; frlbl=[]; frcd=[]
        fgx=[]; fgy=[]; fgsz=[]; fglbl=[]; fgcd=[]
        node_lookup = {}
        total_pubs_global = sum(v["pubs"] for v in centres_stats.values()) or 1

        def _sep(): return "<br><span style='color:rgba(150,150,150,0.5)'>──────────────</span><br>"

        for nid, attrs in node_attrs.items():
            x, y  = pos[nid]
            ntype = attrs["type"]
            if ntype == "centre":
                c_hex = centre_color_map.get(attrs["label"], "#888888")
                sz    = 38 + 7 * math.sqrt(max(attrs["pubs"], 1))
                cx.append(x); cy.append(y); csz.append(sz); cout.append(c_hex); clbl.append(attrs["label"])
                pct  = round(attrs["pubs"] / total_pubs_global * 100, 1)
                c_str = ", ".join(attrs.get("countries_list",[])[:10]) or "—"
                ccd.append(f"<b style='font-size:14px'>🏛 {attrs['label']}</b>" + _sep() +
                            f"📄 <b>{attrs['pubs']}</b> copublications (<b>{pct}%</b>)<br>"
                            f"👤 <b>{attrs['nb_fr']}</b> auteurs Inria · "
                            f"🌍 <b>{attrs['nb_foreign']}</b> étrangers<br>"
                            f"🗺 <b>{attrs['nb_countries']}</b> pays · 🏙 <b>{attrs.get('nb_cities',0)}</b> villes<br>"
                            f"🏢 <b>{attrs.get('nb_orgs',0)}</b> organismes" + _sep() + f"<i>Pays : {c_str}</i>")
                node_lookup[nid] = {"type":"centre","label":attrs["label"]}
            elif ntype == "fr":
                centre_lbl = fr_to_centre.get(nid, "—")
                c_hex = centre_color_map.get(centre_lbl, "#00bcd4")
                frx.append(x); fry.append(y)
                frsz.append(9 + 3.5 * math.sqrt(max(attrs["pubs"], 1)))
                frcol.append(_rgba(c_hex, 0.90)); frlbl.append(attrs["label"])
                top_fg = sorted(fr_to_foreign.get(nid,{}).items(), key=lambda kv:-kv[1])[:6]
                top_fg_str = "<br>".join(f"  • {fid.replace('foreign::','')} ({n})" for fid,n in top_fg) or "  —"
                frcd.append(f"<b style='font-size:13px'>👤 {attrs['label']}</b>" + _sep() +
                             f"🏛 Centre : <b>{centre_lbl}</b><br>📄 <b>{attrs['pubs']}</b> copublications<br>"
                             f"🌍 <b>{attrs.get('nb_countries',0)}</b> pays partenaires" + _sep() +
                             "<i>Principaux co-auteurs étrangers :</i><br>" + top_fg_str)
                node_lookup[nid] = {"type":"fr","label":attrs["label"]}
            elif ntype == "foreign":
                fgx.append(x); fgy.append(y)
                fgsz.append(6 + 2.5 * math.sqrt(max(attrs["pubs"], 1))); fglbl.append(attrs["label"])
                collab_c = set()
                for fr_id in fg_to_fr.get(nid, {}):
                    c_lbl = fr_to_centre.get(fr_id, "")
                    if c_lbl: collab_c.add(c_lbl)
                top_fr = sorted(fg_to_fr.get(nid,{}).items(), key=lambda kv:-kv[1])[:6]
                top_fr_str = "<br>".join(f"  • {fid.replace('fr::','')} ({n})" for fid,n in top_fr) or "  —"
                fgcd.append(f"<b style='font-size:13px'>🌐 {attrs['label']}</b>" + _sep() +
                             f"🗺 Pays : <b>{attrs.get('country','—')}</b><br>"
                             f"🏙 Ville : <b>{attrs.get('city','—')}</b><br>"
                             f"🏢 Organisme : <b>{attrs.get('org','—')}</b><br>"
                             f"📄 <b>{attrs['pubs']}</b> copublications" + _sep() +
                             f"<i>Centres partenaires :</i><br>  {', '.join(sorted(collab_c)) or '—'}" + _sep() +
                             "<i>Principaux auteurs Inria :</i><br>" + top_fr_str)
                node_lookup[nid] = {"type":"foreign","label":attrs["label"]}

        ex=[]; ey=[]
        for u,v in G.edges():
            x0,y0=pos[u]; x1,y1=pos[v]
            ex+=[x0,x1,None]; ey+=[y0,y1,None]

        anonymize_fg = bool(anonymize_clicks) and (anonymize_clicks % 2 == 1)

        edge_trace   = go.Scattergl(x=ex,y=ey,mode="lines",line=dict(width=0.8,color=EDGE_COLOR),hoverinfo="none",showlegend=False,name="_edges")
        fg_trace     = go.Scattergl(x=fgx,y=fgy,mode="markers",marker=dict(size=fgsz,color="rgba(100,116,139,0.55)" if not is_dark else "rgba(148,163,184,0.50)",line=dict(width=0.8,color="rgba(255,255,255,0.60)")),customdata=fgcd,hovertemplate="%{customdata}<extra></extra>",showlegend=False,name="")
        fr_trace     = go.Scattergl(x=frx,y=fry,mode="markers",marker=dict(size=frsz,color=frcol,line=dict(width=0.8,color="rgba(255,255,255,0.70)"),opacity=0.90),customdata=frcd,hovertemplate="%{customdata}<extra></extra>",showlegend=False,name="")
        halo_traces  = [go.Scattergl(x=cx,y=cy,mode="markers",marker=dict(size=[s*hsz for s in csz],color=[_rgba(c,ha) for c in cout],line=dict(width=1,color=[_rgba(c,ha*2) for c in cout])),hoverinfo="skip",showlegend=False) for hsz,ha in zip([4.5,2.8,1.7],HALO_A)]
        centre_disc  = go.Scattergl(x=cx,y=cy,mode="markers",marker=dict(size=csz,color=[_rgba(c,DISC_A) for c in cout],line=dict(width=2.5,color="rgba(255,255,255,0.90)")),customdata=ccd,hovertemplate="%{customdata}<extra></extra>",showlegend=False,name="")
        centre_labels= go.Scatter(x=cx,y=cy,mode="text",text=clbl,textposition="bottom center",textfont=dict(size=12,color="#1e293b" if not is_dark else "#f1f5f9",family="Open Sans, Arial, sans-serif"),hoverinfo="skip",showlegend=False,name="")
        fr_lbl_trace = go.Scattergl(x=frx,y=fry,mode="text",text=frlbl,textposition="top center",textfont=dict(size=8,color=LABEL_FR_COLOR,family="Open Sans, Arial, sans-serif"),hoverinfo="skip",showlegend=False)
        fg_lbl_trace = go.Scattergl(x=fgx,y=fgy,mode="text",text=["" if anonymize_fg else lbl for lbl in fglbl],textposition="top center",textfont=dict(size=8,color=LABEL_FG_COLOR,family="Open Sans, Arial, sans-serif"),hoverinfo="skip",showlegend=False)

        legend_traces = [go.Scattergl(x=[None],y=[None],mode="markers",name=cname,marker=dict(size=12,color=_rgba(chex,0.85),line=dict(width=2,color=chex)),showlegend=True) for cname,chex in centre_color_map.items()]
        legend_traces += [
            go.Scattergl(x=[None],y=[None],mode="markers",marker=dict(size=10,color=frcol[0] if frcol else "#636EFA",line=dict(width=1,color="white")),name="Auteur Inria",showlegend=True),
            go.Scattergl(x=[None],y=[None],mode="markers",marker=dict(size=10,color="rgba(100,116,139,0.70)",line=dict(width=1,color="white")),name="Auteur étranger",showlegend=True),
        ]

        fig_net = go.Figure(data=[edge_trace]+halo_traces+[fg_trace,fr_trace,centre_disc,centre_labels,fr_lbl_trace,fg_lbl_trace]+legend_traces)
        fig_net.update_layout(
            title=None, showlegend=True,
            legend=dict(title=dict(text="<b>Centres Inria</b>",font=dict(size=11,color=LEGEND_FG)),
                        orientation="v",x=0.01,xanchor="left",y=0.99,yanchor="top",
                        bgcolor=LEGEND_BG,bordercolor=LEGEND_BORDER,borderwidth=1,
                        font=dict(size=10,color=LEGEND_FG),itemsizing="constant"),
            xaxis=dict(showgrid=False,zeroline=False,visible=False),
            yaxis=dict(showgrid=False,zeroline=False,visible=False,scaleanchor="x",scaleratio=1),
            margin=dict(l=0,r=0,t=40,b=50), hovermode="closest",
            paper_bgcolor=BG_NET, plot_bgcolor=BG_NET,
            hoverlabel=dict(bgcolor=HOVER_BG,font_size=12,font_color=HOVER_FG,bordercolor=LEGEND_BORDER,namelength=0,align="left"),
            clickmode="none",
            annotations=[
                dict(x=0.99,y=0.99,xref="paper",yref="paper",xanchor="right",yanchor="top",
                     text=f"<span style='color:{LEGEND_FG};font-size:11px'><b>{G.number_of_nodes()}</b> nœuds · <b>{G.number_of_edges()}</b> liens</span>",
                     showarrow=False,bgcolor=LEGEND_BG,bordercolor=LEGEND_BORDER,borderwidth=1,borderpad=6),
                dict(x=0.5,y=-0.005,xref="paper",yref="paper",xanchor="center",yanchor="top",
                     text=f"<span style='color:{LEGEND_FG};font-size:10px'>● Auteurs Inria (couleur = centre) &nbsp;● Auteurs étrangers &nbsp;◯ Centre</span>",
                     showarrow=False,bgcolor=LEGEND_BG,bordercolor=LEGEND_BORDER,borderwidth=1,borderpad=6),
            ])
        fig_net.layout.hovermode = "closest"
        return fig_net, fig_net, node_lookup

    # ========================================================
    @app.callback(
        Output("network-fullscreen-modal", "style"),
        [Input("btn-network-fullscreen-open", "n_clicks"), Input("btn-network-fullscreen-close", "n_clicks")],
        State("network-fullscreen-modal", "style"),
        prevent_initial_call=True,
    )
    def toggle_network_fullscreen(open_clicks, close_clicks, current_style):
        ctx = dash.callback_context
        if not ctx.triggered: return current_style
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        style_open   = {"display":"block","position":"fixed","inset":"0","background":"rgba(0,0,0,0.35)","zIndex":"9999","padding":"24px"}
        style_closed = {**style_open, "display":"none"}
        if trigger == "btn-network-fullscreen-open":  return style_open
        if trigger == "btn-network-fullscreen-close": return style_closed
        return current_style

    # ========================================================
    # 4 — Onglet "Évolution des copublications" — FIX COMPLET
    # ========================================================
    @app.callback(
        [
            Output("sunburst_collab", "figure"),
            Output("radar_centre",    "figure"),
            Output("team_timeline",   "figure"),
            Output("sankey_collab",   "figure"),
            Output("story_evol",      "children"),
        ],
        [
            Input("centre",      "value"),
            Input("equipe",      "value"),
            Input("pays",        "value"),
            Input("ville",       "value"),
            Input("org",         "value"),
            Input("annee",       "value"),
            Input("tabs",        "value"),
            Input("store-data",  "data"),
        ],
    )
    def update_evolution(centres, equipes, pays, villes, orgs, annees, tab, stored_data):

        # ── Garde : ne calcule que quand l'onglet est actif ──
        if tab != "tab-evolution":
            return no_update, no_update, no_update, no_update, no_update

        df  = pd.DataFrame(stored_data) if stored_data is not None else df_base
        dff = filter_df(df, centres, equipes, pays, villes, orgs, annees)

        def _empty_fig(title="Aucune donnée"):
            return go.Figure().update_layout(template=GRAPH_TEMPLATE, title=title)

        if dff.empty:
            story = html.Div([
                html.H5("Résumé", className="mb-2", style={"color": PRIMARY}),
                html.P("Aucune copublication pour les filtres sélectionnés."),
            ], style={"backgroundColor":"#f8fbff","borderRadius":"12px","border":f"1px solid {PRIMARY_LIGHT}30"})
            return _empty_fig(), _empty_fig(), _empty_fig(), _empty_fig(), story

        # ── 1) SUNBURST ──
        if all(c in dff.columns for c in ["Centre","Equipe","Organisme_copubliant"]):
            sun_df = (dff.groupby(["Centre","Equipe","Organisme_copubliant"], observed=True)["HalID"]
                      .nunique().reset_index(name="Publications"))
            cmap   = {c: get_centre_color(c, i) for i, c in enumerate(sun_df["Centre"].unique())}
            fig_sunburst = px.sunburst(sun_df, path=["Centre","Equipe","Organisme_copubliant"],
                                       values="Publications", color="Centre",
                                       color_discrete_map=cmap, title="Centre → Équipe → Organisme")
            fig_sunburst.update_layout(template=GRAPH_TEMPLATE)
        else:
            fig_sunburst = _empty_fig("Hiérarchie (colonnes manquantes)")

        # ── 2) TEAM TIMELINE ──
        if all(c in dff.columns for c in ["Année","Equipe"]):
            team_df = (dff.groupby(["Année","Equipe"], observed=True)["HalID"]
                       .nunique().reset_index(name="Publications"))
            fig_team = px.line(team_df, x="Année", y="Publications", color="Equipe",
                               markers=True, color_discrete_sequence=QUAL_PALETTE,
                               title="Évolution des copublications par équipe")
            fig_team.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Année : %{x}<br>Copublications : <b>%{y}</b><extra></extra>")
            fig_team.update_layout(template=GRAPH_TEMPLATE, hovermode="closest",
                                   legend_itemclick="toggleothers", legend_itemdoubleclick="toggle")
        else:
            fig_team = _empty_fig("Évolution par équipe (colonnes manquantes)")

        # ── 3) SANKEY ──
        if all(c in dff.columns for c in ["Centre","Pays","Organisme_copubliant"]):
            sankey_df = (dff.groupby(["Centre","Pays","Organisme_copubliant"], observed=True)["HalID"]
                         .nunique().reset_index(name="Publications")
                         .sort_values("Publications", ascending=False).head(80))
            labels=[]; node_index={}
            def get_idx(lbl):
                if lbl not in node_index:
                    node_index[lbl] = len(node_index); labels.append(lbl)
                return node_index[lbl]
            sources=[]; targets=[]; values=[]
            for _, row in sankey_df.iterrows():
                c=get_idx(f"Centre : {row['Centre']}"); p=get_idx(f"Pays : {row['Pays']}")
                o=get_idx(f"Org : {row['Organisme_copubliant']}"); v=row["Publications"]
                sources+=[c,p]; targets+=[p,o]; values+=[v,v]
            def _snk_color(lbl):
                if lbl.startswith("Centre : "): return get_centre_color(lbl[len("Centre : "):], 0)
                if lbl.startswith("Pays : "):   return "rgba(100,130,200,0.70)"
                return "rgba(160,160,160,0.55)"
            fig_sankey = go.Figure(data=[go.Sankey(
                node=dict(pad=15,thickness=15,line=dict(color="black",width=0.3),
                          label=labels,color=[_snk_color(l) for l in labels]),
                link=dict(source=sources,target=targets,value=values,color="rgba(39,52,139,0.2)"))])
            fig_sankey.update_layout(template=GRAPH_TEMPLATE, title="Flux Centre → Pays → Organisme")
        else:
            fig_sankey = _empty_fig("Flux (colonnes manquantes)")

        # ── 4) RADAR ──
        if "Centre" in dff.columns and "Domaine(s)" in dff.columns:
            dom_df = (dff.dropna(subset=["Centre","Domaine(s)"])
                      .groupby(["Centre","Domaine(s)"], observed=True)["HalID"]
                      .nunique().reset_index(name="Publications"))
            if dom_df.empty:
                fig_radar = _empty_fig("Profil par domaine (aucune donnée)")
            else:
                if centres:
                    ctp = [c for c in centres if c in dom_df["Centre"].unique()]
                else:
                    ctp = dom_df.groupby("Centre",observed=True)["Publications"].sum().sort_values(ascending=False).head(5).index.tolist()
                if not ctp:
                    ctp = dom_df.groupby("Centre",observed=True)["Publications"].sum().sort_values(ascending=False).head(5).index.tolist()

                top_dom = dom_df.groupby("Domaine(s)",observed=True)["Publications"].sum().sort_values(ascending=False).head(8).index.tolist()
                cats    = top_dom
                c_tots  = dom_df[dom_df["Centre"].isin(ctp)].groupby("Centre",observed=True)["Publications"].sum().to_dict()

                def _hex_to_rgba(hex_color, alpha=0.15):
                    h = hex_color.lstrip("#")
                    if len(h) == 3: h = "".join([c*2 for c in h])
                    r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
                    return f"rgba({r},{g},{b},{alpha})"

                def _wrap(s, mx=18):
                    s = str(s).strip()
                    if len(s) <= mx: return s
                    words=s.split(); lines=[]; cur=""
                    for w in words:
                        if len(cur)+len(w)+1 <= mx: cur=(cur+" "+w).strip()
                        else:
                            if cur: lines.append(cur)
                            cur=w
                    if cur: lines.append(cur)
                    return "<br>".join(lines)

                cats_w  = [_wrap(d) for d in cats]
                cats_wc = cats_w + cats_w[:1]

                fig_radar = go.Figure()
                for i, centre in enumerate(ctp):
                    sub   = dom_df[dom_df["Centre"] == centre]
                    total = c_tots.get(centre, 1) or 1
                    vals  = [round(sub.loc[sub["Domaine(s)"]==d,"Publications"].sum()/total*100,1) for d in cats]
                    color = get_centre_color(centre, i)
                    fig_radar.add_trace(go.Scatterpolar(
                        r=vals+vals[:1], theta=cats_wc, fill="toself", name=centre,
                        line=dict(color=color,width=2.5), fillcolor=_hex_to_rgba(color,0.15),
                        opacity=1, hovertemplate="<b>"+centre+"</b><br>%{theta} : <b>%{r:.1f}%</b><extra></extra>"))

                titre_c = " · ".join(ctp) if len(ctp)<=3 else f"{len(ctp)} centres"
                fig_radar.update_layout(
                    template=GRAPH_TEMPLATE,
                    title=dict(text=f"Profil par domaine — {titre_c}",font=dict(size=13),x=0.5,xanchor="center"),
                    polar=dict(domain=dict(x=[0.12,0.88],y=[0.10,0.92]),bgcolor="rgba(240,244,255,0.45)",
                               radialaxis=dict(visible=True,ticksuffix="%",tickfont=dict(size=9,color="#6b7280"),
                                               gridcolor="rgba(0,0,0,0.10)",linecolor="rgba(0,0,0,0.12)",range=[0,None],showline=True,tickangle=0),
                               angularaxis=dict(tickfont=dict(size=10,color=PRIMARY,family="Open Sans, Arial, sans-serif"),
                                                linecolor="rgba(0,0,0,0.15)",gridcolor="rgba(0,0,0,0.08)",rotation=90,direction="clockwise")),
                    legend=dict(orientation="h",x=0.5,xanchor="center",y=-0.05,yanchor="top",
                                font=dict(size=11),bgcolor="rgba(255,255,255,0.85)",bordercolor="rgba(0,0,0,0.08)",borderwidth=1),
                    margin=dict(l=110,r=110,t=60,b=80),
                    hoverlabel=dict(bgcolor="white",font_size=12,font_color=PRIMARY))
        else:
            fig_radar = _empty_fig("Profil par domaine (colonnes Centre / Domaine(s) manquantes)")

        # ── 5) STORY ──
        total_pubs = dff["HalID"].nunique() if "HalID" in dff.columns else len(dff)
        nb_pays    = dff["Pays"].nunique()   if "Pays"  in dff.columns else 0
        nb_orgs    = dff["Organisme_copubliant"].nunique() if "Organisme_copubliant" in dff.columns else 0
        years      = dff["Année"].dropna().astype(int) if "Année" in dff.columns else pd.Series([], dtype=int)
        periode    = f"{int(years.min())}–{int(years.max())}" if len(years) > 0 else "période inconnue"

        c_present = dff["Centre"].dropna().unique().tolist() if "Centre" in dff.columns else []
        c_story   = [c for c in centres if c in c_present] if centres and c_present else c_present
        if not c_story:        c_txt = "les centres Inria impliqués"
        elif len(c_story) == 1: c_txt = f"le centre {c_story[0]}"
        else:                   c_txt = "les centres " + ", ".join(c_story)

        story = html.Div([
            html.H5("Résumé des copublications", className="mb-2", style={"color": PRIMARY}),
            html.P(f"Sur la période {periode}, les filtres actuels représentent {total_pubs} copublications "
                   f"impliquant {nb_pays} pays et {nb_orgs} organismes partenaires.", className="mb-1"),
            html.P(f"Les profils par domaine et les flux décrits ci-dessus mettent en évidence le rôle de {c_txt}.", className="mb-0"),
        ], style={"backgroundColor":"#f8fbff","borderRadius":"12px","border":f"1px solid {PRIMARY_LIGHT}30"})

        return fig_sunburst, fig_radar, fig_team, fig_sankey, story

    # ========================================================
    # 5 — Onglet "Évolution par pays"
    # ========================================================
    @app.callback(
        [Output("country_line_chart","figure"), Output("country_heatmap","figure"), Output("country_top_bar","figure")],
        [Input("centre","value"), Input("equipe","value"), Input("pays","value"),
         Input("ville","value"),  Input("org","value"),    Input("annee","value"),
         Input("tabs","value"),   Input("store-data","data"), Input("country-top-n","value")],
    )
    def update_country_evolution(centres, equipes, pays, villes, orgs, annees, tab, stored_data, top_n):
        if tab != "tab-country-evolution":
            return no_update, no_update, no_update

        df  = pd.DataFrame(stored_data) if stored_data is not None else df_base
        dff = filter_df(df, centres, equipes, pays, villes, orgs, annees)
        top_n = top_n or 10
        empty_fig = go.Figure().update_layout(template=GRAPH_TEMPLATE, title="Aucune donnée pour les filtres actuels")

        if dff.empty or "Pays" not in dff.columns or "Année" not in dff.columns:
            return empty_fig, empty_fig, empty_fig

        top_pays_list = (dff.groupby("Pays",observed=True)["HalID"].nunique()
                         .sort_values(ascending=False).head(top_n).index.tolist())
        dff_top = dff[dff["Pays"].isin(top_pays_list)]

        line_df = (dff_top.groupby(["Année","Pays"],observed=True)["HalID"]
                   .nunique().reset_index(name="Publications").sort_values("Année"))
        if line_df.empty:
            fig_line = empty_fig
        else:
            fig_line = px.line(line_df, x="Année", y="Publications", color="Pays",
                               markers=True, color_discrete_sequence=QUAL_PALETTE,
                               title=f"Évolution annuelle – Top {top_n} pays")
            fig_line.update_traces(line=dict(width=2.5), marker=dict(size=7),
                hovertemplate="<b>%{fullData.name}</b><br>Année : %{x}<br>Publications : <b>%{y}</b><extra></extra>")
            fig_line.update_layout(template=GRAPH_TEMPLATE, hovermode="closest",
                legend=dict(orientation="v",x=1.02,xanchor="left",y=1,yanchor="top",
                            font=dict(size=10),bgcolor="rgba(255,255,255,0.85)"),
                margin=dict(l=10,r=10,t=50,b=40),
                legend_itemclick="toggleothers", legend_itemdoubleclick="toggle")

        pivot_df = (dff_top.groupby(["Pays","Année"],observed=True)["HalID"].nunique().unstack(fill_value=0))
        if pivot_df.empty:
            fig_heatmap = empty_fig
        else:
            pivot_df = pivot_df.loc[pivot_df.sum(axis=1).sort_values(ascending=False).index]
            years_cols = sorted(pivot_df.columns.tolist()); pivot_df = pivot_df[years_cols]
            fig_heatmap = go.Figure(go.Heatmap(
                z=pivot_df.values, x=[str(int(y)) for y in years_cols], y=pivot_df.index.tolist(),
                colorscale=[[0,"#ccedf6"],[0.4,"#00a5cc"],[0.7,"#1067a3"],[1,"#27348b"]],
                hovertemplate="Pays : %{y}<br>Année : %{x}<br>Publications : %{z}<extra></extra>", showscale=True))
            fig_heatmap.update_layout(template=GRAPH_TEMPLATE,
                title=f"Heatmap – Top {top_n} pays × année",
                xaxis=dict(title="Année",tickangle=-35), yaxis=dict(title=""),
                margin=dict(l=10,r=10,t=50,b=40))

        bar_df = (dff_top.groupby("Pays",observed=True)["HalID"].nunique()
                  .reset_index(name="Publications").sort_values("Publications",ascending=True))
        if bar_df.empty:
            fig_bar = empty_fig
        else:
            colors_bar = [QUAL_PALETTE[i%len(QUAL_PALETTE)] for i in range(len(bar_df))]
            fig_bar = go.Figure(go.Bar(x=bar_df["Publications"], y=bar_df["Pays"],
                orientation="h", marker=dict(color=colors_bar,line=dict(width=0)),
                hovertemplate="Pays : %{y}<br>Publications : %{x}<extra></extra>",
                text=bar_df["Publications"], textposition="outside"))
            fig_bar.update_layout(template=GRAPH_TEMPLATE, title=f"Volume total – Top {top_n} pays",
                xaxis=dict(title="Publications"), yaxis=dict(title=""),
                margin=dict(l=10,r=10,t=50,b=40), showlegend=False)

        return fig_line, fig_heatmap, fig_bar

    # ========================================================
    # 6 — ONGLET PARTS RELATIVES
    # ========================================================
    @app.callback(
        [Output("share-pays","figure"),   Output("share-centre","figure"),
         Output("share-org","figure"),    Output("share-equipe","figure"),
         Output("share-evol","figure"),   Output("share-kpi-zone","children")],
        [Input("centre","value"), Input("equipe","value"), Input("pays","value"),
         Input("ville","value"),  Input("org","value"),    Input("annee","value"),
         Input("tabs","value"),   Input("store-data","data")],
    )
    def update_share(centres, equipes, pays, villes, orgs, annees, tab, stored_data):
        if tab != "tab-share":
            return (no_update,) * 6

        df       = pd.DataFrame(stored_data) if stored_data is not None else df_base
        dff      = filter_df(df, centres, equipes, pays, villes, orgs, annees)
        df_global= filter_df(df, None, None, None, None, None, annees)
        total_global = df_global["HalID"].nunique() if not df_global.empty else 1
        total_sel    = dff["HalID"].nunique()

        empty_fig = go.Figure().update_layout(template=GRAPH_TEMPLATE, title="Aucune sélection ou donnée insuffisante")

        def _donut_share(df_sel, col, filtre_vals, use_local_total=False):
            if df_sel.empty or col not in df_sel.columns: return empty_fig
            denom = (total_sel if (use_local_total and total_sel > 0) else total_global) or 1
            if filtre_vals:
                rows = [{"label":str(v),"n":df_sel[df_sel[col].astype(str)==str(v)]["HalID"].nunique()} for v in filtre_vals]
                for r in rows: r["pct"] = r["n"] / denom * 100
                n_sel = sum(r["n"] for r in rows)
                rows.append({"label":"Reste (non sélectionné)","n":max(denom-n_sel,0),"pct":max(denom-n_sel,0)/denom*100})
                colors = ([get_centre_color(r["label"],i) for i,r in enumerate(rows[:-1])] if col=="Centre"
                          else [QUAL_PALETTE[i%len(QUAL_PALETTE)] for i in range(len(rows)-1)]) + ["rgba(200,200,200,0.35)"]
                fig = go.Figure(go.Pie(labels=[r["label"] for r in rows], values=[r["pct"] for r in rows],
                    hole=0.52, marker=dict(colors=colors), pull=[0.06]*(len(rows)-1)+[0],
                    textinfo="percent", hovertemplate="%{label}<br>Part : <b>%{value:.2f}%</b><extra></extra>", sort=False))
            else:
                grp = df_sel.groupby(col,observed=True)["HalID"].nunique().sort_values(ascending=False).head(8).reset_index(name="n")
                grp["pct"] = grp["n"] / denom * 100
                n_autres   = max(denom - grp["n"].sum(), 0)
                grp = pd.concat([grp, pd.DataFrame([{col:"Autres","n":n_autres,"pct":n_autres/denom*100}])], ignore_index=True)
                colors = ([get_centre_color(str(grp.iloc[i][col]),i) for i in range(len(grp)-1)] if col=="Centre"
                          else [QUAL_PALETTE[i%len(QUAL_PALETTE)] for i in range(len(grp)-1)]) + ["rgba(200,200,200,0.35)"]
                fig = go.Figure(go.Pie(labels=grp[col].astype(str), values=grp["pct"],
                    hole=0.52, marker=dict(colors=colors), textinfo="percent",
                    hovertemplate="%{label}<br>Part : <b>%{value:.2f}%</b><extra></extra>", sort=False))
            fig.update_layout(template=GRAPH_TEMPLATE, title=None, showlegend=True,
                legend=dict(orientation="v",x=1.02,xanchor="left",y=0.5,yanchor="middle",font=dict(size=10),bgcolor="rgba(255,255,255,0.85)"),
                margin=dict(l=10,r=10,t=10,b=10),
                annotations=[dict(text=f"<b>{total_sel/total_global*100:.1f}%</b><br>sélection",x=0.5,y=0.5,font_size=13,showarrow=False)])
            return fig

        use_local = bool(pays or villes)
        fig_pays   = _donut_share(dff, "Pays",                 pays,    use_local_total=False)
        fig_centre = _donut_share(dff, "Centre",               centres, use_local_total=use_local)
        fig_org    = _donut_share(dff, "Organisme_copubliant", orgs,    use_local_total=use_local)
        fig_equipe = _donut_share(dff, "Equipe",               equipes, use_local_total=use_local)

        if "Année" not in dff.columns or dff.empty:
            fig_evol = empty_fig
        else:
            ann_global  = df_global.groupby("Année",observed=True)["HalID"].nunique().reset_index(name="Total_global")
            traces_def  = []
            if pays:    traces_def.append(("Pays",                 pays,    "Pays"))
            if centres: traces_def.append(("Centre",               centres, "Centre"))
            if orgs:    traces_def.append(("Organisme_copubliant", orgs,    "Organisme"))
            if equipes: traces_def.append(("Equipe",               equipes, "Équipe"))
            if villes:  traces_def.append(("Ville",                villes,  "Ville"))
            if not traces_def: traces_def = [("__global__", None, "Sélection")]

            fig_evol  = go.Figure()
            color_idx = 0
            for col, vals, dim_label in traces_def:
                if col == "__global__":
                    ann_sel = dff.groupby("Année",observed=True)["HalID"].nunique().reset_index(name="n_sel")
                    merged  = ann_sel.merge(ann_global, on="Année", how="left")
                    merged["pct"] = (merged["n_sel"] / merged["Total_global"].replace(0,np.nan) * 100).round(2)
                    fig_evol.add_trace(go.Scattergl(x=merged["Année"],y=merged["pct"],mode="lines+markers",
                        name="Sélection globale", line=dict(width=2.5,color=QUAL_PALETTE[color_idx%len(QUAL_PALETTE)]),
                        marker=dict(size=7), hovertemplate="Année : %{x}<br>Part : <b>%{y:.2f}%</b><extra></extra>"))
                    color_idx += 1
                else:
                    for val in (vals or []):
                        ann_sel = (dff[dff[col].astype(str)==str(val)]
                                   .groupby("Année",observed=True)["HalID"].nunique().reset_index(name="n_sel"))
                        if ann_sel.empty: continue
                        merged = ann_sel.merge(ann_global, on="Année", how="left")
                        merged["pct"] = (merged["n_sel"] / merged["Total_global"].replace(0,np.nan) * 100).round(2)
                        tc = get_centre_color(str(val),color_idx) if col=="Centre" else QUAL_PALETTE[color_idx%len(QUAL_PALETTE)]
                        fig_evol.add_trace(go.Scattergl(x=merged["Année"],y=merged["pct"],mode="lines+markers",
                            name=f"{dim_label} : {val}", line=dict(width=2.5,color=tc), marker=dict(size=7),
                            hovertemplate=f"{dim_label} : {val}<br>Année : %{{x}}<br>Part : <b>%{{y:.2f}}%</b><extra></extra>"))
                        color_idx += 1
            fig_evol.update_layout(template=GRAPH_TEMPLATE, hovermode="x unified",
                yaxis=dict(title="Part (% du total annuel)",ticksuffix="%",rangemode="tozero"),
                xaxis=dict(title="Année",dtick=1),
                legend=dict(orientation="h",x=0.5,xanchor="center",y=-0.22,yanchor="top",font=dict(size=10)),
                margin=dict(l=10,r=10,t=20,b=60))

        pct_global = total_sel / total_global * 100 if total_global else 0
        def _fmt(n): return f"{int(n):,}".replace(",","\u202f")
        def _kpi(label, val, color):
            return dbc.Col(dbc.Card(dbc.CardBody([
                html.Div(label, className="small text-muted mb-1"),
                html.H4(val, className="fw-bold mb-0", style={"color":color}),
            ]), className="shadow-sm text-center",
                style={"borderRadius":"14px","border":f"1px solid {color}22"}), md=3,sm=6,xs=12)

        kpi_zone = dbc.Row([
            _kpi("Publications sélectionnées", _fmt(total_sel),             PRIMARY),
            _kpi("Total global (période)",      _fmt(total_global),          PRIMARY_LIGHT),
            _kpi("Part de la sélection",        f"{pct_global:.2f} %",       ACCENT),
            _kpi("Publications hors sélection", _fmt(total_global-total_sel), DARK),
        ], className="g-2 mt-1 mb-3")

        return fig_pays, fig_centre, fig_org, fig_equipe, fig_evol, kpi_zone