"""Module responsable for controlling Buzz Controllers"""

import os
import time
import tkinter as tk
from typing import List
from abc import abstractmethod
from easyhid import Enumeration
import requests

SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))


class BuzzBase:
    """Class for controlling Buzz Controllers"""

    def __init__(self):
        self.button_state = [
            {
                "red": False,
                "yellow": False,
                "green": False,
                "orange": False,
                "blue": False,
            },
            {
                "red": False,
                "yellow": False,
                "green": False,
                "orange": False,
                "blue": False,
            },
            {
                "red": False,
                "yellow": False,
                "green": False,
                "orange": False,
                "blue": False,
            },
            {
                "red": False,
                "yellow": False,
                "green": False,
                "orange": False,
                "blue": False,
            },
        ]

    def _reset_state(self):
        """
        Clears the state of the buttons
        """
        for i in range(4):
            for j in ["red", "yellow", "green", "orange", "blue"]:
                self.button_state[i][j] = False

    def _handle_buzz(self):
        """
        Handles the data from the buzzes
        """

        for i in range(0, 4):
            for color, value in self.button_state[i].items():
                if value:
                    requests.post(
                        f"http://localhost:{SERVER_PORT}/buzz",
                        json={"controller": i, "color": color},
                        timeout=10000,
                    )
                    break

    @abstractmethod
    def buzz_thread(self):
        """
        Thread that reads the buzzes and calls _handle_buzz
        """

    def turn_light_on(self, controllers: List[int]):
        """turn the lights of the given controllers on
        Args:
            controllers (List[int]): list of controllers to turn on
        """

    def turn_light_off(self, controllers: List[int]):
        """turn the lights of the given controllers off
        Args:
            controllers (List[int]): list of controllers to turn on
        """


class Buzz(BuzzBase):
    """Class for controlling Buzz Controllers"""

    def __init__(self):
        super().__init__()
        self.light_array = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        en = Enumeration()
        devices = en.find(manufacturer="Namtai")
        self.dev = devices[0]
        self.dev.open()
        self.dev.set_nonblocking(True)

    def turn_light_on(self, controllers: List[int]):
        """Turn the lights of the given controllers on

        Args:
            controllers (List[int]): controllers
        """
        for i in controllers:
            self.light_array[i + 1] = 0xFF
        self.dev.write(self.light_array)

    def turn_light_off(self, controllers: List[int]):
        """Turn the lights of the given controllers off

        Args:
            controllers (List[int]): controllers
        """
        for i in controllers:
            self.light_array[i + 1] = 0x00
        self.dev.write(self.light_array)

    def __parse_buzz_data(self, data):
        """
        Parses the data from the buzz
        """
        self.button_state[0]["red"] = (data[2] & 0x01) != 0  # red
        self.button_state[0]["yellow"] = (data[2] & 0x02) != 0  # yellow
        self.button_state[0]["green"] = (data[2] & 0x04) != 0  # green
        self.button_state[0]["orange"] = (data[2] & 0x08) != 0  # orange
        self.button_state[0]["blue"] = (data[2] & 0x10) != 0  # blue
        self.button_state[1]["red"] = (data[2] & 0x20) != 0  # red
        self.button_state[1]["yellow"] = (data[2] & 0x40) != 0  # yellow
        self.button_state[1]["green"] = (data[2] & 0x80) != 0  # green
        self.button_state[1]["orange"] = (data[3] & 0x01) != 0  # orange
        self.button_state[1]["blue"] = (data[3] & 0x02) != 0  # blue
        self.button_state[2]["red"] = (data[3] & 0x04) != 0  # red
        self.button_state[2]["yellow"] = (data[3] & 0x08) != 0  # yellow
        self.button_state[2]["green"] = (data[3] & 0x10) != 0  # green
        self.button_state[2]["orange"] = (data[3] & 0x20) != 0  # orange
        self.button_state[2]["blue"] = (data[3] & 0x40) != 0  # blue
        self.button_state[3]["red"] = (data[3] & 0x80) != 0  # red
        self.button_state[3]["yellow"] = (data[4] & 0x01) != 0  # yellow
        self.button_state[3]["green"] = (data[4] & 0x02) != 0  # green
        self.button_state[3]["orange"] = (data[4] & 0x04) != 0  # orange
        self.button_state[3]["blue"] = (data[4] & 0x08) != 0  # blue

    def buzz_thread(self):
        """
        Thread that reads the buzzes
        """
        while True:
            data = self.dev.read(5)
            if data:
                self._reset_state()
                self.__parse_buzz_data(data)
                self._handle_buzz()

            time.sleep(0.001)


class VirtualBuzz(BuzzBase):
    """Class for Buzz controlling Virtual Buzz Controllers"""

    def __update_button_state(self, controller: int, color: str):
        """
            Trigger when a button is pressed

        Args:
            controller (int): The controller pressed
            color (str): The coller of the button pressed
        """
        super()._reset_state()
        self.button_state[controller][color] = True
        super()._handle_buzz()

    def __create_controller_frame(self, root: tk.Tk, controller_index: int):
        """creates a virtual buzz controller

        Args:
            root (tk.Tk): canvas to add controller to
            controller_index (int): index of the controller
        """
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Create the big red circle button
        red_button = tk.Button(
            frame,
            text="Red",
            bg="red",
            command=lambda: self.__update_button_state(controller_index, "red"),
        )
        red_button.pack(pady=10)

        # Create the remaining color buttons
        colors = ["yellow", "green", "orange", "blue"]
        for color in colors:
            color_button = tk.Button(
                frame,
                text=color.capitalize(),
                bg=color,
                command=lambda c=color: self.__update_button_state(controller_index, c),
            )
            color_button.pack(pady=5)

    def buzz_thread(self):
        """
        Thread that creates the virtual buzz controllers
        """
        root = tk.Tk()
        root.title("Virtual Buzz Controllers")

        for i in range(4):
            self.__create_controller_frame(root, i)

        root.mainloop()
