#!/bin/bash
set -euo pipefail

PROJECT_DIR="/Users/azizmadhi/Apps/Social"
PYTHON="$PROJECT_DIR/venv/bin/python"

# Start server in background
"$PYTHON" "$PROJECT_DIR/ui_app.py" >/tmp/social_ui.log 2>&1 &
SERVER_PID=$!

# Give the server a moment to boot
sleep 1

# Open the browser
open "http://localhost:5050"

# Keep this terminal open and show logs
trap "kill $SERVER_PID" EXIT

if [ -f /tmp/social_ui.log ]; then
  tail -f /tmp/social_ui.log
else
  wait $SERVER_PID
fi
