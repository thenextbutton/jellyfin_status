from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get as get_entity_registry

async def get_jellyfin_sensor_entity_ids(hass: HomeAssistant) -> list[str]:
    """Return all entity IDs for Jellyfin sensors, dynamically and safely."""
    registry = get_entity_registry(hass)
    return [
        entry.entity_id
        for entry in registry.entities.values()
        if entry.domain == "sensor" and entry.platform == "jellyfin"
    ]
