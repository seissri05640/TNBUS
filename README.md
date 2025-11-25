# Traffic Services API

Bootstrap backend service powered by [FastAPI](https://fastapi.tiangolo.com/) that will host future
traffic data features. The service lives under `services/api` and is packaged with [Poetry](https://python-poetry.org/),
Docker, typed settings, and placeholder tests.

## Getting started

### Prerequisites
- Python 3.11+
- [Poetry 1.8+](https://python-poetry.org/docs/#installation)
- Docker (optional, for containerized runs)

### Installation & development commands

All helper commands are defined at the repository root:

| Command | Description |
| --- | --- |
| `make install` | Install API dependencies with Poetry |
| `make lint` | Run Ruff lint checks over the API code and tests |
| `make test` | Execute the FastAPI test suite via pytest |
| `make run` | Start the FastAPI development server with live reload |
| `make docker-build` | Build the API Docker image |
| `make docker-run` | Run the previously built Docker image, exposing port 8000 |

### Running locally
1. Install dependencies: `make install`
2. Start the server: `make run`
3. Open `http://localhost:8000/health` or `/version` to exercise the foundational endpoints.

### Docker workflow
```sh
make docker-build IMAGE_NAME=traffic-api
make docker-run IMAGE_NAME=traffic-api
```
The container listens on port `8000` by default.

### Configuration
Environment variables prefixed with `API_` control runtime behavior (see `services/api/.env.example`).

## Project layout

```
services/
  api/
    app/
      core/        # settings & logging
      routers/     # FastAPI routers (health, version)
      schemas/     # Pydantic response models
      services/    # domain/service layer helpers
    tests/         # pytest-based health + version checks
    Dockerfile     # production container image
    pyproject.toml # Poetry project + dependency metadata
```
