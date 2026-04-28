import os
from pathlib import Path
import pandas as pd

# ─────────────────────────────────────────────
# Chemins
# ─────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
XLSX_PATH   = BASE_DIR / "dashboard_dri_v3.xlsx"
CSV_PATH    = BASE_DIR / "dashboard_dri_v3.csv"
PARQUET_PATH = BASE_DIR / "dashboard_dri_v3.parquet"

# ─────────────────────────────────────────────
# Cache global — chargé UNE SEULE FOIS
# ─────────────────────────────────────────────
_CACHE = {
    "df":         None,   # DataFrame principal
    "aggregates": None,   # Pré-agrégations pour les graphiques
}


def create_csv_from_xlsx(xlsx_path=XLSX_PATH, csv_path=CSV_PATH, sheet_name=0, force=False):
    """Crée dashboard.csv depuis dashboard.xlsx."""
    print("XLSX attendu :", xlsx_path)
    print("CSV attendu  :", csv_path)

    if not xlsx_path.exists():
        raise FileNotFoundError(f"Fichier Excel introuvable : {xlsx_path}")

    csv_path.parent.mkdir(parents=True, exist_ok=True)

    if csv_path.exists() and not force:
        print("[INFO] CSV déjà présent, pas de recréation.")
        return

    print("[INFO] Lecture du XLSX...")
    df_excel = pd.read_excel(xlsx_path, sheet_name=sheet_name, dtype=str)

    print("[INFO] Écriture du CSV...")
    df_excel.to_csv(csv_path, index=False, encoding="utf-8-sig", sep=",")
    print(f"[OK] CSV créé : {csv_path} ({csv_path.stat().st_size} octets)")


def _build_parquet():
    """Convertit le CSV en Parquet si nécessaire (lecture 5x plus rapide)."""
    if PARQUET_PATH.exists():
        # Regénérer seulement si le CSV est plus récent
        if CSV_PATH.exists() and CSV_PATH.stat().st_mtime <= PARQUET_PATH.stat().st_mtime:
            return  # Parquet déjà à jour

    print("[INFO] Conversion CSV → Parquet...")
    encodings = ["utf-8-sig", "utf-8", "latin1"]
    seps = [",", ";"]
    df = None

    for enc in encodings:
        for sep in seps:
            try:
                df_try = pd.read_csv(
                    CSV_PATH, encoding=enc, sep=sep,
                    engine="python", on_bad_lines="skip", dtype=str,
                )
                if df_try is not None and df_try.shape[1] >= 2:
                    df = df_try
                    break
            except Exception:
                pass
        if df is not None:
            break

    if df is None:
        raise RuntimeError("Impossible de lire le CSV pour la conversion Parquet.")

    df.to_parquet(PARQUET_PATH, index=False)
    print(f"[OK] Parquet créé : {PARQUET_PATH}")


def _clean_df(df):
    """Nettoyage, renommage, conversions — appliqué une seule fois."""

    # Nettoyage colonnes
    df.columns = (
        df.columns.astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    rename_map = {
        "Auteurs FR":           "Auteurs_FR",
        "Auteurs copubliants":  "Auteurs_copubliants",
        "Organisme copubliant": "Organisme_copubliant",
        "UE/Non UE":            "UE/Non_UE",
        "ID Aurehal":           "ID_Aurehal",
        "Ann\u00e9e":           "Année",
        "Domaines consolid\u00e9s": "Domaines consolidés",
    }
    df = df.rename(columns=rename_map)

    # Nettoyage valeurs texte
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip()

    # Latitude / Longitude
    for col in ["Latitude", "Longitude"]:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace(",", ".", regex=False)
                .replace({"": None, "nan": None, "None": None})
            )

    # Conversions numériques
    for col in ["Année", "Latitude", "Longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Harmonisation centres
    if "Centre" in df.columns:
        df["Centre"] = df["Centre"].astype(str).str.strip()
        centre_map = {
            "Inria Saclay IPP":                          "Inria Saclay",
            "Inria Saclay UPS":                          "Inria Saclay",
            "Inria Saclay - Île-de-France":              "Inria Saclay",
            "Inria Saclay Ile-de-France":                "Inria Saclay",
            "Inria Paris Sorbonne":                      "Inria Paris",
            "Inria Paris - Sorbonne":                    "Inria Paris",
            "Inria Sorbonne":                            "Inria Paris",
            "Inria de Paris":                            "Inria Paris",
            "CRI Paris":                                 "Inria Paris",
            "Inria Bordeaux - Sud-Ouest":                "Inria Univ. Bordeaux",
            "Inria Bordeaux Sud-Ouest":                  "Inria Univ. Bordeaux",
            "Inria Bordeaux":                            "Inria Univ. Bordeaux",
            "Bordeaux":                                  "Inria Univ. Bordeaux",
            "Inria Grenoble - Rhône-Alpes":              "Inria Univ. Grenoble",
            "Inria Grenoble Rhône-Alpes":                "Inria Univ. Grenoble",
            "Inria Grenoble":                            "Inria Univ. Grenoble",
            "Grenoble":                                  "Inria Univ. Grenoble",
            "Inria Rennes - Bretagne Atlantique":        "Inria Univ. Rennes",
            "Inria Rennes Bretagne Atlantique":          "Inria Univ. Rennes",
            "Inria Rennes":                              "Inria Univ. Rennes",
            "Rennes":                                    "Inria Univ. Rennes",
            "Inria Nancy - Grand Est":                   "Inria Univ. Lorraine",
            "Inria Nancy Grand Est":                     "Inria Univ. Lorraine",
            "Inria Nancy":                               "Inria Univ. Lorraine",
            "Nancy":                                     "Inria Univ. Lorraine",
            "Grand Est":                                 "Inria Univ. Lorraine",
            "Inria Lille - Nord Europe":                 "Inria Lille",
            "Inria Lille Nord Europe":                   "Inria Lille",
            "Lille":                                     "Inria Lille",
            "Inria Univ. Côte d'Azur":                  "Inria Univ. Cote Azur",
            "Inria Univ. Côte Azur":                    "Inria Univ. Cote Azur",
            "Inria Univ Cote Azur":                     "Inria Univ. Cote Azur",
            "Inria Sophia Antipolis":                    "Inria Univ. Cote Azur",
            "Inria Sophia Antipolis - Méditerranée":     "Inria Univ. Cote Azur",
            "Sophia Antipolis":                          "Inria Univ. Cote Azur",
            "Sophia":                                    "Inria Univ. Cote Azur",
            "Lyon":                                      "Inria Lyon",
            "Inria siège":                               "Inria Siege",
            "Inria Siège":                               "Inria Siege",
            "Inria siege":                               "Inria Siege",
        }
        df["Centre"] = df["Centre"].replace(centre_map)

    # Filtrage années
    if "Année" in df.columns:
        df = df[df["Année"].between(2017, 2026, inclusive="both")]

    # Optimisation mémoire : convertir les colonnes texte en "category"
    cat_cols = ["Centre", "Equipe", "Pays", "Ville",
                "Organisme_copubliant", "UE/Non_UE", "Domaines consolidés"]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df


def _build_aggregates(df):
    """
    Pré-calcule toutes les agrégations utilisées par les graphiques.
    Appelé une seule fois au chargement — les callbacks n'ont plus qu'à
    lire ces résultats pré-calculés.
    """
    agg = {}

    if "Année" in df.columns:
        agg["by_year"] = (
            df.groupby("Année", observed=True)
            .size()
            .reset_index(name="count")
        )

    if "Centre" in df.columns:
        agg["by_centre"] = (
            df.groupby("Centre", observed=True)
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

    if "Pays" in df.columns:
        agg["by_pays"] = (
            df.groupby("Pays", observed=True)
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

    if "Organisme_copubliant" in df.columns:
        agg["by_organisme"] = (
            df.groupby("Organisme_copubliant", observed=True)
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(50)  # Top 50 suffisant pour les graphiques
        )

    if "Centre" in df.columns and "Année" in df.columns:
        agg["by_centre_year"] = (
            df.groupby(["Centre", "Année"], observed=True)
            .size()
            .reset_index(name="count")
        )

    if "Pays" in df.columns and "Année" in df.columns:
        agg["by_pays_year"] = (
            df.groupby(["Pays", "Année"], observed=True)
            .size()
            .reset_index(name="count")
        )

    # Listes de valeurs uniques pour les filtres (dropdowns)
    agg["unique_centres"]   = sorted(df["Centre"].dropna().unique().tolist()) if "Centre" in df.columns else []
    agg["unique_equipes"]   = sorted(df["Equipe"].dropna().unique().tolist()) if "Equipe" in df.columns else []
    agg["unique_pays"]      = sorted(df["Pays"].dropna().unique().tolist()) if "Pays" in df.columns else []
    agg["unique_villes"]    = sorted(df["Ville"].dropna().unique().tolist()) if "Ville" in df.columns else []
    agg["unique_organismes"]= sorted(df["Organisme_copubliant"].dropna().unique().tolist()) if "Organisme_copubliant" in df.columns else []
    agg["unique_annees"]    = sorted(df["Année"].dropna().astype(int).unique().tolist()) if "Année" in df.columns else []

    return agg


def load_data():
    """
    Retourne le DataFrame depuis le cache.
    Si le cache est vide (premier appel), charge et nettoie les données
    puis les garde en mémoire pour tous les appels suivants.
    """
    if _CACHE["df"] is not None:
        print("[CACHE] Données déjà en mémoire — retour immédiat.")
        return _CACHE["df"]

    print("[INIT] Premier chargement des données...")

    # Créer le CSV si besoin
    create_csv_from_xlsx(force=False)

    # Convertir en Parquet si besoin
    _build_parquet()

    # Lire depuis Parquet (rapide) ou CSV (fallback)
    if PARQUET_PATH.exists():
        print("[INFO] Lecture depuis Parquet...")
        df = pd.read_parquet(PARQUET_PATH)
    else:
        print("[INFO] Lecture depuis CSV (fallback)...")
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", sep=",",
                         engine="python", on_bad_lines="skip", dtype=str)

    # Nettoyage
    df = _clean_df(df)

    # Pré-agrégations
    _CACHE["aggregates"] = _build_aggregates(df)

    # Mise en cache
    _CACHE["df"] = df

    print(f"[OK] {len(df)} lignes chargées et mises en cache.")
    return df


def get_aggregates():
    """
    Retourne les agrégations pré-calculées.
    Appelle load_data() si nécessaire.
    """
    if _CACHE["aggregates"] is None:
        load_data()
    return _CACHE["aggregates"]


def filter_df(df, centres, equipes, pays, villes, organismes, annees):
    """
    Filtre le DataFrame selon les sélections utilisateur.
    Utilise les colonnes 'category' pour un filtrage ultra-rapide.
    """
    dff = df

    if centres and "Centre" in dff.columns:
        dff = dff[dff["Centre"].isin(centres)]
    if equipes and "Equipe" in dff.columns:
        dff = dff[dff["Equipe"].isin(equipes)]
    if pays and "Pays" in dff.columns:
        dff = dff[dff["Pays"].isin(pays)]
    if villes and "Ville" in dff.columns:
        dff = dff[dff["Ville"].isin(villes)]
    if organismes and "Organisme_copubliant" in dff.columns:
        dff = dff[dff["Organisme_copubliant"].isin(organismes)]
    if annees and "Année" in dff.columns:
        dff = dff[dff["Année"].isin(annees)]

    return dff


# ─────────────────────────────────────────────
# Test direct
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import time
    t0 = time.time()
    df = load_data()
    print(f"Premier chargement : {time.time() - t0:.2f}s")

    t1 = time.time()
    df2 = load_data()
    print(f"Deuxième appel (cache) : {time.time() - t1:.4f}s")

    agg = get_aggregates()
    print("Agrégations disponibles :", list(agg.keys()))
    print("Lignes :", len(df))