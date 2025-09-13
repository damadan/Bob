.PHONY: lint test

lint:
	ruff check src tests
	black --check src tests

test:
	pytest
