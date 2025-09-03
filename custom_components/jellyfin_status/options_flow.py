from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class JellyfinOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize Jellyfin options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        # Helper to prefer updated options over original config, safely preserving 0/False
        def get_opt(key, default=None):
            if key in self._config_entry.options:
                return self._config_entry.options[key]
            return self._config_entry.data.get(key, default)

        if user_input is not None:
            # Preserve server_name internally; not exposed in form
            user_input["server_name"] = get_opt("server_name")
            return self.async_create_entry(title="", data=user_input)

        # Option form schema
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    "host",
                    default=get_opt("host"),
                    description={
                        "suggested_value": get_opt("host"),
                        "translation_key": "host"
                    }
                ): str,
                vol.Required(
                    "port",
                    default=get_opt("port"),
                    description={
                        "suggested_value": get_opt("port"),
                        "translation_key": "port"
                    }
                ): int,
                vol.Required(
                    "api_key",
                    default=get_opt("api_key"),
                    description={
                        "suggested_value": get_opt("api_key"),
                        "translation_key": "api_key"
                    }
                ): str,
                vol.Required(
                    "scan_interval",
                    default=get_opt("scan_interval", 30),
                    description={
                        "suggested_value": get_opt("scan_interval"),
                        "translation_key": "scan_interval"
                    }
                ): vol.In([0, 1, 5, 10, 15, 30, 60, 120]),
                vol.Optional(
                    "use_https",
                    default=get_opt("use_https", False),
                    description={
                        "suggested_value": get_opt("use_https"),
                        "translation_key": "use_https"
                    }
                ): bool,
                vol.Optional(
                    "ignore_ssl",
                    default=get_opt("ignore_ssl", False),
                    description={
                        "suggested_value": get_opt("ignore_ssl"),
                        "translation_key": "ignore_ssl"
                    }
                ): bool,
                vol.Optional(
                    "playback_format",
                    default=get_opt("playback_format", "{play_icon} {media_icon} {user}: {artist} – {title} ({playing_position}/{playback_runtime}) {playback_percentage}"),
                    description={
                        "suggested_value": get_opt("playback_format"),
                                        "translation_key": "playback_format"
                    }
                ): str,
                vol.Optional(
                    "idle_message",
                    default=get_opt("idle_message", "💤 Nothing Playing."),
                    description={
                        "suggested_value": get_opt("idle_message"),
                        "translation_key": "idle_message"
                    }
                ): vol.All(str, vol.Length(min=0)),
                vol.Optional(
                    "debug_payloads",
                    default=get_opt("debug_payloads", False),
                    description={
                        "suggested_value": get_opt("debug_payloads"),
                        "translation_key": "debug_payloads"
                    }
                ): bool
            }),
            description_placeholders={
                "host": get_opt("host")
            }
        )
