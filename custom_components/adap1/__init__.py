import logging
import aiohttp
import async_timeout
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_UPDATE_INTERVAL, API_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry):
    """Set up the integration from a config entry."""
    hass.data[DOMAIN] = {}

    host = config_entry.data.get("host", DEFAULT_HOST)  # Kulcs: "host"
    port = config_entry.data.get("port", DEFAULT_PORT)  # Kulcs: "port"
    update_interval = config_entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL)  # Kulcs: "update_interval"

    # Az update_interval-t másodpercből timedelta-vá alakítjuk
    update_interval_timedelta = timedelta(seconds=update_interval)

    api_url = API_URL.format(host=host, port=port)

    session = async_get_clientsession(hass)
    coordinator = AdaOkosMeroDataUpdateCoordinator(hass, session, api_url, update_interval_timedelta)

    await coordinator.async_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])
    )

    return True

class AdaOkosMeroDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to handle JSON data updates."""

    def __init__(self, hass, session, api_url, update_interval):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.session = session
        self.api_url = api_url

    async def _async_update_data(self):
        """Fetch data from the JSON URL."""
        try:
            async with async_timeout.timeout(10):
                response = await self.session.get(self.api_url)
                data = await response.json()
                return data
        except Exception as err:
            _LOGGER.error("Error fetching JSON data: %s", err)
            raise
