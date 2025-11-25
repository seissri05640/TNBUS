SHELL := /bin/bash
POETRY ?= poetry
API_DIR := services/api
IMAGE_NAME ?= traffic-api

.PHONY: install
install:
	cd $(API_DIR) && $(POETRY) install

.PHONY: lint
lint:
	cd $(API_DIR) && $(POETRY) run ruff check app tests

.PHONY: test
test:
	cd $(API_DIR) && $(POETRY) run pytest

.PHONY: run
run:
	cd $(API_DIR) && $(POETRY) run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: docker-build
docker-build:
	docker build -f $(API_DIR)/Dockerfile -t $(IMAGE_NAME) .

.PHONY: docker-run
docker-run:
	docker run --rm -p 8000:8000 $(IMAGE_NAME)
