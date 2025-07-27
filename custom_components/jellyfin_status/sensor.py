import logging
import os
import aiofiles.os
from datetime import timedelta
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_registry
from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.helpers.translation import async_get_translations
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED


from typing import List
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)

# Translation loader
async def async_list_translation_files():
    path = os.path.join(os.path.dirname(__file__), "translations")
    try:
        return [f for f in await aiofiles.os.listdir(path) if f.endswith(".json")]
    except Exception as e:
        _LOGGER.warning("Translation file listing failed: %s", e)
        return []

# Registry-based Jellyfin sensor discovery
async def get_jellyfin_sensor_entity_ids(hass: HomeAssistant) -> list[str]:
    registry = async_get_registry(hass)
    jellyfin_entities = []

    for entry in registry.entities.values():
        if (
            entry.domain == "sensor"
            and entry.platform == DOMAIN
            and not entry.disabled_by
            and entry.entity_category != EntityCategory.DIAGNOSTIC
        ):
            jellyfin_entities.append(entry.entity_id)

    return jellyfin_entities

# Entry setup
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([JellyfinSensor(coordinator, entry, async_add_entities)])

# Per-server Jellyfin status
class JellyfinSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
        super().__init__(coordinator)
        self.entry = entry
        self._async_add_entities = async_add_entities
        server_name = entry.options.get("server_name") or entry.title or "Jellyfin"
        slug = server_name.lower().replace(" ", "_").replace("-", "_")

        self._attr_name = f"{server_name} Status"
        self._attr_unique_id = f"{DOMAIN}_{slug}"
        self._friendly_name = self._attr_name
        self._translations = {}
        self._language = None
        self._attr_should_poll = False

    async def async_added_to_hass(self):
        self._language = self.hass.config.language
        self._translations = await async_get_translations(
            self.hass, self._language, f"custom_components.{DOMAIN}"
        )
        _LOGGER.debug("📁 Available translation files: %s", await async_list_translation_files())
        _LOGGER.debug("Loaded translations for: %s", self._language)
        _LOGGER.debug("Translation keys: %s", list(self._translations))
        self.coordinator.async_add_listener(self._handle_coordinator_update)
        await self.coordinator.async_request_refresh()

        if self.entry.entry_id == list(self.hass.data[DOMAIN].keys())[0]:
            async_call_later(
                self.hass,
                5,
                lambda _: self.hass.loop.call_soon_threadsafe(
                    lambda: self._async_add_entities([
                    JellyfinGlobalSensor(self.hass, "total"),
                    JellyfinGlobalSensor(self.hass, "error")
            ])
        )
    )

    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    def _t(self, key: str, fallback: str = None) -> str:
        # This method is primarily for general sensor translations if they exist.
        # For state attributes, we will use direct access as seen below.
        return self._translations.get(f"sensor.{key}", fallback or key)

    @property
    def state(self):
        sessions = self.coordinator.data or []
        for session in sessions:
            play_state = session.get("PlaybackState")
            flags = session.get("PlayState", {})
            if play_state == "Playing" or (not flags.get("IsPaused") and flags.get("PositionTicks", 0) > 0):
                return "Active"
        return "Idle"

    @property
    def extra_state_attributes(self):
        attrs = {}

        # Accessing translations for attribute names directly from en.json structure
        attrs["friendly_name"] = self._translations.get("entity", {}).get("sensor", {}).get("jellyfin_playback_sensor", {}).get("state_attributes", {}).get("friendly_name", {}).get("name", self._friendly_name)
        attrs["polling_enabled"] = self.coordinator.update_interval is not None
        attrs["polling_interval_seconds"] = int(self.coordinator.update_interval.total_seconds()) if self.coordinator.update_interval else 0
        attrs["last_updated"] = self.coordinator.last_updated

        sessions = self.coordinator.data or []
        active = []

        for session in sessions:
            play_state = session.get("PlaybackState")
            flags = session.get("PlayState", {})
            item = session.get("NowPlayingItem")
            user = session.get("UserName", "Unknown")

            if item and (play_state == "Playing" or (not flags.get("IsPaused") and flags.get("PositionTicks", 0) > 0)):
                active.append((user, item, session))

        sorted_sessions = sorted(active, key=lambda x: (x[0].lower(), x[1].get("Name", "").lower()))
        phrases = []

        # Retrieving localized strings for "watching" and "listening to"
        listening_to_phrase = self._translations.get("entity", {}).get("sensor", {}).get("jellyfin_playback_sensor", {}).get("state_attributes", {}).get("listening_to", {}).get("name", "is listening to")
        watching_phrase = self._translations.get("entity", {}).get("sensor", {}).get("jellyfin_playback_sensor", {}).get("state_attributes", {}).get("watching", {}).get("name", "is watching")

        for user, item, session in sorted_sessions:
            media_type = item.get("Type", "Unknown")
            title = item.get("Name", "Unknown")
            artist = item.get("Artists", [None])[0] or item.get("AlbumArtist", "Unknown")
            emoji = {"Audio": "🎵", "Movie": "🎬", "Episode": "📺"}.get(media_type, "📺")

            if media_type == "Audio":
                phrases.append(f"{emoji} {user} {listening_to_phrase} {artist} – {title}")
            elif media_type == "Episode":
                series = item.get("SeriesName", "Unknown Series")
                season = item.get("ParentIndexNumber")
                episode = item.get("IndexNumber")
                suffix = f" (S{season:02} E{episode:02})" if season and episode else ""
                phrases.append(f"{emoji} {user} {watching_phrase} {series} – {title}{suffix}")
            elif media_type == "Movie":
                phrases.append(f"{emoji} {user} {watching_phrase} {title}")
            else:
                phrases.append(f"📺 {user} {watching_phrase} {title}")

        # Retrieving localized string for "idle_message"
        idle_message_text = self._translations.get("entity", {}).get("sensor", {}).get("jellyfin_playback_sensor", {}).get("state_attributes", {}).get("idle_message", {}).get("name", "😴 Idle — nothing to see here")
        attrs["currently_playing"] = "\n".join(phrases) if phrases else idle_message_text

        # The following attribute names are not values to be translated, but keys for counts.
        # However, if you wanted their 'name' (e.g., "Active sessions") to be translated
        # and displayed as part of the attributes, you would need to fetch them similarly.
        # For this scenario, they are counts, so direct translation of the attribute value is not applicable.
        attrs["active_session_count"] = len(active)
        attrs["audio_session_count"] = sum(1 for _, item, _ in active if item.get("Type") == "Audio")
        attrs["episode_session_count"] = sum(1 for _, item, _ in active if item.get("Type") == "Episode")
        attrs["movie_session_count"] = sum(1 for _, item, _ in active if item.get("Type") == "Movie")

        # Adding other state attribute names explicitly from en.json structure if they were to be displayed directly
        # Currently, these are just keys for numeric values, not displayable strings in themselves.
        # If you wanted to *show* "Active sessions" as a string in the attributes dictionary,
        # you would fetch its name.
        attrs["language"] = self._translations.get("entity", {}).get("sensor", {}).get("jellyfin_playback_sensor", {}).get("state_attributes", {}).get("language", {}).get("name", "Language code")
        attrs["loaded_translation"] = self._translations.get("entity", {}).get("sensor", {}).get("jellyfin_playback_sensor", {}).get("state_attributes", {}).get("loaded_translation", {}).get("name", "Loaded translation")


        return attrs

# Global Jellyfin diagnostics
class JellyfinGlobalSensor(SensorEntity):
    def __init__(self, hass: HomeAssistant, sensor_type: str):
        self._hass = hass
        self._type = sensor_type
        # These are handled by translation_key directly, which should map to total_servers_sensor_name/error_servers_sensor_name in en.json
        self._attr_translation_key = f"{sensor_type}_servers_sensor_name"
        self._attr_unique_id = f"jellyfin_servers_{sensor_type}"
        self._attr_icon = "mdi:server"
        self._attr_native_value = 0
        self._attr_extra_state_attributes = {}
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        self._debounce_handle = None  # Debounce gate

    async def async_added_to_hass(self):
        async def delayed_refresh(_):
            await self._refresh(retry=True)

        async_call_later(
            self._hass,
            10,
            lambda _: self._hass.loop.call_soon_threadsafe(
                lambda: self._hass.async_create_task(delayed_refresh(None))
            )
        )

        async_track_time_interval(
            self._hass,
            lambda _: self._hass.loop.call_soon_threadsafe(
                lambda: self._hass.async_create_task(self._refresh())
            ),
            timedelta(seconds=30)
        )

        self._hass.bus.async_listen(
            EVENT_ENTITY_REGISTRY_UPDATED,
            self._handle_registry_update
        )

        self._hass.bus.async_listen(
            "state_changed",
            self._handle_state_change
        )

    async def _handle_registry_update(self, event):
        if event.data.get("action") in ("create", "remove"):
            _LOGGER.debug("📡 Registry update detected: %s", event.data.get("action"))
            self._debounce_refresh()

    async def _handle_state_change(self, event):
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")

        if (
            entity_id
            and new_state
            and entity_id.startswith("sensor.jellyfin")
            and (
                new_state.state == STATE_UNAVAILABLE or
                (old_state and old_state.state == STATE_UNAVAILABLE and new_state.state != STATE_UNAVAILABLE)
            )
        ):
            _LOGGER.debug("🔄 Jellyfin entity state changed: %s → %s", old_state.state if old_state else "?", new_state.state)
            self._debounce_refresh()

    def _debounce_refresh(self, delay: int = 5):
        if self._debounce_handle:
            self._debounce_handle()  # Cancel previous call

        def _trigger(now):
            self._debounce_handle = None
            self._hass.loop.call_soon_threadsafe(
                lambda: self._hass.async_create_task(self._refresh())
            )

        self._debounce_handle = async_call_later(self._hass, delay, _trigger)

    async def _refresh(self, retry=False):
        entity_ids = await get_jellyfin_sensor_entity_ids(self._hass)

        if retry and not entity_ids:
            _LOGGER.warning("🕵️ JellyfinGlobalSensor found no entities — retrying in 10s")
            async_call_later(
                self._hass,
                10,
                lambda _: self._hass.async_create_task(self._refresh(retry=True))
            )
            return

        available = []
        unavailable = []
        for entity_id in entity_ids:
            state = self._hass.states.get(entity_id)
            if state is None or state.state == STATE_UNAVAILABLE:
                unavailable.append(entity_id)
            else:
                available.append(entity_id)

        if self._type == "total":
            self._attr_native_value = len(entity_ids)
        elif self._type == "error":
            self._attr_native_value = len(unavailable)

        self._attr_extra_state_attributes = {
            "available": len(available),
            "unavailable": len(unavailable),
            "entities": entity_ids,
        }

        self.async_write_ha_state()