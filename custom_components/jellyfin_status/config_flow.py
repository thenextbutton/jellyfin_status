from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol
import logging

from .const import DOMAIN
from .options_flow import OptionsFlowHandler
from .coordinator import JellyfinCoordinator

_LOGGER = logging.getLogger(__name__)

class JellyfinConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jellyfin Status."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        # Use prior input values to repopulate the form on error
        default_name = user_input.get("server_name") if user_input else "Jellyfin"
        default_host = user_input.get("host") if user_input else "localhost"
        default_port = user_input.get("port") if user_input else 8096
        default_api_key = user_input.get("api_key") if user_input else ""
        default_scan = user_input.get("scan_interval") if user_input else 30
        default_https = user_input.get("use_https") if user_input else False
        default_ignore_ssl = user_input.get("ignore_ssl") if user_input else False

        if user_input is not None:
            # Check for duplicate server_name (case-insensitive)
            input_name = default_name.strip().lower()
            for entry in self._async_current_entries():
                existing_name = entry.data.get("server_name", "").strip().lower()
                if existing_name == input_name:
                    errors["base"] = "duplicate_server_name"
                    break

            # Skip Jellyfin validation if error already triggered
            if not errors:
                try:
                    if not default_host or not default_api_key:
                        errors["base"] = "invalid_input"
                    else:
                        temp_coordinator = JellyfinCoordinator(
                            hass=self.hass,
                            api_key=default_api_key,
                            address=f"{default_host}:{default_port}",
                            update_interval=None,
                            use_https=default_https,
                            ignore_ssl=default_ignore_ssl
                        )
                        await temp_coordinator._async_update_data()
                        await temp_coordinator.async_close()

                        return self.async_create_entry(
                            title=default_name,
                            data=user_input
                        )

                except Exception as e:
                    _LOGGER.warning("Connection test failed: %s", str(e))
                    error_text = str(e).lower()
                    if "401" in error_text or "unauthorized" in error_text:
                        errors["base"] = "invalid_api_key"
                    elif "cannot connect" in error_text or "timeout" in error_text:
                        errors["base"] = "cannot_connect"
                    else:
                        errors["base"] = "unknown"

        # Form schema with retained inputs
        data_schema = vol.Schema({
            vol.Required("server_name", default=default_name): str,
            vol.Required("host", default=default_host): str,
            vol.Required("port", default=default_port): int,
            vol.Required("api_key", default=default_api_key): str,
            vol.Required("scan_interval", default=default_scan): vol.In([0, 10, 15, 30, 60, 120]),
            vol.Optional("use_https", default=default_https): bool,
            vol.Optional("ignore_ssl", default=default_ignore_ssl): bool
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

class InvalidInputError(HomeAssistantError):
    """Raised when required fields are missing or malformed."""
