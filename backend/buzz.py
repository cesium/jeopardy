"""Module responsable for controlling Buzz Controllers"""

import os
import time
import tkinter as tk
from easyhid import Enumeration
import requests
import shared_globals


BUZZ_PENALTY_TIMEOUT = int(os.getenv("BUZZ_PENALTY_TIMEOUT", "5")) * 1e9
TIME_TO_ANSWER = int(os.getenv("TIME_TO_ANSWER", "20")) * 1e9
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))


class Buzz:
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
        self.reading = False
        self.reading_until = time.time_ns()
        self.timeouts = [time.time_ns()] * 4

    def _reset_state(self):
        """
        Clears the state of the buttons
        """
        for i in range(4):
            for j in ["red", "yellow", "green", "orange", "blue"]:
                self.button_state[i][j] = False

    def __get_valid_buzzes(self):
        """
        Returns a list of the players who pressed the button and are allowed to play
        """
        ls = []
        for i in range(0, 4):
            if self.button_state[i]["red"]:
                print(
                    f"""=====================================
Already Answered: {shared_globals.state.get_players_answered_current_question()}
Allowed: {shared_globals.state.get_allowed_players()}
Player: {i}
====================================="""
                )
                if not shared_globals.state.player_already_answered(
                    i
                ) and shared_globals.state.player_allowed_to_play(i):
                    ls.append(i)

        return ls

    def buzz_notification_thread(self):
        """
        Thread that waits for buzzes to be enabled
        """
        while True:
            with shared_globals.buzz_condition:
                shared_globals.buzz_condition.wait()
                self.reading = True
                self.reading_until = time.time_ns() + TIME_TO_ANSWER

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

    def __is_timed_out(self, controller):
        """
        Returns if the controller is in timeout
        """
        return self.timeouts[controller] >= time.time_ns()

    def _handle_buzz(self):
        """
        Handles the data from the buzzes
        """
        pressed = self.__get_valid_buzzes()

        if pressed:
            if self.reading:
                if self.reading_until >= time.time_ns():
                    for controller in pressed:
                        if self.__is_timed_out(controller):
                            print("Timeout")
                        else:
                            requests.post(
                                f"http://localhost:{SERVER_PORT}/buzz",
                                json={"player": controller},
                                timeout=10000,
                            )
                            self.reading = False
                            break
            else:
                print("Not reading")
                for p in pressed:
                    self.timeouts[p] = time.time_ns() + BUZZ_PENALTY_TIMEOUT

    def buzz_thread(self):
        """
        Thread that reads the buzzes
        """
        en = Enumeration()
        devices = en.find(manufacturer="Namtai")
        dev = devices[0]
        dev.open()
        dev.set_nonblocking(True)
        while True:
            data = dev.read(5)
            with shared_globals.buzz_condition:
                if data:
                    self._reset_state()
                    self.__parse_buzz_data(data)
                    self._handle_buzz()

            time.sleep(0.001)


class VirtualBuzz(Buzz):
    """Class for Buzz controlling Virtual Buzz Controllers"""

    def __update_button_state(self, controller: int, color: str):
        """
            Trigger when a button is pressed

        Args:
            controller (int): The controller pressed
            color (str): The coller of the button pressed
        """
        with shared_globals.buzz_condition:
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
