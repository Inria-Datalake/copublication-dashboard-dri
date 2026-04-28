"""
patch_callbacks.py
------------------
Corrige le bug MemoryError dans callbacks.py en ajoutant observed=True
a tous les groupby() qui ne l'ont pas encore.

Usage :
    python patch_callbacks.py
depuis le dossier dashboard/
"""
import re, shutil, sys
from pathlib import Path

TARGET = Path(__file__).parent / "callbacks.py"

if not TARGET.exists():
    print(f"ERREUR : fichier non trouve : {TARGET}")
    sys.exit(1)

# Sauvegarde
backup = TARGET.with_suffix(".py.bak")
shutil.copy2(TARGET, backup)
print(f"Sauvegarde : {backup}")

content = TARGET.read_text(encoding="utf-8")
original = content

# --- Correction 1 : ajouter observed=True aux groupby sans observed ---
def add_observed(m):
    inside = m.group(1)
    if "observed=" in inside:
        return m.group(0)
    return f".groupby({inside}, observed=True)"

content = re.sub(r"\.groupby\(([^)]+)\)", add_observed, content)

# --- Correction 2 : reparer "Domaine(s, observed=True)" si deja patch partiel ---
content = content.replace(
    '.groupby(["Centre", "Domaine(s, observed=True)"])',
    '.groupby(["Centre", "Domaine(s)"], observed=True)',
)
content = content.replace(
    ".groupby([\"Centre\", \"Domaine(s, observed=True)\"])",
    ".groupby([\"Centre\", \"Domaine(s)\"], observed=True)",
)
content = content.replace(
    '.groupby("Domaine(s, observed=True)")',
    '.groupby("Domaine(s)", observed=True)',
)

if content == original:
    print("Aucun changement necessaire (deja patche).")
else:
    TARGET.write_text(content, encoding="utf-8")
    n = content.count("observed=True") - original.count("observed=True")
    print(f"OK : {n} groupby() corriges avec observed=True")

# --- Verification syntaxe ---
import ast
try:
    ast.parse(content)
    print("Syntaxe Python : OK")
except SyntaxError as e:
    print(f"ERREUR de syntaxe ligne {e.lineno}: {e.msg}")
    print("Restauration de la sauvegarde...")
    shutil.copy2(backup, TARGET)
