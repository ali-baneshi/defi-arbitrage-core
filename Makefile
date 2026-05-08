PYTHON ?= python

.PHONY: validate validate-rust test lint docker-build docker-validate

validate:
	PYTHONPATH=src $(PYTHON) scripts/validate_all.py

validate-rust:
	PYTHONPATH=src $(PYTHON) scripts/validate_all.py --include-rust

test:
	pytest

lint:
	ruff check .

docker-build:
	docker build -t defi-arbitrage-core:local .

docker-validate:
	docker run --rm --entrypoint python defi-arbitrage-core:local scripts/validate_all.py
