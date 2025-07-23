from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize Jellyfin options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        # Helper to prefer updated options over original config, safely preserving 0/False
        def get_opt(key, default=None):
            if key in self.config_entry.options:
                return self.config_entry.options[key]
            return self.config_entry.data.get(key, default)

        if user_input is not None:
            # 🚫 Ensure server_name is retained unmodified
            user_input["server_name"] = get_opt("server_name")
            return self.async_create_entry(title="", data=user_input)

        # 📝 Option form schema (server_name omitted to hide from UI)
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
                ): vol.In([0, 10, 15, 30, 60, 120]),
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
                ): bool
            }),
            description_placeholders={
                "host": get_opt("host")
            }
        )
