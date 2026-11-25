#!/bin/zsh
# Sample data for trying the sports portal on your own computer.
#   zsh scripts/sample_data.sh load    – make sample_sports.db with the sample events (once)
#   zsh scripts/sample_data.sh serve   – run the site on it at http://localhost:5001
#   zsh scripts/sample_data.sh reset   – delete sample_sports.db and load it again
# Its own database file; mail, WhatsApp and AI are off; nothing reaches the live site.
REPO=${0:A:h:h}
cd "$REPO" || exit 1
PY="$REPO/.venv/bin/python"
[[ -x $PY ]] || { echo "Make the virtual environment first: python3.11 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt"; exit 1; }
export LOCAL_SQLITE_PATH="$REPO/sample_sports.db"
export DATABASE_URL= CLOUD_SQL_INSTANCE= MASTER_SECRET_KEY=
export MAIL_USER= MAIL_PASS= MAIL_FROM= BREVO_API_KEY= TWILIO_ACCOUNT_SID= TWILIO_AUTH_TOKEN= TWILIO_WHATSAPP_FROM=
export GEMINI_API_KEY= ANTHROPIC_API_KEY= BASE_URL=http://localhost:5001 FLASK_ENV=development PORT=5001 STORAGE_TYPE=local
case $1 in
  load)  exec "$PY" scripts/sample_data.py ;;
  reset) rm -f "$REPO/sample_sports.db"; exec "$PY" scripts/sample_data.py ;;
  serve) exec "$PY" app.py ;;
  *)     echo "Use: zsh scripts/sample_data.sh load | serve | reset"; exit 1 ;;
esac
