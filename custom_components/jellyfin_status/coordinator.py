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
        self.library_counts = {}  # Initialize empty dictionary
        self.application_version = None
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
        base_url = f"{protocol}://{self.address}"
        sessions_url = f"{base_url}/Sessions?api_key={self.api_key}"
        counts_url = f"{base_url}/Items/Counts?api_key={self.api_key}"

        _LOGGER.debug("Polling Jellyfin sessions and counts (SSL verify: %s)", not self.ignore_ssl)

        try:
            async with async_timeout.timeout(10):
                # Fetch Active Sessions
                async with self.session.get(sessions_url) as resp:
                    session_data = await resp.json()
                
                # Fetch Library Counts
                async with self.session.get(counts_url) as resp:
                    self.library_counts = await resp.json()

                # Update timestamp
                self.last_updated = datetime.now().isoformat()
                
                if self.debug_payloads: 
                    _LOGGER.debug("Session payload → %s", session_data)
                    _LOGGER.debug("Counts payload → %s", self.library_counts)

                # Capture server version (Keep previous version if current list is empty)
                self.application_version = next(
                    (s.get("ApplicationVersion") for s in session_data if s.get("ApplicationVersion")),
                    self.application_version
                )

                return session_data

        except Exception as err:
            _LOGGER.error("Jellyfin update failed: %s", err)
            raise UpdateFailed(f"Error communicating with Jellyfin: {err}")

    async def async_close(self):
        """Closes HTTP session on unload."""
        await self.session.close()
        _LOGGER.info("JellyfinCoordinator session closed")
