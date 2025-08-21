# Bob

Это продукт для оптимизации работы архитектора.

## Структура репозитория

- `services/mcp-material` — сервис извлечения спецификаций материалов и расчёта их стоимости.

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
