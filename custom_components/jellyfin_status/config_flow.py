from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN
from .options_flow import OptionsFlowHandler

class JellyfinConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["server_name"],
                data={
                    "host": user_input["host"],
                    "port": user_input["port"],
                    "api_key": user_input["api_key"],
                    "scan_interval": user_input["scan_interval"],
                    "use_https": user_input["use_https"],
                    "ignore_ssl": user_input["ignore_ssl"]
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("server_name", default="Jellyfin"): str,
                vol.Required("host", default="<Jellyfin Host Address>"): str,
                vol.Required("port", default=8096): int,
                vol.Required("api_key"): str,
                vol.Required("scan_interval", default=30): vol.In([0, 10, 15, 30, 60, 120]),
                vol.Optional("use_https", default=False): bool,
                vol.Optional("ignore_ssl", default=False): bool
            })
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)
