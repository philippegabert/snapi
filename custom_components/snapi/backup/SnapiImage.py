from homeassistant.components.image import ImageEntity
from homeassistant.components.camera import Camera

import collections


class SnapiImage(ImageEntity):
    def __init__(self, image_bytes):
        self._attr_name: str = "XXX"
        self._attr_unique_id: str = "image.snapi_" + "xxx"
        self._attr_content_type: str = "image/jpeg"
        self._attr_icon = "mdi:camera"
        self._attr_unique_id = "image.snapi_864323052188720"  # + str(self.idx)
        self._attr_entity_id = "image.snapi_864323052188720"  # + str(self.idx)
        self._image_bytes = image_bytes

    @property
    def camera_image(self):
        """Return the image URL of the entity."""
        return self._image_url

    @property
    def image(self) -> bytes | None:
        """Return bytes of image."""
        return self._image_bytes

    @property
    async def async_image(self) -> bytes | None:
        """Return bytes of image."""
        return self._image_bytes
