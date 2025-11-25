import logging
from typing import Any

import httpx

from ..core.config import get_settings
from ..schemas.traffic import TrafficData

logger = logging.getLogger(__name__)


class TrafficAPIAdapter:
    """Adapter for fetching and transforming data from external traffic APIs."""

    def __init__(self, api_url: str | None = None, api_key: str | None = None):
        settings = get_settings()
        self.api_url = api_url or settings.traffic_api_url
        self.api_key = api_key or settings.traffic_api_key
        self.timeout = 30.0

    async def fetch_traffic_data(self) -> TrafficData | None:
        """
        Fetch current traffic data from the external API.
        Returns None if the request fails or data is invalid.
        """
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Fetching traffic data from {self.api_url}")
                response = await client.get(self.api_url, headers=headers)
                response.raise_for_status()

                data = response.json()
                return self._transform_response(data)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching traffic data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching traffic data: {e}")
            return None

    def _transform_response(self, raw_data: dict[str, Any]) -> TrafficData:
        """
        Transform the raw API response into a TrafficData schema.
        This method can be customized for different API formats.
        """
        return TrafficData(
            source=raw_data.get("source", "external_api"),
            captured_at=raw_data.get("captured_at"),
            congestion_index=raw_data.get("congestion_index"),
            incident_count=raw_data.get("incident_count"),
            average_speed_kph=raw_data.get("average_speed_kph"),
            payload=raw_data.get("payload"),
        )
