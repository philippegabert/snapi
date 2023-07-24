from datetime import datetime, timedelta
from urllib.parse import urlencode
import logging
import aiohttp
from .exceptions import ApiAuthError, ApiError
from .const import SNAPI_BASE_API
from PIL import Image
import io

_LOGGER = logging.getLogger(__name__)


class SnapiAPI:
    def __init__(self, snapi_config) -> None:
        _LOGGER.debug("Initialising SnapiAPI")
        self.snapi_config = snapi_config

    async def get_token(
        self,
    ):
        base_url = SNAPI_BASE_API + "/gateway/oauth/oauth/token"
        _LOGGER.debug(f"Getting SnapiAPI token using URL {0}", base_url)
        params = {
            "username": self.snapi_config["username"],
            "password": self.snapi_config["password"],
            "grant_type": "password",
        }

        url = f"{base_url}?{urlencode(params)}"

        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                _LOGGER.debug(f"Token succesfully retrieved.")
                access_token = data["access_token"]
                return access_token
            elif response.status == 400:
                try:
                    data_err = await response.json()
                    if "msg" in data_err and data_err["msg"] == "Bad credentials":
                        raise ApiAuthError(
                            msg=f"Error while retrieving access token ! Authentication failed.",
                            logger=_LOGGER,
                        )
                except:
                    raise ApiError(
                        msg=f"Error {response.status} while retrieving access token !",
                        logger=_LOGGER,
                    )

    async def fetch_data(self):
        access_token = await self.get_token()
        base_url = SNAPI_BASE_API + "/gateway/data/v1/dataAndPic"
        _LOGGER.debug(f"Fetching devices data using URL {base_url}.")
        devices_readings = {}

        for device in self.snapi_config["devices"]:
            device_name = str(device["device_name"])

            _LOGGER.info(
                f'Getting value for device "{ device["friendly_name"] }" ({device_name}).'
            )
            params = {
                "productKey": device["product_key"],
                "deviceName": device_name,
                "startTimeStamp": int(
                    (datetime.now() - timedelta(weeks=1)).timestamp()
                ),
                "endTimeStamp": int(datetime.timestamp(datetime.now())),
                "currentPage": 1,
                "pageSize": 2,
                "isChart": "false",
                "access_token": access_token,
            }

            url = f"{base_url}?{urlencode(params)}"
            async with aiohttp.ClientSession() as session, session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug(
                        f'Data successfully retrieved for { str(device["device_name"]) }. Data was {data}'
                    )

                    data_reading = data["data"]["list"][0]
                    value_reading = 0
                    if data_reading["data"]["number"] is not None:
                        value_reading = float(data_reading["data"]["number"])

                    # Value reading
                    device_reading = {
                        "type": device["type"],
                        "friendly_name": device["friendly_name"],
                        "value": value_reading,
                        "img_link": SNAPI_BASE_API + data_reading["path"],
                        "current_ts": datetime.now().strftime("%H:%M:%S"),
                    }
                    if (
                        "outlier_threshold" in device
                    ):  # Adding threshold to remove outlier directly in the reading data
                        device_reading["outlier_threshold"] = float(
                            device["outlier_threshold"]
                        )

                    devices_readings[str(device["device_name"])] = device_reading
                    # Battery reading
                    battery_reading = {
                        "type": "battery",
                        "friendly_name": device["friendly_name"] + " (Battery)",
                        "value": data_reading["data"]["electricity"],
                    }
                    devices_readings[
                        str(device["device_name"]) + "_battery"
                    ] = battery_reading
                else:
                    raise ApiError(
                        msg=f"Error {response.status} while retrieving data!",
                        logger=_LOGGER,
                    )
        return devices_readings

    async def get_image_data(self, img_link: str, angle: int):
        """To be implemented"""
        img_url = SNAPI_BASE_API + img_link
        _LOGGER.info(f"Getting meter image from URL {img_url}")
        async with aiohttp.ClientSession() as session, session.get(img_url) as response:
            if response.status == 200:
                data = await response.read()
                img = Image.open(io.BytesIO(data))
                img_rotated = img.rotate(angle)
                return img_rotated.tobytes()  # self.image_to_byte_array(img_rotated)
            else:
                raise ApiError(
                    msg=f"Error while retrieving image data.",
                    logger=_LOGGER,
                )

    def image_to_byte_array(self, image: Image):
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr
