from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from .coordinator import JellyfinCoordinator
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    def get_opt(key, default=None):
        return entry.options.get(key) or entry.data.get(key, default)

    host = get_opt("host")
    port = get_opt("port")
    api_key = get_opt("api_key")
    scan_interval = get_opt("scan_interval", 30)
    use_https = get_opt("use_https", False)
    ignore_ssl = get_opt("ignore_ssl", False)

    update_interval = None if scan_interval == 0 else timedelta(seconds=scan_interval)

    coordinator = JellyfinCoordinator(
        hass,
        api_key=api_key,
        address=f"{host}:{port}",
        update_interval=update_interval,
        use_https=use_https,
        ignore_ssl=ignore_ssl
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    coordinator._schedule_refresh()
    
    async def handle_refresh(call):
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "refresh", handle_refresh)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.async_close()
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])

async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
    return True
