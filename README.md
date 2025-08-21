# Bob

Это продукт для оптимизации работы архитектора.

## Структура репозитория

- `services/mcp-material` — сервис извлечения спецификаций материалов и расчёта их стоимости.

## Реализовано

На данный момент в сервисе `mcp-material` доступны следующие возможности:

- `GET /health` — проверка состояния сервиса.
- `POST /mcp/material/parse_drawing` — преобразование PDF/IFC в список позиций.
- `POST /mcp/material/extract_bom` — формирование нормализованной спецификации: объединение таблиц, автоматическое распознавание заголовков, нормализация единиц и суммирование количеств.
- `POST /mcp/material/price_bom` — расчёт стоимости спецификации по региональному прайс‑листу.
- `POST /mcp/material/suggest_substitutions` — подбор альтернативных материалов.

## Быстрый старт

Перейдите в каталог сервиса и установите зависимости:

```bash
cd services/mcp-material
pip install -r requirements-core.txt
pip install -r requirements-extras.txt
```

Запуск приложения в режиме разработки:

```bash
make dev
```

Запуск через Docker Compose:

```bash
docker compose up --build
```

## Тестирование

```bash
cd services/mcp-material
pytest -q
```
