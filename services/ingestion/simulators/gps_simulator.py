#!/usr/bin/env python3
"""
GPS Event Simulator

Generates realistic GPS telemetry events for buses and sends them to the ingestion webhook.
"""

import argparse
import asyncio
import logging
import random
from datetime import datetime, timezone

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GPSSimulator:
    """Simulates GPS events for a fleet of buses."""

    def __init__(
        self,
        webhook_url: str,
        num_buses: int = 5,
        interval: float = 2.0,
        batch_mode: bool = False,
    ):
        self.webhook_url = webhook_url
        self.num_buses = num_buses
        self.interval = interval
        self.batch_mode = batch_mode

        self.fleet_numbers = [f"BUS-{i:03d}" for i in range(1, num_buses + 1)]

        self.bus_positions = {
            fleet_num: {
                "lat": 37.7749 + random.uniform(-0.05, 0.05),
                "lon": -122.4194 + random.uniform(-0.05, 0.05),
                "heading": random.randint(0, 359),
            }
            for fleet_num in self.fleet_numbers
        }

    def generate_gps_event(self, fleet_number: str) -> dict:
        """Generate a single GPS event for a bus."""
        position = self.bus_positions[fleet_number]

        lat_delta = random.uniform(-0.001, 0.001) * (random.random() * 10)
        lon_delta = random.uniform(-0.001, 0.001) * (random.random() * 10)

        position["lat"] += lat_delta
        position["lon"] += lon_delta
        position["heading"] = (position["heading"] + random.randint(-10, 10)) % 360

        position["lat"] = max(37.7, min(37.85, position["lat"]))
        position["lon"] = max(-122.5, min(-122.35, position["lon"]))

        event = {
            "fleet_number": fleet_number,
            "latitude": round(position["lat"], 6),
            "longitude": round(position["lon"], 6),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "speed_kph": round(random.uniform(0, 60), 1),
            "heading": position["heading"],
            "passenger_load": random.randint(0, 40),
        }

        return event

    async def send_event(self, event: dict, client: httpx.AsyncClient) -> bool:
        """Send a single GPS event to the webhook."""
        try:
            response = await client.post(self.webhook_url, json=event)
            if response.status_code in (200, 202):
                logger.info(
                    f"Sent GPS event for {event['fleet_number']} at "
                    f"({event['latitude']}, {event['longitude']})"
                )
                return True
            else:
                logger.error(
                    f"Failed to send event: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error sending GPS event: {e}")
            return False

    async def send_batch(self, events: list[dict], client: httpx.AsyncClient) -> bool:
        """Send a batch of GPS events to the webhook."""
        try:
            batch_url = self.webhook_url.replace("/events", "/events/batch")
            response = await client.post(batch_url, json=events)
            if response.status_code in (200, 202):
                logger.info(f"Sent batch of {len(events)} GPS events")
                return True
            else:
                logger.error(
                    f"Failed to send batch: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error sending GPS batch: {e}")
            return False

    async def run(self, duration: int | None = None):
        """
        Run the GPS simulator.

        Args:
            duration: Number of seconds to run (None = run indefinitely)
        """
        logger.info(
            f"Starting GPS simulator for {self.num_buses} buses "
            f"(interval: {self.interval}s, batch_mode: {self.batch_mode})"
        )

        start_time = asyncio.get_event_loop().time()
        iteration = 0

        async with httpx.AsyncClient(timeout=10.0) as client:
            while True:
                iteration += 1
                events = [
                    self.generate_gps_event(fleet_num) for fleet_num in self.fleet_numbers
                ]

                if self.batch_mode:
                    await self.send_batch(events, client)
                else:
                    await asyncio.gather(*[self.send_event(event, client) for event in events])

                if duration and (asyncio.get_event_loop().time() - start_time) >= duration:
                    logger.info(f"Simulator completed after {iteration} iterations")
                    break

                await asyncio.sleep(self.interval)


def main():
    parser = argparse.ArgumentParser(description="GPS Event Simulator")
    parser.add_argument(
        "--webhook-url",
        default="http://localhost:8002/api/v1/gps/events",
        help="Ingestion webhook URL",
    )
    parser.add_argument(
        "--num-buses", type=int, default=5, help="Number of buses to simulate"
    )
    parser.add_argument(
        "--interval", type=float, default=2.0, help="Interval between events (seconds)"
    )
    parser.add_argument(
        "--duration", type=int, default=None, help="Duration to run (seconds, default: infinite)"
    )
    parser.add_argument(
        "--batch", action="store_true", help="Send events in batches instead of individually"
    )

    args = parser.parse_args()

    simulator = GPSSimulator(
        webhook_url=args.webhook_url,
        num_buses=args.num_buses,
        interval=args.interval,
        batch_mode=args.batch,
    )

    try:
        asyncio.run(simulator.run(duration=args.duration))
    except KeyboardInterrupt:
        logger.info("Simulator stopped by user")


if __name__ == "__main__":
    main()
