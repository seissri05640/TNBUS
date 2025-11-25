# Traffic Data Ingestion Service

A modular data collection service that receives simulated real-time GPS events and polls external traffic APIs. The service validates, batches, and persists data into the traffic database.

## Features

- **GPS Event Ingestion**: Webhook endpoints to receive GPS telemetry events from buses
- **Traffic API Polling**: Background task that periodically fetches traffic data from external APIs
- **Data Validation**: Pydantic schemas validate all incoming data
- **Batching**: GPS events are batched for efficient database writes
- **Adapters**: Modular adapters for different data sources
- **Background Scheduler**: Celery with Redis for async tasks
- **Simulators**: Mock GPS and traffic data generators for testing

## Architecture

```
services/ingestion/
├── app/
│   ├── adapters/          # Data source adapters
│   │   ├── gps_adapter.py       # GPS event batching
│   │   └── traffic_adapter.py   # Traffic API client
│   ├── core/              # Configuration & logging
│   ├── db/                # Database session management
│   ├── routers/           # FastAPI endpoints
│   │   ├── health.py            # Health check endpoints
│   │   └── gps_webhook.py       # GPS event webhook
│   ├── schemas/           # Pydantic validation models
│   │   ├── gps.py               # GPS event schema
│   │   └── traffic.py           # Traffic data schema
│   ├── services/          # Business logic
│   │   └── persistence.py       # Database persistence
│   └── tasks/             # Celery background tasks
│       └── traffic_poller.py    # Traffic API polling
├── simulators/            # Data generators for testing
│   ├── gps_simulator.py         # GPS event generator
│   └── traffic_api_mock.py      # Mock traffic API server
└── tests/                 # Test suite
```

## Prerequisites

- Python 3.11+
- [Poetry 1.8+](https://python-poetry.org/docs/#installation)
- PostgreSQL (shared with API service)
- Redis (for Celery broker)

## Installation

1. **Install dependencies**:
   ```bash
   cd services/ingestion
   poetry install
   ```

2. **Set up environment variables** (optional, defaults work for local development):
   Create a `.env` file in `services/ingestion/`:
   ```env
   INGESTION_DATABASE_URL=postgresql+asyncpg://traffic:traffic@localhost:5432/traffic
   INGESTION_REDIS_URL=redis://localhost:6379/0
   INGESTION_CELERY_BROKER_URL=redis://localhost:6379/0
   INGESTION_CELERY_RESULT_BACKEND=redis://localhost:6379/0
   INGESTION_TRAFFIC_API_URL=http://localhost:8001/traffic
   INGESTION_TRAFFIC_API_KEY=
   INGESTION_TRAFFIC_POLL_INTERVAL=300
   INGESTION_GPS_BATCH_SIZE=50
   INGESTION_GPS_BATCH_TIMEOUT=30
   INGESTION_LOG_LEVEL=INFO
   INGESTION_DEBUG=false
   ```

## Running the Service

### 1. Start Redis (required for Celery)

```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or using your system package manager
# Ubuntu/Debian: sudo apt-get install redis-server
# macOS: brew install redis && brew services start redis
```

### 2. Ensure the database is set up

The ingestion service shares the database with the API service:

```bash
# From the repository root
make db-upgrade  # Run migrations
make db-seed     # Load sample data (buses, routes, etc.)
```

### 3. Start the ingestion web service

```bash
cd services/ingestion
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

The service will be available at `http://localhost:8002`

### 4. Start the Celery worker (for background tasks)

In a separate terminal:

```bash
cd services/ingestion
poetry run celery -A celeryconfig.celery_app worker --loglevel=info
```

### 5. Start the Celery beat scheduler (for periodic tasks)

In another terminal:

```bash
cd services/ingestion
poetry run celery -A celeryconfig.celery_app beat --loglevel=info
```

## Using the Simulators

### GPS Event Simulator

Generates and sends GPS telemetry events to the ingestion webhook:

```bash
cd services/ingestion
poetry run python simulators/gps_simulator.py --help

# Basic usage (5 buses, 2-second interval)
poetry run python simulators/gps_simulator.py

# Custom configuration
poetry run python simulators/gps_simulator.py \
  --webhook-url http://localhost:8002/api/v1/gps/events \
  --num-buses 10 \
  --interval 1.0 \
  --duration 60

# Batch mode (send multiple events per request)
poetry run python simulators/gps_simulator.py --batch --num-buses 10
```

**Options**:
- `--webhook-url`: Ingestion webhook URL (default: `http://localhost:8002/api/v1/gps/events`)
- `--num-buses`: Number of buses to simulate (default: 5)
- `--interval`: Seconds between event generations (default: 2.0)
- `--duration`: Total runtime in seconds (default: infinite, use Ctrl+C to stop)
- `--batch`: Send events in batches instead of individually

### Traffic API Mock Server

Provides a mock external traffic API that returns simulated data:

```bash
cd services/ingestion
poetry run python simulators/traffic_api_mock.py --help

# Start the mock server
poetry run python simulators/traffic_api_mock.py --port 8001

# Test the endpoint
curl http://localhost:8001/traffic
```

**Options**:
- `--host`: Host to bind to (default: `0.0.0.0`)
- `--port`: Port to bind to (default: 8001)

## API Endpoints

### Health & Version

- **GET** `/health` - Health check
- **GET** `/version` - Service version

### GPS Events

- **POST** `/api/v1/gps/events` - Receive a single GPS event
  ```json
  {
    "fleet_number": "BUS-001",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "recorded_at": "2024-01-15T10:30:00Z",
    "speed_kph": 45.5,
    "heading": 180,
    "passenger_load": 25
  }
  ```

- **POST** `/api/v1/gps/events/batch` - Receive multiple GPS events
  ```json
  [
    {
      "fleet_number": "BUS-001",
      "latitude": 37.7749,
      "longitude": -122.4194,
      "recorded_at": "2024-01-15T10:30:00Z",
      "speed_kph": 45.5,
      "heading": 180,
      "passenger_load": 25
    },
    ...
  ]
  ```

## Data Flow

### GPS Event Flow

1. **Reception**: GPS events arrive at `/api/v1/gps/events` webhook
2. **Validation**: Pydantic schema validates the event data
3. **Batching**: `GPSAdapter` accumulates events until batch size or timeout is reached
4. **Persistence**: Batch is written to `telemetry_records` table
5. **Response**: HTTP 202 Accepted returned to sender

### Traffic Data Flow

1. **Scheduling**: Celery beat triggers the polling task every N seconds (configurable)
2. **Fetching**: `TrafficAPIAdapter` calls the external traffic API
3. **Transformation**: Raw API response is transformed to `TrafficData` schema
4. **Validation**: Pydantic validates the transformed data
5. **Persistence**: Data is written to `traffic_snapshots` table

## Configuration Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `INGESTION_DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://traffic:traffic@localhost:5432/traffic` |
| `INGESTION_REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `INGESTION_CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/0` |
| `INGESTION_CELERY_RESULT_BACKEND` | Celery result backend URL | `redis://localhost:6379/0` |
| `INGESTION_TRAFFIC_API_URL` | External traffic API endpoint | `http://localhost:8001/traffic` |
| `INGESTION_TRAFFIC_API_KEY` | API key for traffic service | `` |
| `INGESTION_TRAFFIC_POLL_INTERVAL` | Polling interval (seconds) | `300` |
| `INGESTION_GPS_BATCH_SIZE` | GPS events per batch | `50` |
| `INGESTION_GPS_BATCH_TIMEOUT` | Max seconds before flushing batch | `30` |
| `INGESTION_LOG_LEVEL` | Logging level | `INFO` |
| `INGESTION_DEBUG` | Enable debug mode | `false` |

## Testing End-to-End

To verify the complete data flow:

1. **Start all services**:
   ```bash
   # Terminal 1: Redis
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   
   # Terminal 2: Mock Traffic API
   cd services/ingestion
   poetry run python simulators/traffic_api_mock.py
   
   # Terminal 3: Ingestion web service
   poetry run uvicorn app.main:app --port 8002 --reload
   
   # Terminal 4: Celery worker
   poetry run celery -A celeryconfig.celery_app worker --loglevel=info
   
   # Terminal 5: Celery beat scheduler
   poetry run celery -A celeryconfig.celery_app beat --loglevel=info
   
   # Terminal 6: GPS simulator
   poetry run python simulators/gps_simulator.py --num-buses 5 --interval 2
   ```

2. **Verify data in database**:
   ```sql
   -- Check GPS telemetry records
   SELECT COUNT(*) FROM telemetry_records;
   SELECT * FROM telemetry_records ORDER BY recorded_at DESC LIMIT 10;
   
   -- Check traffic snapshots
   SELECT COUNT(*) FROM traffic_snapshots;
   SELECT * FROM traffic_snapshots ORDER BY captured_at DESC LIMIT 10;
   ```

3. **Monitor logs**:
   - Watch the ingestion service logs for incoming GPS events
   - Check Celery worker logs for traffic polling activity
   - Verify batching behavior in the GPS adapter logs

## Troubleshooting

### GPS events not persisting

- Ensure buses exist in the database (run `make db-seed` from root)
- Check that fleet numbers in simulator match database records
- Verify database connection string in configuration

### Traffic polling not working

- Confirm Redis is running: `redis-cli ping` should return `PONG`
- Check Celery worker and beat are both running
- Verify mock traffic API is accessible: `curl http://localhost:8001/traffic`
- Review Celery worker logs for errors

### Connection errors

- PostgreSQL: Ensure the database is running and accessible
- Redis: Verify Redis is running on the configured port
- Check firewall rules if running across different hosts

## Development

### Running tests

```bash
cd services/ingestion
poetry run pytest
```

### Code formatting

```bash
poetry run ruff check app tests
```

## Docker Support

Coming soon: Dockerfile and docker-compose configuration for containerized deployment.
