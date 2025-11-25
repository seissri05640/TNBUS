SHELL := /bin/bash
POETRY ?= poetry
API_DIR := services/api
INGESTION_DIR := services/ingestion
IMAGE_NAME ?= traffic-api

.PHONY: install
install:
    cd $(API_DIR) && $(POETRY) install

.PHONY: install-ingestion
install-ingestion:
    cd $(INGESTION_DIR) && $(POETRY) install

.PHONY: install-all
install-all: install install-ingestion

.PHONY: lint
lint:
    cd $(API_DIR) && $(POETRY) run ruff check app tests

.PHONY: lint-ingestion
lint-ingestion:
    cd $(INGESTION_DIR) && $(POETRY) run ruff check app tests

.PHONY: lint-all
lint-all: lint lint-ingestion

.PHONY: test
test:
    cd $(API_DIR) && $(POETRY) run pytest

.PHONY: test-ingestion
test-ingestion:
    cd $(INGESTION_DIR) && $(POETRY) run pytest

.PHONY: test-all
test-all: test test-ingestion

.PHONY: run
run:
    cd $(API_DIR) && $(POETRY) run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: run-ingestion
run-ingestion:
    cd $(INGESTION_DIR) && $(POETRY) run uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

.PHONY: run-ingestion-worker
run-ingestion-worker:
    cd $(INGESTION_DIR) && $(POETRY) run celery -A celeryconfig.celery_app worker --loglevel=info

.PHONY: run-ingestion-beat
run-ingestion-beat:
    cd $(INGESTION_DIR) && $(POETRY) run celery -A celeryconfig.celery_app beat --loglevel=info

.PHONY: run-gps-simulator
run-gps-simulator:
    cd $(INGESTION_DIR) && $(POETRY) run python simulators/gps_simulator.py

.PHONY: run-traffic-mock
run-traffic-mock:
    cd $(INGESTION_DIR) && $(POETRY) run python simulators/traffic_api_mock.py

.PHONY: db-upgrade
db-upgrade:
    cd $(API_DIR) && $(POETRY) run alembic upgrade head

.PHONY: db-seed
db-seed:
    cd $(API_DIR) && $(POETRY) run python scripts/seed_data.py

.PHONY: docker-build
docker-build:
    docker build -f $(API_DIR)/Dockerfile -t $(IMAGE_NAME) .

.PHONY: docker-run
docker-run:
    docker run --rm -p 8000:8000 $(IMAGE_NAME)

.PHONY: docker-build-ingestion
docker-build-ingestion:
    docker build -f $(INGESTION_DIR)/Dockerfile -t traffic-ingestion $(INGESTION_DIR)

.PHONY: docker-run-ingestion
docker-run-ingestion:
    docker run --rm -p 8002:8002 traffic-ingestion
