from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.translation import async_get_translations
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

class JellyfinSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity that reports Jellyfin playback activity and user sessions."""

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)

        server_name = entry.options.get("server_name") or entry.title or "Jellyfin"
        slug = server_name.lower().replace(" ", "_").replace("-", "_")

        self._attr_name = f"{server_name} Status"
        self._attr_unique_id = f"jellyfin_status_{slug}"
        self._friendly_name = self._attr_name
        self._translations = {}
        self._language = None

    async def async_added_to_hass(self):
        """Preload translations after entity is added to Home Assistant."""
        self._language = self.hass.config.language
        self._translations = await async_get_translations(
            self.hass, self._language, f"custom_components.{DOMAIN}"
        )
        _LOGGER.debug("Loaded translations for language: %s", self._language)

    def _t(self, key: str, fallback: str = None) -> str:
        """Fetch translated string by key from sensor section."""
        full_key = f"sensor.{key}"
        return self._translations.get(full_key, fallback or key)

    @property
    def state(self):
        """Returns 'Active' if any session is playing, otherwise 'Idle'."""
        sessions = self.coordinator.data or []
        for session in sessions:
            play_state = session.get("PlaybackState")
            play_flags = session.get("PlayState", {})

            if (
                play_state == "Playing"
                or (
                    play_flags.get("IsPaused") is False
                    and play_flags.get("PositionTicks", 0) > 0
                )
            ):
                return "Active"
        return "Idle"

    @property
    def extra_state_attributes(self):
        """Reports all active sessions in sorted order, including emoji-rich details."""
        attrs = {
            "friendly_name": self._friendly_name,
            "polling_enabled": self.coordinator.update_interval is not None,
            "last_updated": self.coordinator.last_updated,
        }

        sessions = self.coordinator.data or []
        active_sessions = []

        for session in sessions:
            play_state = session.get("PlaybackState")
            play_flags = session.get("PlayState", {})
            item = session.get("NowPlayingItem")
            user = session.get("UserName", "Unknown")

            if item and (
                play_state == "Playing"
                or (
                    play_flags.get("IsPaused") is False
                    and play_flags.get("PositionTicks", 0) > 0
                )
            ):
                active_sessions.append((user, item, session))

        sorted_sessions = sorted(
            active_sessions,
            key=lambda x: (x[0].lower(), x[1].get("Name", "").lower())
        )

        playing = []
        for user, item, session in sorted_sessions:
            media_type = item.get("Type", "Unknown")
            title = item.get("Name", "Unknown")
            artist = item.get("Artists", [None])[0] or item.get("AlbumArtist", "Unknown")
            emoji = {"Audio": "🎵", "Movie": "🎬", "Episode": "📺"}.get(media_type, "📺")

            if media_type == "Audio":
                phrase = f"{emoji} {user} {self._t('listening_to', 'is listening to')} {artist} – {title}"
            elif media_type == "Episode":
                series = item.get("SeriesName", "Unknown Series")
                season = item.get("ParentIndexNumber")
                episode = item.get("IndexNumber")
                suffix = f" (S{season:02} E{episode:02})" if season and episode else ""
                phrase = f"{emoji} {user} {self._t('watching', 'is watching')} {series} – {title}{suffix}"
            elif media_type == "Movie":
                phrase = f"{emoji} {user} {self._t('watching', 'is watching')} {title}"
            else:
                phrase = f"📺 {user} {self._t('watching', 'is watching')} {title}"

            playing.append(phrase)

        if playing:
            attrs["currently_playing"] = "\n".join(playing)
        else:
            attrs["currently_playing"] = self._t("idle_message", "😴 Idle — nothing to see here")

        attrs["active_session_count"] = len(active_sessions)
        attrs["audio_session_count"] = sum(1 for _, item, _ in active_sessions if item.get("Type") == "Audio")
        attrs["episode_session_count"] = sum(1 for _, item, _ in active_sessions if item.get("Type") == "Episode")
        attrs["movie_session_count"] = sum(1 for _, item, _ in active_sessions if item.get("Type") == "Movie")

        return attrs

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Registers the Jellyfin Status sensor when the integration is loaded."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([JellyfinSensor(coordinator, entry)])
