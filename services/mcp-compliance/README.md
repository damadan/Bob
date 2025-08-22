# mcp-compliance

Mock building code compliance service exposing separate checks for fire code, egress and structural spans.

## Endpoints
- `POST /mcp/compliance/check_fire_code`
- `POST /mcp/compliance/check_egress`
- `POST /mcp/compliance/check_structural_spans`

Service listens on **8081** and returns a JSON body with an `issues` list for each call.
