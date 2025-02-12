"""Module responsable for controlling Buzz Controllers"""

import time
import os
import argparse
import tkinter as tk
from typing import List
from abc import abstractmethod
from threading import Thread
from easyhid import Enumeration
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


class BuzzBase:
    """Class for controlling Buzz Controllers"""

    def __init__(self, host: str, port: int):
        self.server_url = f"http://{host}:{port}"
        self.light_array = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
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

    def _handle_buzz_no_confirm(self):
        """
        Handles the data from the buzzes
        """

        for i in range(0, 4):
            for color, value in self.button_state[i].items():
                if value:
                    try:
                        requests.post(
                            f"{self.server_url}/buzz",
                            json={"controller": i, "color": color},
                            timeout=0.00000000000001,
                        )
                    except requests.exceptions.ReadTimeout:
                        pass
                    break

    def _handle_buzz(self):
        """
        Handles the data from the buzzes
        """

        for i in range(0, 4):
            for color, value in self.button_state[i].items():
                if value:
                    requests.post(
                        f"{self.server_url}/buzz",
                        json={"controller": i, "color": color},
                        timeout=10,
                    )
                    break

    @abstractmethod
    def start(self):
        """
        Thread that reads the buzzes and calls _handle_buzz
        """

    @abstractmethod
    def update_controllers_lights(self):
        """turn the lights of the given controllers off"""


class Buzz(BuzzBase):
    """Class for controlling Buzz Controllers"""

    def __init__(self, host: str, port: int):
        super().__init__(host, port)

        en = Enumeration()
        devices = en.find(manufacturer="Namtai")
        self.dev = devices[0]
        self.dev.open()
        self.dev.set_nonblocking(True)

    def update_controllers_lights(self):
        """Update the lights of the controllers"""
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

    def start(self):
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

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.red_buttons = []

    def __update_button_state(self, controller: int, color: str):
        """
        Trigger when a button is pressed.

        Args:
            controller (int): The controller pressed.
            color (str): The color of the button pressed.
        """
        super()._reset_state()
        self.button_state[controller][color] = True
        super()._handle_buzz_no_confirm()

    def __create_controller_frame(self, root: tk.Tk, controller_index: int):
        """Creates a virtual buzz controller.

        Args:
            root (tk.Tk): Canvas to add the controller to.
            controller_index (int): Index of the controller.
        """
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        b = tk.Button(
            frame,
            text="Red",
            bg="#8B0000",
            command=lambda: self.__update_button_state(controller_index, "red"),
        )
        b.pack(pady=5)

        # Create the red button
        self.red_buttons.append(b)

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

    def update_controllers_lights(self):
        """
        Updates the colors of the red circle buttons based on the light array.
        """
        for i in range(4):
            new_color = "#FF0000" if self.light_array[i + 1] == 0xFF else "#8B0000"
            self.red_buttons[i].config(bg=new_color)

    def start(self):
        """
        Thread that creates the virtual buzz controllers.
        """
        root = tk.Tk()
        root.title("Virtual Buzz Controllers")

        for i in range(4):
            self.__create_controller_frame(root, i)

        root.mainloop()


if __name__ == "__main__":
    load_dotenv("backend/.env", override=True)
    SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
    CONTROLLER_PORT = int(os.getenv("CONTROLLER_PORT", "8001"))

    parser = argparse.ArgumentParser(description="Jeopardy Backend Controller")
    parser.add_argument(
        "--virtual", action="store_true", help="Enable virtual buzz buttons."
    )

    args = parser.parse_args()
    buzzController = (
        VirtualBuzz("localhost", SERVER_PORT)
        if args.virtual
        else Buzz("localhost", SERVER_PORT)
    )
    t = Thread(target=buzzController.start, args=())
    t.start()

    app = FastAPI()

    class LightRequest(BaseModel):
        """Request model"""

        controllers: List[int]

    class Reponse(BaseModel):
        """Response model"""

        status: str

    @app.post("/on", response_model=Reponse)
    def post_on(body: LightRequest):
        """Turn the lights of the given controllers on
        Args:
            light_request (LightRequest): controllers
        """
        for i in body.controllers:
            buzzController.light_array[i + 1] = 0xFF
        buzzController.update_controllers_lights()
        return {"status": "success"}

    @app.post("/off", response_model=Reponse)
    def post_off(body: LightRequest):
        """Turn the lights of the given controllers off
        Args:
            light_request (LightRequest): controllers
        """
        for i in body.controllers:
            buzzController.light_array[i + 1] = 0x00
        buzzController.update_controllers_lights()
        return {"status": "success"}

    uvicorn.run(app, host="0.0.0.0", port=CONTROLLER_PORT)
    t.join()
