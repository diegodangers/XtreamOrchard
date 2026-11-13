#!/bin/sh
set -eu
export XTREAM_ORCHARD_DB=/data/xtream_orchard.db
# The administrator token must be supplied by the app configuration.
if [ -z "${XTREAM_ORCHARD_ADMIN_TOKEN:-}" ]; then
  echo "Missing XTREAM_ORCHARD_ADMIN_TOKEN; refusing to start" >&2
  exit 1
fi
exec /opt/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8099 --proxy-headers=false
