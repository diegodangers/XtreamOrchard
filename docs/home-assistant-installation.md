# Home Assistant Green installation — pre-release checklist

**Do not install until the latest CI build succeeds and ingress behavior has been validated.**

## Repository layout
The Home Assistant app repository is rooted at `repository.yaml`; the app lives at `xtream_orchard/`. The older `homeassistant/` directory is retained temporarily during migration and is not the Home Assistant app repository root.

## Before a controlled test
1. Make a current Home Assistant backup.
2. Keep the GitHub repository private and ensure Home Assistant can access it (private GitHub repository URLs are not generally usable as public custom app repositories without an authenticated distribution method). A release/distribution method must be selected before installation.
3. Do not enter live provider credentials until the ingress and credential-handling security review is complete.
4. Verify the app's Configuration options and persistence with disposable test values.
5. Verify that the sidebar panel loads and its API requests stay under the ingress prefix.
6. Verify that unpaired devices cannot access the management API.

## Rollback
Stop and uninstall the test app. Its database resides in the app's /data storage. Preserve a backup before removing app data. Existing Home Assistant automations and integrations should not be modified by this app.

## Outstanding release blockers
- Private repository distribution for Home Assistant app installation
- End-to-end Home Assistant ingress authentication validation
- DNS resolution and rebinding protection for provider endpoints
- Provider credentials stored in Home Assistant options; secrets management review
- No Android TV device pairing or native Home Assistant integration yet
