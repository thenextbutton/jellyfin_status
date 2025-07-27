from datetime import timedelta
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED

from .coordinator import JellyfinCoordinator
from .const import DOMAIN
from .discovery import get_jellyfin_sensor_entity_ids

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    def get_opt(key, default=None):
        return entry.options.get(key, entry.data.get(key, default))

    host = get_opt("host")
    port = get_opt("port")
    api_key = get_opt("api_key")
    scan_interval = get_opt("scan_interval", 30)
    use_https = get_opt("use_https", False)
    ignore_ssl = get_opt("ignore_ssl", False)

    update_interval = None if scan_interval == 0 else timedelta(seconds=scan_interval)

    _LOGGER.info("🔧 Configured scan_interval: %s", scan_interval)
    _LOGGER.info("⏱️ Polling enabled: %s", update_interval is not None)

    coordinator = JellyfinCoordinator(
        hass=hass,
        entry=entry,
        api_key=api_key,
        address=f"{host}:{port}",
        update_interval=update_interval,
        use_https=use_https,
        ignore_ssl=ignore_ssl
    )

    await coordinator.async_config_entry_first_refresh()

    domain_data = hass.data.setdefault(DOMAIN, {})
    domain_data[entry.entry_id] = coordinator

    # 🧭 Trigger global sensor creation via platform
    if not domain_data.get("global_sensors_created"):
        domain_data["create_global_sensors"] = True

    # 🔄 Manual refresh service
    async def handle_refresh(call):
        await coordinator.async_request_refresh()
    hass.services.async_register(DOMAIN, "refresh", handle_refresh)

    # 🔊 Listen for entity registry updates
    def handle_registry_event(event):
        _LOGGER.debug("🔄 Entity registry updated, refreshing Jellyfin sensors...")
        hass.loop.call_soon_threadsafe(lambda: hass.async_create_task(coordinator.async_request_refresh()))
    
    coordinator._unsub_registry = hass.bus.async_listen(EVENT_ENTITY_REGISTRY_UPDATED, handle_registry_event)

    # 🚀 Forward platform setup
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    domain_data = hass.data.get(DOMAIN, {})
    coordinator = domain_data.pop(entry.entry_id, None)

    if coordinator and hasattr(coordinator, "_unsub_registry"):
        coordinator._unsub_registry()
        coordinator._unsub_registry = None

    await coordinator.async_close()
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])

async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
    return True
