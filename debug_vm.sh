#!/bin/bash
# debug_vm.sh — Diagnostic et forçage de mise à jour sur la VM
# Usage : bash debug_vm.sh

echo ""
echo "══════════════════════════════════════════════"
echo "  DIAGNOSTIC DASHBOARD COPUBLICATIONS INRIA"
echo "══════════════════════════════════════════════"
echo ""

# ── 1. Répertoire du projet ───────────────────────────────────
PROJECT_DIR=$(find /home /srv /opt /var/www -name "app.py" 2>/dev/null | grep -i copublic | head -1 | xargs dirname)
if [ -z "$PROJECT_DIR" ]; then
    PROJECT_DIR=$(find /home /srv /opt -name "callbacks.py" 2>/dev/null | head -1 | xargs dirname)
fi

if [ -z "$PROJECT_DIR" ]; then
    echo "[ERREUR] Impossible de trouver le répertoire du projet."
    echo "         Cherchez manuellement avec : find / -name 'app.py' 2>/dev/null"
    exit 1
fi

echo "[INFO] Projet trouvé : $PROJECT_DIR"
cd "$PROJECT_DIR"

# ── 2. Dernier commit local ───────────────────────────────────
echo ""
echo "--- Git local ---"
git log --oneline -5

echo ""
echo "--- Git remote (origin/main) ---"
git fetch origin 2>/dev/null
git log --oneline origin/main -5

# ── 3. Diff entre local et remote ────────────────────────────
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null)
echo ""
if [ "$BEHIND" -gt 0 ] 2>/dev/null; then
    echo "[ATTENTION] La VM est EN RETARD de $BEHIND commit(s) par rapport à origin/main"
    echo "            Lancement du pull..."
    git pull origin main
    echo "[OK] Pull effectué"
else
    echo "[OK] La VM est à jour avec origin/main"
fi

# ── 4. Hash du callbacks.py local vs attendu ─────────────────
echo ""
echo "--- Vérification observed=True dans callbacks.py ---"
COUNT=$(grep -c "observed=True" "$PROJECT_DIR/callbacks.py" 2>/dev/null || echo 0)
echo "    observed=True présent : $COUNT fois (attendu : ≥ 20)"
if [ "$COUNT" -lt 20 ]; then
    echo "    [ALERTE] Le callbacks.py sur la VM ne contient pas le correctif !"
    echo "             Il faut re-pusher depuis Windows et re-puller ici."
else
    echo "    [OK] Le correctif groupby est bien en place"
fi

# ── 5. Trouver et redémarrer le process ──────────────────────
echo ""
echo "--- Processus Python en cours ---"
ps aux | grep -E "gunicorn|app\.py|uvicorn" | grep -v grep

echo ""
echo "--- Tentative de redémarrage ---"

# Gunicorn (le plus courant en prod)
if command -v systemctl &>/dev/null; then
    SERVICE=$(systemctl list-units --type=service --state=running 2>/dev/null \
              | grep -iE "copublic|datalake|dashboard|gunicorn|inria" \
              | awk '{print $1}' | head -1)
    if [ -n "$SERVICE" ]; then
        echo "    Service systemd trouvé : $SERVICE"
        sudo systemctl restart "$SERVICE"
        sleep 3
        STATUS=$(systemctl is-active "$SERVICE")
        echo "    Statut après restart : $STATUS"
    else
        echo "    Aucun service systemd identifié."
        echo "    Services actifs :"
        systemctl list-units --type=service --state=running 2>/dev/null | grep -v "\.scope" | tail -20
    fi
fi

# Docker
if command -v docker &>/dev/null; then
    CONTAINER=$(docker ps --format "{{.Names}}" 2>/dev/null \
                | grep -iE "copublic|datalake|dashboard|inria" | head -1)
    if [ -n "$CONTAINER" ]; then
        echo "    Conteneur Docker trouvé : $CONTAINER"
        docker restart "$CONTAINER"
        echo "    [OK] Conteneur redémarré"
    fi
fi

echo ""
echo "══════════════════════════════════════════════"
echo "  FIN DU DIAGNOSTIC"
echo "══════════════════════════════════════════════"
echo ""
echo "Si rien n'a changé sur le site, lancez manuellement :"
echo "  sudo systemctl restart <nom-du-service>"
echo "  ou : docker restart <nom-du-conteneur>"
echo ""
