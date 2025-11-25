#!/bin/bash
set -e

echo "================================================"
echo "Traffic Ingestion Service - Quick Start"
echo "================================================"
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."
echo

# Check Poetry
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}✗ Poetry not found${NC}"
    echo "Please install Poetry: https://python-poetry.org/docs/#installation"
    exit 1
else
    echo -e "${GREEN}✓ Poetry installed${NC}"
fi

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    echo -e "${YELLOW}⚠ Redis CLI not found - Redis may not be installed${NC}"
    echo "You can run Redis with Docker: docker run -d --name redis -p 6379:6379 redis:7-alpine"
else
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠ Redis is not running${NC}"
        echo "Start Redis or run: docker run -d --name redis -p 6379:6379 redis:7-alpine"
    fi
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠ PostgreSQL CLI not found${NC}"
    echo "You can run PostgreSQL with Docker:"
    echo "docker run -d --name postgres -e POSTGRES_USER=traffic -e POSTGRES_PASSWORD=traffic -e POSTGRES_DB=traffic -p 5432:5432 postgres:15-alpine"
else
    if PGPASSWORD=traffic psql -U traffic -h localhost -d traffic -c '\q' &> /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL is accessible${NC}"
    else
        echo -e "${YELLOW}⚠ PostgreSQL is not accessible${NC}"
        echo "Make sure PostgreSQL is running with the correct credentials"
    fi
fi

echo
echo "================================================"
echo "Installation"
echo "================================================"
echo

# Install dependencies
echo "Installing dependencies..."
poetry install

echo
echo -e "${GREEN}✓ Installation complete${NC}"
echo

echo "================================================"
echo "Starting Services"
echo "================================================"
echo
echo "To run the ingestion service, you need to start multiple components:"
echo
echo "1. Ingestion Web Service:"
echo "   poetry run uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"
echo
echo "2. Celery Worker:"
echo "   poetry run celery -A celeryconfig.celery_app worker --loglevel=info"
echo
echo "3. Celery Beat Scheduler:"
echo "   poetry run celery -A celeryconfig.celery_app beat --loglevel=info"
echo
echo "4. Mock Traffic API:"
echo "   poetry run python simulators/traffic_api_mock.py"
echo
echo "5. GPS Simulator (generates test data):"
echo "   poetry run python simulators/gps_simulator.py --num-buses 5 --interval 2"
echo
echo "================================================"
echo "Using Makefile (from repository root)"
echo "================================================"
echo
echo "  make run-ingestion           # Start web service"
echo "  make run-ingestion-worker    # Start Celery worker"
echo "  make run-ingestion-beat      # Start Celery beat"
echo "  make run-traffic-mock        # Start mock traffic API"
echo "  make run-gps-simulator       # Start GPS simulator"
echo
echo "================================================"
echo "Testing the Service"
echo "================================================"
echo
echo "Once running, test with:"
echo
echo "curl http://localhost:8002/health"
echo
echo "Send a GPS event:"
echo 'curl -X POST http://localhost:8002/api/v1/gps/events \\'
echo '  -H "Content-Type: application/json" \\'
echo '  -d '"'"'{"fleet_number":"BUS-001","latitude":37.7749,"longitude":-122.4194,"recorded_at":"2024-01-15T10:30:00Z"}'"'"
echo
echo "================================================"
echo "See SETUP.md for detailed instructions"
echo "================================================"
