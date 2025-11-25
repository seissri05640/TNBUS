#!/usr/bin/env python3
"""
Traffic API Mock Server

Provides a mock external traffic API endpoint that returns simulated traffic data.
"""

import argparse
import logging
import random
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Mock Traffic API", version="1.0.0")


@app.get("/traffic")
async def get_traffic_data():
    """
    Mock endpoint that returns simulated traffic data.
    """
    congestion_index = random.randint(20, 90)
    incident_count = random.randint(0, 5)

    base_speed = 50.0
    speed_factor = 1.0 - (congestion_index / 150.0)
    average_speed = round(base_speed * speed_factor, 1)

    traffic_data = {
        "source": "mock_traffic_api",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "congestion_index": congestion_index,
        "incident_count": incident_count,
        "average_speed_kph": average_speed,
        "payload": {
            "region": "downtown",
            "weather": random.choice(["clear", "cloudy", "rain", "fog"]),
            "time_of_day": datetime.now(timezone.utc).strftime("%H:%M"),
            "road_conditions": random.choice(["good", "fair", "poor"]),
        },
    }

    logger.info(
        f"Serving traffic data: congestion={congestion_index}, "
        f"incidents={incident_count}, speed={average_speed}kph"
    )

    return traffic_data


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mock_traffic_api"}


def main():
    parser = argparse.ArgumentParser(description="Mock Traffic API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    args = parser.parse_args()

    logger.info(f"Starting Mock Traffic API on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
