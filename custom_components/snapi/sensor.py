"""The Snapi Devices Reader integration."""

from datetime import timedelta
import logging

# import aiohttp
import async_timeout

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from homeassistant.const import PERCENTAGE, UnitOfVolume
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from homeassistant.helpers.entity import generate_entity_id


from .const import DOMAIN
from .exceptions import ApiAuthError, ApiError
from .snapi_api import SnapiAPI

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """async_setup_platform."""
    _LOGGER.info("Setting up SNAPI integration")
    snapi_entry = config

    snapiAPI = SnapiAPI(snapi_entry)
    coordinator = SnapiCoordinator(hass, snapiAPI, snapi_entry)

    await coordinator.async_config_entry_first_refresh()
    _LOGGER.info("Adding SNAPI entities")

    async_add_entities(
        SnapiEntity(coordinator, ent) for idx, ent in enumerate(coordinator.data)
    )
    _LOGGER.info(f"{len(coordinator.data)} SNAPI entities added")

    await coordinator.async_request_refresh()
    return True


class SnapiCoordinator(DataUpdateCoordinator):
    """SnapiCoordinator"""

    config: ConfigType

    def __init__(self, hass: HomeAssistant, snapiAPI, config) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="SNAPI",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(minutes=int(config["refresh_frequency"])),
        )
        self.config = config
        _LOGGER.info(f"Update interval for SNAPI entities is {self.update_interval}.")
        self.snapiAPI = snapiAPI

    async def _async_update_data(self):
        _LOGGER.debug("Refreshing SNAPI entities")
        try:
            async with async_timeout.timeout(60):
                return await self.snapiAPI.fetch_data()
        except ApiAuthError as err:
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")


class SnapiEntity(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, idx) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        _LOGGER.debug("Initialising entity {idx}")
        self.idx = idx
        self._attr_name = self.coordinator.data[self.idx]["friendly_name"]
        meter_type = self.coordinator.data[self.idx]["type"]
        self.entity_id = "snapi.snapi_" + str(self.idx)
        #self.unique_id = "snapi.snapi_" + str(self.idx)
        self._attr_unique_id = "snapi.snapi_" + str(self.idx)
        
        _LOGGER.debug(
            "Entity details: Name = {self._attr_name}, Unique ID = {self.unique_id}, Type = {meter_type}"
        )
        if meter_type == "gas":
            self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            self._attr_device_class = SensorDeviceClass.GAS
            self._attr_icon = "mdi:meter-gas-outline"
        elif meter_type == "water":
            self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            self._attr_device_class = SensorDeviceClass.WATER
            self._attr_icon = "mdi:water"
        elif meter_type == "battery":
            self._attr_device_class = SensorDeviceClass.BATTERY
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_icon = "mdi:battery"

    # @property
    # def device_info(self) -> DeviceInfo:
    #     return DeviceInfo(
    #         identifiers={
    #             # Serial numbers are unique identifiers within a specific domain
    #             (DOMAIN, "gas_meter_xxxxx")
    #         },
    #         name="Gas Meter",
    #         manufacturer="SNAPI",
    #         model="SNAPI GAS READER",
    #         # via_device=(DOMAIN, self.api.bridgeid),
    #     )

    def correct_outlier(self, old_value, new_value, outlier_threshold) -> float:
        if old_value > new_value:
            return old_value
        if (new_value - old_value) > outlier_threshold:
            return old_value
        return new_value

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if (
            "outlier_threshold" in self.coordinator.data[self.idx]
            and self._attr_native_value is not None
        ):
            old_value = float(self._attr_native_value)
            new_value = float(self.coordinator.data[self.idx]["value"])
            self._attr_native_value = self.correct_outlier(
                old_value,
                new_value,
                self.coordinator.data[self.idx]["outlier_threshold"],
            )
        else:
            self._attr_native_value = self.coordinator.data[self.idx]["value"]

        # img_link = self.coordinator.data[self.idx]["value"]
        if "img_link" in self.coordinator.data[self.idx]:
            self._attr_extra_state_attributes = {
                "image_link": self.coordinator.data[self.idx]["img_link"]
            }
        # print("New value = " + str(self._attr_native_value))
        self.async_write_ha_state()
