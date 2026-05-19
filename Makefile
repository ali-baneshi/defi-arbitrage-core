PYTHON ?= python
PIP_INDEX_URL ?=
PIP_EXTRA_INDEX_URL ?=
PIP_FLAGS ?= --no-build-isolation

.PHONY: bootstrap validate validate-rust test lint docker-build docker-validate

bootstrap:
	$(PYTHON) -m venv .venv
	.venv/bin/python -m pip install -U pip setuptools wheel
	.venv/bin/python -m pip install -e '.[dev]' $(PIP_FLAGS) $(if $(PIP_INDEX_URL),--index-url $(PIP_INDEX_URL),) $(if $(PIP_EXTRA_INDEX_URL),--extra-index-url $(PIP_EXTRA_INDEX_URL),)

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
