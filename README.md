# Traffic Services Platform

A microservices platform for traffic data collection, processing, and analysis. The platform consists of:

- **API Service** (`services/api`): FastAPI backend for querying traffic data and predictions
- **Ingestion Service** (`services/ingestion`): Data collection pipeline for GPS events and external traffic APIs

Both services are powered by [FastAPI](https://fastapi.tiangolo.com/) and packaged with [Poetry](https://python-poetry.org/),
Docker, typed settings, and comprehensive tests.

## Getting started

### Prerequisites
- Python 3.11+
- [Poetry 1.8+](https://python-poetry.org/docs/#installation)
- PostgreSQL (for data persistence)
- Redis (for ingestion service task queue)
- Docker (optional, for containerized runs)

### Installation & development commands

All helper commands are defined at the repository root:

#### API Service
| Command | Description |
| --- | --- |
| `make install` | Install API dependencies with Poetry |
| `make lint` | Run Ruff lint checks over the API code and tests |
| `make test` | Execute the API test suite via pytest |
| `make run` | Start the API development server with live reload (port 8000) |
| `make docker-build` | Build the API Docker image |
| `make docker-run` | Run the previously built Docker image, exposing port 8000 |

#### Ingestion Service
| Command | Description |
| --- | --- |
| `make install-ingestion` | Install ingestion service dependencies |
| `make lint-ingestion` | Run Ruff lint checks over ingestion code |
| `make test-ingestion` | Execute the ingestion test suite |
| `make run-ingestion` | Start the ingestion web service (port 8002) |
| `make run-ingestion-worker` | Start the Celery worker for background tasks |
| `make run-ingestion-beat` | Start the Celery beat scheduler |
| `make run-gps-simulator` | Run the GPS event simulator |
| `make run-traffic-mock` | Run the mock traffic API server |
| `make docker-build-ingestion` | Build the ingestion Docker image |
| `make docker-run-ingestion` | Run the ingestion container |

#### Combined
| Command | Description |
| --- | --- |
| `make install-all` | Install dependencies for both services |
| `make lint-all` | Run lint checks on both services |
| `make test-all` | Execute all test suites |

#### Database
| Command | Description |
| --- | --- |
| `make db-upgrade` | Apply the latest Alembic migrations to the configured database |
| `make db-seed` | Populate the database with representative sample data |

### Running locally

#### API Service
1. Install dependencies: `make install`
2. Set up the database: `make db-upgrade && make db-seed`
3. Start the server: `make run`
4. Open `http://localhost:8000/health` or `/version` to exercise the foundational endpoints.

#### Ingestion Service
See the [Ingestion Service README](services/ingestion/README.md) for comprehensive setup and usage instructions.

Quick start:
1. Install dependencies: `make install-ingestion`
2. Ensure Redis is running: `docker run -d --name redis -p 6379:6379 redis:7-alpine`
3. Start the ingestion service: `make run-ingestion` (Terminal 1)
4. Start the Celery worker: `make run-ingestion-worker` (Terminal 2)
5. Start the Celery beat scheduler: `make run-ingestion-beat` (Terminal 3)
6. Run simulators to generate data:
   - GPS simulator: `make run-gps-simulator` (Terminal 4)
   - Traffic API mock: `make run-traffic-mock` (Terminal 5)

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
      models/      # SQLAlchemy database models
      db/          # database session management
    tests/         # pytest-based health + version checks
    alembic/       # database migrations
    Dockerfile     # production container image
    pyproject.toml # Poetry project + dependency metadata
  
  ingestion/
    app/
      adapters/    # data source adapters (GPS, traffic API)
      core/        # configuration & logging
      db/          # database session management
      routers/     # FastAPI endpoints (webhooks, health)
      schemas/     # Pydantic validation models
      services/    # business logic (persistence, batching)
      tasks/       # Celery background tasks
    simulators/    # GPS and traffic data generators
    tests/         # pytest test suite
    celeryconfig.py # Celery configuration
    Dockerfile     # production container image
    pyproject.toml # Poetry project + dependency metadata
```

## Database schema & migrations

The service now persists operational data in Postgres via SQLAlchemy models and Alembic
migrations. The MVP entities support route lookup, telemetry history, and prediction
retrieval queries:

```
Route ──< Bus ──< TelemetryRecord
   \            \
    \            `── Prediction >── TrafficSnapshot
     `──────────────────────────────^
```

| Table | Purpose | Indexed / unique columns |
| --- | --- | --- |
| `routes` | Canonical definition of a bus route | `code` (unique) |
| `buses` | Individual fleet vehicles + operational status | `fleet_number` (unique), `route_id` |
| `telemetry_records` | Time-series GPS + ridership metrics per bus | (`bus_id`, `recorded_at`) composite index + unique constraint |
| `traffic_snapshots` | External congestion + incident observations | `captured_at` |
| `predictions` | ETA/headway forecasts derived from telemetry + traffic inputs | (`route_id`, `target_arrival`) index |

### Running migrations & seeds
1. Provision a Postgres database and update `services/api/.env` (copy from `.env.example`).
2. Install dependencies: `make install`.
3. Apply the schema: `make db-upgrade` (runs `alembic upgrade head`).
4. Load representative fixtures: `make db-seed`.

Alembic configuration lives under `services/api/alembic/` and the generated SQLAlchemy
models live in `services/api/app/models/`.

