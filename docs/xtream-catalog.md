# Xtream catalog adapter

The adapter in `server/app/xtream.py` supports credential verification, live categories, and live stream catalog retrieval. It is not yet wired to persistent credentials or the public API.

## Security gates before deployment
- Authenticate every management endpoint and pair each TV with a scoped token.
- Encrypt or otherwise securely protect provider secrets at rest.
- Validate and constrain provider URLs to prevent server-side request forgery; account for DNS rebinding, private address exceptions, and redirects.
- Ensure logs, HTTP errors and traces do not reveal credentials in query strings.
- Use TLS to protect Xtream credentials in transit wherever the provider supports it.
- Implement provider-specific rate limiting and refresh scheduling.
- Preserve visibility across catalog refreshes; handle provider stream-ID churn.

Never deploy the current unauthenticated API to the home network.
