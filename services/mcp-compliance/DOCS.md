# mcp-compliance API

## Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| POST | `/mcp/compliance/check_fire_code` | Run fire code rules |
| POST | `/mcp/compliance/check_egress` | Check egress requirements |
| POST | `/mcp/compliance/check_structural_spans` | Validate structural spans |

Each endpoint expects a body containing a `bom` object and responds with an `issues` array.
