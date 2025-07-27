import logging
import os
import aiofiles.os
import json  # Added: Import json for manual parsing
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
# Removed: from homeassistant.helpers.translation import async_get_translations
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED


from typing import List
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)


# Removed: async def async_list_translation_files(): as it's not used with manual loading

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
        self._translations = {} # Re-initialized for manual loading
        self._language = None # Re-initialized for manual loading
        self._attr_should_poll = False

    async def async_added_to_hass(self):
        self._language = self.hass.config.language.split('-')[0] # Get 'en' from 'en-GB'

        # --- Manual Translation Loading Workaround (Corrected Path) ---
        translation_file_path = os.path.join(
            os.path.dirname(__file__), # This correctly points to 'custom_components/jellyfin_status/'
            "translations",
            f"{self._language}.json"
        )
        
        # Fallback to 'en.json' if the specific language file doesn't exist
        if not await aiofiles.os.path.exists(translation_file_path):
            translation_file_path = os.path.join(
                os.path.dirname(__file__), # Corrected path here too
                "translations",
                "en.json"
            )

        loaded_translations_data = {}
        try:
            async with aiofiles.open(translation_file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                raw_json_data = json.loads(content)
                
                # Extract the relevant 'state_attributes' translations for jellyfin_playback_sensor
                # Path: entity.sensor.jellyfin_playback_sensor.state_attributes
                entity_path = raw_json_data.get("entity", {}).get("sensor", {}).get("jellyfin_playback_sensor", {})
                if "state_attributes" in entity_path:
                    loaded_translations_data = entity_path["state_attributes"]
                    _LOGGER.debug("Manually loaded state_attributes translations: %s", loaded_translations_data)
                else:
                    _LOGGER.warning("Could not find entity.sensor.jellyfin_playback_sensor.state_attributes in %s.", translation_file_path)

        except FileNotFoundError:
            _LOGGER.error("Translation file not found at %s", translation_file_path)
        except json.JSONDecodeError as e:
            _LOGGER.error("Error decoding JSON from translation file %s: %s", translation_file_path, e)
        except Exception as e:
            _LOGGER.error("Unexpected error during manual translation loading: %s", e)
        
        self._translations = loaded_translations_data
        # --- End of Manual Translation Loading Workaround ---

        _LOGGER.debug("Loaded translations language: %s", self._language)
        _LOGGER.debug("Final _translations dict: %s", self._translations)
        _LOGGER.debug("Translation keys available for _t: %s", list(self._translations.keys()))

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

    # Modified: _t method to use the manually loaded _translations
    def _t(self, key: str, fallback: str = None) -> str:
        # Navigate the dictionary to get the 'name' for the key
        translated_value = self._translations.get(key, {}).get("name")
        return translated_value if translated_value is not None else fallback if fallback is not None else key


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
        attrs = {
            "friendly_name": self._friendly_name,
            "polling_enabled": self.coordinator.update_interval is not None,
            "polling_interval_seconds": int(self.coordinator.update_interval.total_seconds()) if self.coordinator.update_interval else 0,
            "last_updated": self.coordinator.last_updated
        }

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

        for user, item, session in sorted_sessions:
            media_type = item.get("Type", "Unknown")
            title = item.get("Name", "Unknown")
            artist = item.get("Artists", [None])[0] or item.get("AlbumArtist", "Unknown")
            emoji = {"Audio": "🎵", "Movie": "🎬", "Episode": "📺"}.get(media_type, "📺")

            if media_type == "Audio":
                phrases.append(f"{emoji} {user} {self._t('listening_to', 'is listening to')} {artist} – {title}")
            elif media_type == "Episode":
                series = item.get("SeriesName", "Unknown Series")
                season = item.get("ParentIndexNumber")
                episode = item.get("IndexNumber")
                suffix = f" (S{season:02} E{episode:02})" if season and episode else ""
                phrases.append(f"{emoji} {user} {self._t('watching', 'is watching')} {series} – {title}{suffix}")
            elif media_type == "Movie":
                phrases.append(f"{emoji} {user} {self._t('watching', 'is watching')} {title}")
            else:
                phrases.append(f"📺 {user} {self._t('watching', 'is watching')} {title}")

        attrs["currently_playing"] = "\n".join(phrases) if phrases else self._t("idle_message", "😴 Idle — nothing to see here")
        attrs["active_session_count"] = len(active)
        attrs["audio_session_count"] = sum(1 for _, item, _ in active if item.get("Type") == "Audio")
        attrs["episode_session_count"] = sum(1 for _, item, _ in active if item.get("Type") == "Episode")
        attrs["movie_session_count"] = sum(1 for _, item, _ in active if item.get("Type") == "Movie")

        return attrs

# Global Jellyfin diagnostics
class JellyfinGlobalSensor(SensorEntity):
    def __init__(self, hass: HomeAssistant, sensor_type: str):
        self._hass = hass
        self._type = sensor_type
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
