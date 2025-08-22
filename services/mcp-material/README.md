# MCP Material Service

Сервис для извлечения спецификаций материалов из чертежей и расчёта стоимости.

## Endpoints

- `GET /health` – сервис доступен.
- `GET /metrics` – метрики Prometheus.
- `GET /quality` – снимок внутренних метрик.
- `POST /mcp/material/parse_drawing` – преобразование PDF/IFC в сырые позиции.
- `POST /mcp/material/extract_bom` – нормализация спецификации.
- `POST /mcp/material/price_bom` – применение прайс‑листа.
- `POST /mcp/material/suggest_substitutions` – подбор альтернатив.
- `POST /mcp/material/export/json` – экспорт сметы в JSON.
- `POST /mcp/material/export/excel` – экспорт сметы в XLSX.
- `POST /mcp/material/report/pdf` – PDF отчёт.
- `POST /ingest/upload` – загрузка файлов проекта.
- `GET /download/<project>/<kind>/<file>` – скачивание файлов.

## URI ресурсов

Сервис использует схему `resource://` для доступа к данным. Поддерживаются варианты:

- `resource://project/<id>/files/<path>` — файлы проекта из каталога `DATA_ROOT`.
- `resource://pricebook/<region>` — прайс‑лист региона из каталога `RESOURCES_ROOT`.
- `resource://catalog/materials` — общий каталог материалов.

## Локальный запуск

### Установка зависимостей

```bash
pip install -r requirements-core.txt
pip install -r requirements-extras.txt
```

### Запуск

```bash
make dev      # режим разработки
make run      # запуск без автоперезапуска
```

### Docker

```bash
docker compose up --build
```

## Тестирование

```bash
pytest -q
```

## Переменные окружения

| Name | Description | Default |
| ---- | ----------- | ------- |
| `API_KEY` | API ключ для защищённых эндпоинтов | `None` |
| `MAX_REQUEST_BODY_MB` | максимальный размер тела запроса | `20` |
| `MAX_FILE_SIZE_MB` | максимальный размер загружаемого файла | `50` |
| `ALLOWED_EXTS` | разрешённые расширения для загрузки (через запятую) | `.pdf,.ifc,.dwg` |
| `REQUEST_TIMEOUT_SECONDS` | таймаут обработки запроса | `30.0` |
| `RATE_LIMIT_RPS` | глобальное ограничение RPS | `5.0` |

## Step 3: Pricing
Endpoints:
- POST /mcp/material/price_bom
- POST /mcp/material/suggest_substitutions

Run:
pip install -r requirements-core.txt
pytest -q
uvicorn app.main:app --host 0.0.0.0 --port 8080

Example:
curl -s http://localhost:8080/mcp/material/price_bom -X POST -H "Content-Type: application/json" -d '{
  "bom":{"items":[{"name":"Бетон C25/30","unit":"m3","qty":12.5,"code":"MAT-001"}]},
  "region":"EU-Central"
}'
