#!/bin/sh
set -eu
export XTREAM_ORCHARD_DB=/data/xtream_orchard.db
CONFIG=/data/options.json
if [ ! -f "$CONFIG" ]; then
  echo "Missing Home Assistant app configuration" >&2
  exit 1
fi
export XTREAM_ORCHARD_ADMIN_TOKEN="$(jq -r '.admin_token // ""' "$CONFIG")"
export XTREAM_ORCHARD_PROVIDER_URL="$(jq -r '.provider_url // ""' "$CONFIG")"
export XTREAM_ORCHARD_PROVIDER_USERNAME="$(jq -r '.provider_username // ""' "$CONFIG")"
export XTREAM_ORCHARD_PROVIDER_PASSWORD="$(jq -r '.provider_password // ""' "$CONFIG")"
if [ "${#XTREAM_ORCHARD_ADMIN_TOKEN}" -lt 32 ]; then
  echo "Configure an admin token with at least 32 characters; refusing to start" >&2
  exit 1
fi
exec /opt/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8099 --no-proxy-headers
