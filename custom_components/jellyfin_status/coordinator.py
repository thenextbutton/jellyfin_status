import aiohttp
import async_timeout
import logging
from datetime import datetime
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class JellyfinCoordinator(DataUpdateCoordinator):
    """Handles polling and session data retrieval for Jellyfin Status."""

    def __init__(self, hass, entry, api_key, address, update_interval, use_https=False, ignore_ssl=False):
        self.api_key = api_key
        self.address = address  # Format: "host:port"
        self.use_https = use_https
        self.ignore_ssl = ignore_ssl
        self.last_updated = None
        self.debug_payloads = entry.options.get("debug_payloads", False) if entry else False

        connector = aiohttp.TCPConnector(verify_ssl=not ignore_ssl)
        self.session = aiohttp.ClientSession(connector=connector)

        super().__init__(
            hass,
            _LOGGER,
            name="Jellyfin Status",
            update_interval=update_interval,
            update_method=self._async_update_data
        )

        # Log polling activation at startup
        _LOGGER.info("JellyfinCoordinator initialized — polling every %s", update_interval)

    async def _async_update_data(self):
        """Fetches active Jellyfin sessions via REST API."""
        protocol = "https" if self.use_https else "http"
        url = f"{protocol}://{self.address}/Sessions?api_key={self.api_key}"

        _LOGGER.debug("Polling Jellyfin → %s (SSL verify: %s)", url, not self.ignore_ssl)

        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url) as resp:
                    data = await resp.json()
                    self.last_updated = datetime.now().isoformat()
                    _LOGGER.debug("Data refreshed at %s", self.last_updated)
                    if self.debug_payloads: _LOGGER.debug("Session payload → %s", data)
                    
                    # Capture server version
                    self.application_version = next(
                        (session.get("ApplicationVersion") for session in data if "ApplicationVersion" in session),
                        None
                    )

                    server_name = self.config_entry.title if self.config_entry else self.address
                    _LOGGER.debug("🔍 Jellyfin %s (%s) version detected: %s", server_name, self.address, self.application_version)

                    
                    return data
        except Exception as err:
            _LOGGER.error("Data update failed — %s", err)
            raise UpdateFailed(f"Error fetching Jellyfin data: {err}")

    async def async_close(self):
        """Closes HTTP session on unload."""
        await self.session.close()
        _LOGGER.info("JellyfinCoordinator session closed")
