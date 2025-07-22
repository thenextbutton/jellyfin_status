from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.translation import async_get_translations
from .const import DOMAIN

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

    async def async_added_to_hass(self):
        # Load sensor translations for the current HA language
        self._translations = await async_get_translations(
            self.hass, self.hass.config.language, f"custom_components.{DOMAIN}"
        )

    def _t(self, key: str) -> str:
        """Fetch translated string by key from sensor section."""
        return self._translations.get(f"sensor.{key}", key)

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
        """Reports all active sessions in sorted order, including TV episode details."""
        attrs = {
            "friendly_name": self._friendly_name,
            "polling_enabled": self.coordinator.update_interval is not None,
            "last_updated": self.coordinator.last_updated,
            "currently_playing": self._t("idle_message")
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

        # Sort by user name, then item title
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
                playing.append(f"{emoji} {user} {self._t('listening_to')} {artist} – {title}")
            elif media_type == "Episode":
                series = item.get("SeriesName", "Unknown Series")
                season = item.get("ParentIndexNumber")
                episode = item.get("IndexNumber")
                suffix = f" (S{season:02} E{episode:02})" if season and episode else ""
                playing.append(f"{emoji} {user} {self._t('watching')} {series} – {title}{suffix}")
            elif media_type == "Movie":
                playing.append(f"{emoji} {user} {self._t('watching')} {title}")
            else:
                playing.append(f"📺 {user} {self._t('watching')} {title}")

        if playing:
            attrs["currently_playing"] = "\n".join(playing)

        # Session stats
        attrs["active_session_count"] = len(active_sessions)
        attrs["audio_session_count"] = sum(1 for _, item, _ in active_sessions if item.get("Type") == "Audio")
        attrs["episode_session_count"] = sum(1 for _, item, _ in active_sessions if item.get("Type") == "Episode")
        attrs["movie_session_count"] = sum(1 for _, item, _ in active_sessions if item.get("Type") == "Movie")

        return attrs

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Registers the Jellyfin Status sensor when the integration is loaded."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([JellyfinSensor(coordinator, entry)])
