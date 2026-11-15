# Development security

All management API endpoints require a bearer token from `XTREAM_ORCHARD_ADMIN_TOKEN`. The health endpoint is unauthenticated. No default token is provided; without one, management endpoints reject all requests.

Provider settings are read from environment variables: `XTREAM_ORCHARD_PROVIDER_URL`, `XTREAM_ORCHARD_PROVIDER_USERNAME`, `XTREAM_ORCHARD_PROVIDER_PASSWORD`. The application does not store provider credentials in SQLite. **Do not commit .env files or credentials.**

The refresh endpoint retrieves the live catalog using the configured server URL. The URL must be controlled by an administrator. Provider URLs are not yet protected against DNS rebinding or SSRF and provider requests use Xtream's query-string credentials, which may be logged by upstream infrastructure. Use TLS wherever supported.

This is **not production ready**: the management bearer token has no per-device scope or rotation, no rate limiting, and no TLS termination. Home Assistant ingress, secure secret management, TV pairing and deployment hardening are still pending. Do not expose this API to a home network or the internet.
