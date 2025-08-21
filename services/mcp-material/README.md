# MCP Material Service

Сервис для извлечения спецификаций материалов из чертежей и расчёта стоимости.

## Возможности

- `GET /health` — проверка состояния сервиса.
- `POST /mcp/material/parse_drawing` — конвертация PDF или IFC в список позиций.
- `POST /mcp/material/extract_bom` — формирование нормализованной спецификации (заглушка).
- `POST /mcp/material/price_bom` — оценка стоимости спецификации (заглушка).
- `POST /mcp/material/suggest_substitutions` — подбор альтернатив (заглушка).

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
  "bom":{"items":[{"name":"\u0411\u0435\u0442\u043e\u043d C25/30","unit":"m3","qty":12.5,"code":"MAT-001"}]},
  "region":"EU-Central"
}'
