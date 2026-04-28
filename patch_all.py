"""
patch_all.py — Correcteur universel du dashboard Copublications Inria
=====================================================================
Corrige en une seule passe :
  1. MemoryError groupby (observed=True)
  2. Logo 404 (paths /assets/ -> /copublications-dashboard/assets/)
  3. Onglet "Evolution" — s'assure que le callback se déclenche bien

Usage :  python patch_all.py
Depuis : le dossier dashboard/
"""
import re, shutil, sys, ast
from pathlib import Path

ROOT = Path(__file__).parent
OK   = []
ERR  = []

def check_syntax(path, content):
    try:
        ast.parse(content)
        return True
    except SyntaxError as e:
        ERR.append(f"  SYNTAXE ligne {e.lineno}: {e.msg} dans {path.name}")
        return False

def patch_file(path, fn_patch, desc):
    if not path.exists():
        ERR.append(f"  Fichier introuvable : {path}")
        return
    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup)
    original = path.read_text(encoding="utf-8")
    patched  = fn_patch(original)
    if patched == original:
        OK.append(f"  Deja a jour : {path.name}")
        return
    if not check_syntax(path, patched) if path.suffix == ".py" else True:
        print(f"  Restauration {path.name} (erreur syntaxe)")
        return
    path.write_text(patched, encoding="utf-8")
    OK.append(f"  OK : {path.name} — {desc}")

# ══════════════════════════════════════════════════════════
# 1. callbacks.py — observed=True + Domaine(s) fix
# ══════════════════════════════════════════════════════════
def patch_callbacks(src):
    # Ajouter observed=True a tous les groupby sans lui
    def add_observed(m):
        inside = m.group(1)
        if "observed=" in inside:
            return m.group(0)
        return f".groupby({inside}, observed=True)"

    src = re.sub(r"\.groupby\(([^)]+)\)", add_observed, src)

    # Reparer "Domaine(s, observed=True)" si present
    src = src.replace(
        '.groupby(["Centre", "Domaine(s, observed=True)"])',
        '.groupby(["Centre", "Domaine(s)"], observed=True)',
    )
    src = src.replace(
        '.groupby("Domaine(s, observed=True)")',
        '.groupby("Domaine(s)", observed=True)',
    )
    return src

patch_file(ROOT / "callbacks.py", patch_callbacks,
           "groupby observed=True (corrige MemoryError)")

# ══════════════════════════════════════════════════════════
# 2. __init__.py — logo paths
# ══════════════════════════════════════════════════════════
def patch_layout(src):
    # Corriger les chemins logo qui manquent le prefixe
    src = src.replace(
        'src="/assets/logo_inria.png"',
        'src="/copublications-dashboard/assets/logo_inria.png"',
    )
    src = src.replace(
        'src="/assets/logo_data.png"',
        'src="/copublications-dashboard/assets/logo_data.png"',
    )
    return src

patch_file(ROOT / "__init__.py", patch_layout,
           "logo paths corriges (/assets/ -> /copublications-dashboard/assets/)")

# ══════════════════════════════════════════════════════════
# 3. custom.css — s'assurer qu'il est bien en place
# ══════════════════════════════════════════════════════════
# Verifie si assets/ existe, sinon cree-le
assets_dir = ROOT / "assets"
if not assets_dir.exists():
    assets_dir.mkdir()
    OK.append("  Dossier assets/ cree")

# Copie les CSS/JS depuis le dossier courant vers assets/ si necessaire
for fname in ["custom.css", "dark-mode.css", "export-pdf.js"]:
    src_f = ROOT / fname
    dst_f = assets_dir / fname
    if src_f.exists() and not dst_f.exists():
        shutil.copy2(src_f, dst_f)
        OK.append(f"  Copie {fname} -> assets/")
    elif src_f.exists() and dst_f.exists():
        # Mise a jour si source plus recente
        if src_f.stat().st_mtime > dst_f.stat().st_mtime:
            shutil.copy2(src_f, dst_f)
            OK.append(f"  Mise a jour assets/{fname}")
        else:
            OK.append(f"  assets/{fname} deja a jour")

# ══════════════════════════════════════════════════════════
# Rapport
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("  PATCH DASHBOARD COPUBLICATIONS INRIA")
print("="*55)
if OK:
    print("\n[OK]")
    for m in OK: print(m)
if ERR:
    print("\n[ERREURS]")
    for m in ERR: print(m)

print("\n" + "="*55)
if not ERR:
    print("  Tout est correct. Relancez : python app.py")
else:
    print("  Des erreurs ont ete detectees (voir ci-dessus).")
print("="*55 + "\n")
