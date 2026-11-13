# Management console preview

The FastAPI server serves a lightweight channel manager at `/`. It supports:
- Search by channel name/category.
- Select filtered channels and bulk show/hide.
- Refresh from a configured Xtream provider.
- Visible/hidden channel counts.

The frontend holds the administrator bearer token in page memory, not localStorage. This is a **development-only** design. Production Home Assistant ingress authentication and TV pairing still need implementation.

The Home Assistant app files are an **unvalidated packaging draft**. The build context must be the repository root (the Dockerfile copies `server/` and `homeassistant/`). No user should install the app until the security and build checks pass.

The UI does not yet support group editing, channel ordering, or EPG mapping.
