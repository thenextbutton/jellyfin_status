from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import aiohttp
import async_timeout
import logging
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

class JellyfinCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api_key, address, update_interval, use_https=False, ignore_ssl=False):
        self.api_key = api_key
        self.address = address  # Format: "host:port"
        self.use_https = use_https
        self.ignore_ssl = ignore_ssl

        connector = aiohttp.TCPConnector(verify_ssl=not ignore_ssl)
        self.session = aiohttp.ClientSession(connector=connector)

        super().__init__(
            hass,
            _LOGGER,
            name="Jellyfin Status",
            update_interval=update_interval,
            update_method=self._async_update_data
        )

    async def _async_update_data(self):
        """Fetches active Jellyfin sessions via REST."""
        protocol = "https" if self.use_https else "http"
        url = f"{protocol}://{self.address}/Sessions?api_key={self.api_key}"

        _LOGGER.debug("Connection → %s (SSL verify: %s)", url, not self.ignore_ssl)

        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url) as resp:
                    data = await resp.json()
                    self.last_updated = datetime.now().isoformat()
                    _LOGGER.info("Coordinator refreshed data at %s", self.last_updated)
                    _LOGGER.debug("Raw session data: %s", data)
                    return data
        except Exception as err:
            _LOGGER.error("Update failed — %s", err)
            raise UpdateFailed(f"Error fetching Jellyfin data: {err}")

    async def async_close(self):
        """Closes the aiohttp session when unloading the integration."""
        await self.session.close()
