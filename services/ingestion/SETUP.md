# Ingestion Service Setup Guide

This guide provides step-by-step instructions for setting up and testing the traffic data ingestion pipeline.

## Prerequisites

Before starting, ensure you have:

- Python 3.11 or higher
- Poetry 1.8 or higher
- PostgreSQL (can use Docker)
- Redis (can use Docker)
- A terminal or command prompt

## Quick Start with Docker

The fastest way to get everything running is using Docker Compose:

```bash
# From the repository root
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f ingestion
docker-compose logs -f ingestion-worker

# Stop all services
docker-compose down
```

This starts:
- PostgreSQL database
- Redis
- API service (port 8000)
- Ingestion web service (port 8002)
- Celery worker
- Celery beat scheduler
- Mock traffic API (port 8001)

## Manual Setup (Development)

### Step 1: Install Dependencies

```bash
cd services/ingestion
poetry install
```

### Step 2: Start Supporting Services

#### Option A: Docker

```bash
# PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_USER=traffic \
  -e POSTGRES_PASSWORD=traffic \
  -e POSTGRES_DB=traffic \
  -p 5432:5432 \
  postgres:15-alpine

# Redis
docker run -d --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

#### Option B: Local Installation

Install PostgreSQL and Redis using your system's package manager:

```bash
# Ubuntu/Debian
sudo apt-get install postgresql redis-server

# macOS
brew install postgresql redis
brew services start postgresql
brew services start redis
```

### Step 3: Set Up Database

```bash
# From repository root
make db-upgrade  # Apply migrations
make db-seed     # Load sample data (buses, routes, etc.)
```

### Step 4: Configure Environment (Optional)

Create `.env` file in `services/ingestion/` if you need custom settings:

```env
INGESTION_DATABASE_URL=postgresql+asyncpg://traffic:traffic@localhost:5432/traffic
INGESTION_REDIS_URL=redis://localhost:6379/0
INGESTION_CELERY_BROKER_URL=redis://localhost:6379/0
INGESTION_CELERY_RESULT_BACKEND=redis://localhost:6379/0
INGESTION_TRAFFIC_API_URL=http://localhost:8001/traffic
INGESTION_TRAFFIC_POLL_INTERVAL=300
INGESTION_GPS_BATCH_SIZE=50
INGESTION_GPS_BATCH_TIMEOUT=30
INGESTION_LOG_LEVEL=INFO
```

### Step 5: Start Services

Open 5 separate terminals:

#### Terminal 1: Ingestion Web Service

```bash
cd services/ingestion
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

Or use the Makefile:
```bash
make run-ingestion
```

#### Terminal 2: Celery Worker

```bash
cd services/ingestion
poetry run celery -A celeryconfig.celery_app worker --loglevel=info
```

Or:
```bash
make run-ingestion-worker
```

#### Terminal 3: Celery Beat Scheduler

```bash
cd services/ingestion
poetry run celery -A celeryconfig.celery_app beat --loglevel=info
```

Or:
```bash
make run-ingestion-beat
```

#### Terminal 4: Mock Traffic API

```bash
cd services/ingestion
poetry run python simulators/traffic_api_mock.py
```

Or:
```bash
make run-traffic-mock
```

#### Terminal 5: GPS Simulator

```bash
cd services/ingestion
poetry run python simulators/gps_simulator.py --num-buses 5 --interval 2
```

Or:
```bash
make run-gps-simulator
```

## Verifying the Setup

### 1. Check Service Health

```bash
# Ingestion service
curl http://localhost:8002/health
# Should return: {"status":"healthy","service":"ingestion"}

# Mock traffic API
curl http://localhost:8001/health
# Should return: {"status":"healthy","service":"mock_traffic_api"}
```

### 2. Manually Send GPS Event

```bash
curl -X POST http://localhost:8002/api/v1/gps/events \
  -H "Content-Type: application/json" \
  -d '{
    "fleet_number": "BUS-001",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "recorded_at": "2024-01-15T10:30:00Z",
    "speed_kph": 45.5,
    "heading": 180,
    "passenger_load": 25
  }'
```

Expected response:
```json
{
  "message": "GPS event received",
  "batch_status": "batched",
  "batch_count": 1
}
```

### 3. Check Traffic API Mock

```bash
curl http://localhost:8001/traffic
```

You should see simulated traffic data with random values.

### 4. Verify Database Records

Connect to PostgreSQL and check the data:

```bash
psql -U traffic -d traffic -h localhost
```

```sql
-- Check GPS telemetry records
SELECT COUNT(*) FROM telemetry_records;
SELECT * FROM telemetry_records ORDER BY recorded_at DESC LIMIT 5;

-- Check traffic snapshots
SELECT COUNT(*) FROM traffic_snapshots;
SELECT * FROM traffic_snapshots ORDER BY captured_at DESC LIMIT 5;

-- Check buses
SELECT * FROM buses;
```

### 5. Monitor Logs

Watch the logs in each terminal:

- **Ingestion service**: Should show incoming GPS events and batch operations
- **Celery worker**: Should show traffic polling tasks executing
- **Celery beat**: Should show scheduled tasks being triggered
- **GPS simulator**: Should show events being sent
- **Mock traffic API**: Should show API requests being served

## Testing Different Scenarios

### High-Volume GPS Events

Send many events quickly to test batching:

```bash
poetry run python simulators/gps_simulator.py --num-buses 20 --interval 0.5 --duration 60
```

### Batch Submission

Send multiple events in a single request:

```bash
curl -X POST http://localhost:8002/api/v1/gps/events/batch \
  -H "Content-Type: application/json" \
  -d '[
    {
      "fleet_number": "BUS-001",
      "latitude": 37.7749,
      "longitude": -122.4194,
      "recorded_at": "2024-01-15T10:30:00Z",
      "speed_kph": 45.5
    },
    {
      "fleet_number": "BUS-002",
      "latitude": 37.7849,
      "longitude": -122.4294,
      "recorded_at": "2024-01-15T10:30:05Z",
      "speed_kph": 38.2
    }
  ]'
```

### Manual Traffic Polling

Trigger the traffic polling task manually:

```bash
# In Python shell within the poetry environment
poetry run python

>>> from celeryconfig import celery_app
>>> result = celery_app.send_task('app.tasks.traffic_poller.poll_traffic_api')
>>> result.get(timeout=10)
```

## Troubleshooting

### GPS Events Not Persisting

**Problem**: Events are received but not appearing in the database.

**Solutions**:
1. Check that buses exist in the database:
   ```sql
   SELECT fleet_number FROM buses;
   ```
2. Ensure `fleet_number` in GPS events matches database records
3. Run `make db-seed` to create sample buses
4. Check ingestion service logs for errors

### Celery Tasks Not Running

**Problem**: Traffic polling not executing.

**Solutions**:
1. Verify Redis is running: `redis-cli ping`
2. Check Celery worker is connected to Redis
3. Ensure Celery beat scheduler is running
4. Review worker logs: `docker-compose logs ingestion-worker`

### Database Connection Errors

**Problem**: Cannot connect to PostgreSQL.

**Solutions**:
1. Verify PostgreSQL is running: `pg_isready -U traffic`
2. Check connection string in `.env` or environment variables
3. Ensure database exists: `psql -U traffic -l`
4. Verify credentials are correct

### Port Already in Use

**Problem**: `Address already in use` error.

**Solutions**:
1. Check what's using the port: `lsof -i :8002`
2. Kill the process or use a different port
3. Update the port in commands and configuration

## Performance Tuning

### Adjust Batch Size

Increase batch size for higher throughput:

```env
INGESTION_GPS_BATCH_SIZE=100
INGESTION_GPS_BATCH_TIMEOUT=10
```

### Scale Celery Workers

Run multiple workers for parallel processing:

```bash
# Worker 1
poetry run celery -A celeryconfig.celery_app worker --loglevel=info --concurrency=4

# Worker 2 (different terminal)
poetry run celery -A celeryconfig.celery_app worker --loglevel=info --concurrency=4
```

### Traffic Polling Frequency

Adjust polling interval (in seconds):

```env
INGESTION_TRAFFIC_POLL_INTERVAL=60  # Poll every minute
```

## Next Steps

- Integrate with real GPS tracking devices
- Connect to actual traffic data providers (TomTom, HERE, Google Maps)
- Add monitoring and alerting (Prometheus, Grafana)
- Implement data retention policies
- Set up automated backups
- Deploy to production (Kubernetes, Docker Swarm)

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Redis Documentation](https://redis.io/docs/)
