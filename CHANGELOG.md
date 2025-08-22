# Changelog

## Unreleased
- Add missing `httpx` dependency and gracefully fallback when embedding model
  is unavailable, allowing tests to run without network access.
- Handle missing `numpy` gracefully in material catalog and reorder security
  middleware to return HTTP 413 before rate limiting.
