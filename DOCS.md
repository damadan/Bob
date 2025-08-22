# AEC Copilot Documentation

## 1. Introduction

AEC Copilot is a modular platform aimed at helping architects and engineers analyse drawings, generate bills of materials, check compliance and estimate environmental impact. The product consists of several FastAPI microservices that can be deployed independently or together.

The project currently implements the **mcp-material** service for material takeoff and pricing. The orchestrator and other services are in development but are documented here for planning and integration purposes.

## 2. Architecture Overview

```
+--------------+        +-----------------+        +----------------+        +-------------+
|  Orchestrator|<-----> | mcp-material    |<-----> | mcp-compliance |<-----> |  mcp-lca    |
+--------------+        +-----------------+        +----------------+        +-------------+
        ^                        ^                          ^                       ^
        |                        |                          |                       |
        |                        |                          |                       |
   Static UI              Data storage                Rules engine            LCA factors
        |                        |                          |                       |
        +---------------------> Observability (Prometheus/Grafana) <---------------+
```

Each service exposes a REST API and publishes Prometheus metrics. The Orchestrator coordinates calls between services and provides a UI for interactive runs.

## 3. Service Reference

### 3.1 mcp-material
Material extraction, pricing and export.

**Endpoints**

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET`  | `/health` | Service health check |
| `POST` | `/ingest/upload` | Upload project files |
| `GET`  | `/download/{project}/{kind}/{path}` | Download previously uploaded or generated files |
| `POST` | `/mcp/material/parse_drawing` | Parse PDF/IFC drawings into raw specs |
| `POST` | `/mcp/material/extract_bom` | Build a normalized bill of materials |
| `POST` | `/mcp/material/price_bom` | Apply a regional pricebook |
| `POST` | `/mcp/material/suggest_substitutions` | Suggest alternative items for gaps |
| `POST` | `/mcp/material/export/excel` | Save a priced BOM as XLSX |
| `POST` | `/mcp/material/export/json` | Save a priced BOM as JSON |
| `POST` | `/mcp/material/report/pdf` | Generate a PDF report |
| `GET`  | `/metrics` | Prometheus metrics |
| `GET`  | `/quality` | JSON dump of current metrics |

**Request/Response Schemas**

Schemas are defined under `app/schemas`. For example `ParseDrawingRequest` expects a `file_uri` string and returns `ParseDrawingResponse` with extracted specs.

**curl examples**

Upload a file:
```bash
curl -X POST "http://localhost:8080/ingest/upload?project_id=demo" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/drawing.pdf"
```

Parse an uploaded drawing:
```bash
curl -X POST "http://localhost:8080/mcp/material/parse_drawing" \
     -H "Content-Type: application/json" \
     -d '{"file_uri": "resource://project/demo/files/drawing.pdf"}'
```

Price a BOM:
```bash
curl -X POST "http://localhost:8080/mcp/material/price_bom" \
     -H "Content-Type: application/json" \
     -d '{"bom": {"items": []}, "region": "EU-Central"}'
```

Export priced BOM to PDF:
```bash
curl -X POST "http://localhost:8080/mcp/material/report/pdf" \
     -H "Content-Type: application/json" \
     -o report.pdf \
     -d '{"project_id":"demo", "priced_bom":{"items":[], "subtotal":0, "currency":"EUR"}}'
```

**Observability endpoints**

- `/metrics` exposes Prometheus formatted metrics.
- `/quality` returns the same metrics in JSON for debugging.

**Known limitations**

- Semantic catalog matching falls back to fuzzy search when embedding models are missing.
- Parsing supports PDF and IFC only; DWG is not yet implemented.

### 3.2 Orchestrator
A LangGraph-based agent that sequences calls to downstream services and provides a minimal chat UI.

**Endpoints**

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/run` | Execute a workflow defined in the request body |
| `POST` | `/run_multipart` | Same as `/run` but accepts file uploads |
| `POST` | `/chat` | Interactive chat endpoint used by the UI |
| `GET`  | `/` | Serves static HTML/JS UI |

**curl example**

```bash
curl -X POST "http://localhost:8090/run" \
     -H "Content-Type: application/json" \
     -d '{"steps":[{"tool":"parse_drawing","args":{"file_uri":"resource://project/demo/files/drawing.pdf"}}]}'
```

```bash
curl -X POST "http://localhost:8090/run_multipart" \
     -F "file=@/path/to/drawing.pdf"
```
The orchestrator also provides a chat interface via `/chat`.

### 3.3 mcp-compliance
Mock code-compliance checks using simplified rule sets.

**Endpoints**

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/mcp/compliance/check_fire_code` | Run fire code checks |
| `POST` | `/mcp/compliance/check_egress` | Validate egress requirements |
| `POST` | `/mcp/compliance/check_structural_spans` | Evaluate structural spans |

Each call returns a JSON body with an `issues` array.

**curl example**

```bash
curl -X POST "http://localhost:8081/mcp/compliance/check_fire_code" \
     -H "Content-Type: application/json" \
     -d '{"bom":{"items":[]}}'
```

### 3.4 mcp-lca
Lifecycle assessment estimation service.

**Endpoints**

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/mcp/lca/estimate` | Compute upfront carbon for a BOM |
| `POST` | `/mcp/lca/compare` | Compare two material options |

**curl example**

```bash
curl -X POST "http://localhost:8082/mcp/lca/estimate" \
     -H "Content-Type: application/json" \
     -d '{"bom":{"items":[]}}'
```

**Status**: Uses mock emission factors; integration with real EPD data is on the roadmap.

## 4. Observability & Monitoring

All services expose a `/metrics` endpoint compatible with Prometheus and a `/quality` endpoint with a JSON snapshot of the same metrics. Deployments typically include a Prometheus instance scraping each service and Grafana dashboards for latency, error rates and coverage ratios. The metric `pricing_coverage_ratio` tracks priced items vs total items and feeds quality dashboards.

## 5. Security

- **API key**: if `API_KEY` is set, requests must include `x-api-key` or `Authorization: Bearer <key>`.
- **Body size limit**: requests larger than `MAX_REQUEST_BODY_MB` (default 20 MB) are rejected with `413`.
- **File whitelist**: uploads and parse operations accept only `.pdf`, `.ifc` or `.dwg` extensions.
- **Timeouts**: middleware aborts requests taking more than `REQUEST_TIMEOUT_SECONDS` (default 30s).
- **Rate limiting**: simple in-process limiter allows `RATE_LIMIT_RPS` requests per second.
- **Security headers**: responses include `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` and a strict `Content-Security-Policy`.

## 6. Deployment Guide

### Development

1. Install dependencies and start the material service:
   ```bash
   cd services/mcp-material
   pip install -r requirements-core.txt
   pip install -r requirements-extras.txt
   make dev
   ```
2. For a quick start with Docker:
   ```bash
   docker compose up --build
   ```

### Production

Production deployments use `deploy/docker-compose.prod.yml` which defines the following stack introduced at **Step 7**:

- Nginx reverse proxy with security headers routing to individual services.
- mcp-material, orchestrator, mcp-compliance and mcp-lca containers.
- Prometheus scraping `/metrics` from mcp-material and the nginx exporter.
- Grafana pre-provisioned with Prometheus and a starter dashboard.

Sample invocation:
```bash
docker compose -f deploy/docker-compose.prod.yml --env-file .env.prod up -d
```

Configuration is supplied via `.env.prod` files passed to each service.

## 7. Testing & Evaluation

Unit tests are implemented with `pytest`. Quality metrics such as pricing coverage are evaluated using curated datasets. The evaluation pipeline currently exists only for **mcp-material**.

To run tests for the material service:
```bash
cd services/mcp-material
pytest
```

## 8. Roadmap

- Expand catalog coverage and improve semantic mapping.
- Replace mock compliance rules with real building norms.
- Integrate real Environmental Product Declaration datasets for LCA.
- Add subcontractor RFQ workflows and cost benchmarking.

## 9. Glossary

- **BOM** – Bill of Materials, a list of items with quantities.
- **EPD** – Environmental Product Declaration, certified environmental impact data.
- **LCA** – Life Cycle Assessment, estimating carbon and other impacts.
- **RPS** – Requests per second.
- **RFQ** – Request for Quotation.

