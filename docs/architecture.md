# Architecture (planned)

- **Backend:** FastAPI + SQLite on Home Assistant Green, packaged as an HA app.
- **Management UI:** React, served through Home Assistant ingress.
- **Native HA integration:** HACS-installable custom component; IPTV-specific entities/actions.
- **TV client:** Kotlin, Compose for TV, Media3 ExoPlayer.
- **Xtream:** Provider API for authorized channel catalog and provider EPG.
- **Sync:** Versioned configuration snapshots, WebSocket change notifications, local cache.
- **Streaming:** Direct from provider to TV, not proxied through Home Assistant.

Only the mock channel API is implemented so far. No production deployment or credentials until API authentication and device pairing are implemented.
