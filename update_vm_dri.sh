#!/usr/bin/env bash

set -e

APP_DIR="$HOME/apps/copublication-dashboard-dri"
VENV="$APP_DIR/.venv/bin/activate"
PORT="8051"
LOG="$APP_DIR/dash-dri.log"

echo "=== Mise à jour du dashboard DRI ==="

cd "$APP_DIR"

echo "[1/5] Activation du venv..."
source "$VENV"

echo "[2/5] Installation des dépendances..."
pip install -r requirements.txt
pip install openpyxl gunicorn gevent pyarrow

echo "[3/5] Arrêt du Gunicorn DRI uniquement..."
PIDS=$(pgrep -f "$APP_DIR/.venv/bin/gunicorn app:server --bind 127.0.0.1:$PORT" || true)

if [ -n "$PIDS" ]; then
    kill $PIDS
    sleep 2
fi

echo "[4/5] Démarrage du Gunicorn DRI..."
nohup "$APP_DIR/.venv/bin/gunicorn" app:server \
    --bind 127.0.0.1:$PORT \
    --workers 2 \
    --worker-class gevent \
    --timeout 120 \
    --preload \
    > "$LOG" 2>&1 &

sleep 2

echo "[5/5] Vérification..."
for i in {1..30}; do
    if curl -fsS -I "http://127.0.0.1:$PORT/copublication-dashboard-dri/" > /dev/null; then
        echo "=== Dashboard DRI OK sur le port $PORT ==="
        exit 0
    fi
    sleep 2
done

echo "=== ERREUR : le dashboard DRI ne répond pas après 60 secondes ==="
exit 1

