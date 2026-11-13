# Home Assistant management console (development preview)

The Home Assistant app directory is self-contained and builds from its own Docker context. It includes a snapshot of the backend source and requirements. The CI workflow checks that bundled sources remain in sync with `server/`.

## Configuration
In the app's Configuration tab, supply a **random administrator token of at least 32 characters** and the Xtream provider URL, username, and password. Credentials are read from the Home Assistant app's options file at startup. Never commit credentials.

The app exposes the management console through Home Assistant ingress, with **no host port mapping**. The browser also requires the administrator bearer token, held in page memory only. Provider credentials are never sent to the browser.

## Current limitations
- No tested installation or image build yet.
- Provider URLs are not hardened against SSRF or DNS rebinding.
- Home Assistant options are not a dedicated encrypted secrets vault.
- No channel groups, ordering, EPG mapping, TV pairing, or automatic sync yet.
- The console currently uses a per-channel sequential bulk visibility API, not a transactional batch endpoint.
- Provider URLs using HTTP transmit credentials without TLS. Prefer HTTPS providers.

**Do not install until CI and security validation pass.**

## Home Assistant repository layout

Home Assistant app discovery expects `repository.yaml` at the repository root and the app in `xtream_orchard/`. The root-level app is now the canonical package. The older `homeassistant/` directory is retained temporarily for migration and should not be used for installation.

CI builds `xtream_orchard/` directly and checks the canonical backend source files against the bundled app copy.

## First installation gate

Do not install solely based on Docker success. The first installation must validate Home Assistant repository discovery, the ingress route, authentication, options persistence, and rollback. The developer must also resolve the provider URL/DNS rebinding risk before exposing live credentials.
