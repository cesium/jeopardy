""" This module is responsible for interfacing with the buzz controller """

from typing import List
import requests


class Buzz:
    """Class to interface with the buzz controller"""

    def __init__(self, host: str, controller_port: str):
        """Initialize the Buzz class
        Args:
            host (str): the host to contact to turn lights
            controller_port (str): the port to contact to turn lights
        """
        self.url = f"http://{host}:{controller_port}"

    def turn_light_on(self, controllers: List[int]):
        """Turn the lights of the given controllers on

        Args:
            controllers (List[int]): controllers

        Raises:
            Exception: Error turning light on
        """
        url = f"{self.url}/on"
        response = requests.post(url, json={"controllers": controllers}, timeout=10)
        if response.status_code != 200:
            raise ConnectionError(f"Error turning light on: {response.text}")

    def turn_light_off(self, controllers: List[int]):
        """Turn the lights of the given controllers off

        Args:
            controllers (List[int]): controllers

        Raises:
            Exception: Error turning light off
        """
        url = f"{self.url}/off"
        response = requests.post(url, json={"controllers": controllers}, timeout=10)
        print(response.status_code)
