# Changelog

## Unreleased
- add security middleware (API key, body/file limits, rate limit, timeout)
- implement upload/download endpoints with path safety
- persist exports under project outputs
- add tests for security, ingest/download, semantic fallback
- document environment variables
- make ``numpy`` optional in catalog to avoid import errors when embeddings are
  unavailable
- ensure oversized requests return 413 before hitting rate limits
