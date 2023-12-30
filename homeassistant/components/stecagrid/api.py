"""The module contains the InverterAPI class for interacting with the StecaGrid inverter."""

import aiohttp
from defusedxml import ElementTree as ET


class InverterAPI:
    """Represents an API for interacting with a StecaGrid inverter.

    Args:
        host (str): The IP address or hostname of the inverter.
        port (int): The port number of the inverter's API.
        session (aiohttp.ClientSession): The aiohttp client session to use for making requests.

    Attributes:
        _host (str): The IP address or hostname of the inverter.
        _port (int): The port number of the inverter's API.
        _session (aiohttp.ClientSession): The aiohttp client session to use for making requests.
    """

    def __init__(self, host, port, session) -> None:
        """Initialize the InverterAPI class.

        Args:
            host (str): The IP address or hostname of the inverter.
            port (int): The port number of the inverter's API.
            session (aiohttp.ClientSession): The aiohttp client session to use for making requests.
        """
        self._host = host
        self._port = port
        self._session = session

    async def validate_connection(self):
        """Validate the connection to the inverter.

        Returns:
            str: The name of the inverter if the connection is valid, False otherwise.
        """
        try:
            response = await self._session.get(
                f"http://{self._host}:{self._port}/measurements.xml"
            )
            response.raise_for_status()
            data = await response.text()
            root = ET.fromstring(data)

            # Check for a specific key-value pair
            device = root.find("Device")
            if device is not None and "StecaGrid" in device.get("Name", ""):
                return device.get("Name", "")

            return False
        except aiohttp.ClientError:
            return False

    async def get_data(self):
        """Retrieve the measurements data from the inverter.

        Returns:
            dict: A dictionary containing the measurements data, where the keys are the measurement types
            and the values are dictionaries with "value" and "unit" keys.
        """
        response = await self._session.get(
            f"http://{self._host}:{self._port}/measurements.xml"
        )
        response.raise_for_status()
        data = await response.text()
        root = ET.fromstring(data)

        measurements = {}
        for measurement in root.find("Device/Measurements"):
            type_ = measurement.get("Type")
            value = measurement.get("Value")
            unit = measurement.get("Unit")
            measurements[type_] = {"value": value, "unit": unit}

        return measurements
