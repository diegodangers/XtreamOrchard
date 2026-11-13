# XtreamOrchard

Private, self-hosted IPTV project for one Onn Google TV device and Home Assistant Green.

## Scope
- Xtream Codes provider (authorized account)
- Provider EPG in phase one
- One shared channel lineup
- Local-only management
- Automatic configuration synchronization (planned)
- Native Home Assistant integration (planned)

## Status: development scaffold only
A FastAPI + SQLite prototype implements a mock channel catalog, default-hidden imports, per-channel visibility, and versioned visible-channel snapshots. It does **not** connect to an Xtream provider or play streams. The Android TV app, web management console, HA integration, HA app image, EPG, and synchronization are not implemented yet.

## Local backend test
```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt httpx pytest
XTREAM_ORCHARD_DB=/tmp/xtream-orchard-dev.db uvicorn app.main:app --reload --port 8099
```

API docs: http://localhost:8099/docs

## Security
The prototype has **no API authentication**. Do not expose it to your network or install it on Home Assistant Green until secure authentication, device pairing, and app packaging are implemented.

## Milestone 1
1. Authentication, schema migrations, credential storage, Xtream adapter.
2. Home Assistant app packaging and ingress.
3. Web channel manager, bulk selection and custom groups.
4. Google TV Kotlin player and device pairing.
5. Automatic synchronization and recovery.
6. Native Home Assistant integration and end-to-end tests.
