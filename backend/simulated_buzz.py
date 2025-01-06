import globals
import time
import tkinter as tk
import requests
import os


TIMEOUT = int(os.getenv("TIMEOUT",5)) * 1e9
TIME_TO_ANSWER = int(os.getenv("TIME_TO_ANSWER",20)) * 1e9


buttonState = [
    {"red": False, "yellow": False, "green": False, "orange": False, "blue": False},
    {"red": False, "yellow": False, "green": False, "orange": False, "blue": False},
    {"red": False, "yellow": False, "green": False, "orange": False, "blue": False},
    {"red": False, "yellow": False, "green": False, "orange": False, "blue": False}
]

reading = False
readingUntil = time.time_ns()
timeouts = [time.time_ns()] * 4

def reset_state():
    """
        Clears the state of the buttons
    """
    global buttonState
    
    for i in range(4):
        for j in ["red", "yellow", "green", "orange", "blue"]:
            buttonState[i][j] = False

def get_pressed():
    """
        Returns a list of the players who pressed the button and are allowed to play
    """
    ls = []
    global buttonState
    for i in range(0,4):
        if buttonState[i]["red"]:
            print("=====================================")
            print(f"Already Answered: {globals.state.get_players_answered_current_question()}")
            print(f"Allowed: {globals.state.get_allowed_players()}")
            print(f"Player: {i}")
            print("=====================================")
        
        if buttonState[i]["red"] and not globals.state.player_already_answered(i) and globals.state.player_allowed_to_play(i):
            ls = ls + [i]

    return ls

def buzz_notification_thread():
    """
        Thread that waits for buzzes to be enabled
    """
    global reading,buttonState,readingUntil
    reading = False
    readingUntil = time.time_ns()
    while True:
        with globals.buzz_condition:
            globals.buzz_condition.wait()
            reading = True
            readingUntil = time.time_ns() + TIME_TO_ANSWER

def update_button_state(controller : int, color: str):
    """
        Trigger when a button is pressed

    Args:
        controller (int): The controller pressed
        color (str): The coller of the button pressed
    """
    global timeouts,buttonState,reading,readingUntil
    reset_state()
    buttonState[controller][color] = True
    with globals.buzz_condition:
        pressed = get_pressed()

        if pressed != []:
            if reading and readingUntil >= time.time_ns():
                for i in range(0,len(pressed)):
                    if timeouts[pressed[i]] < time.time_ns():
                        requests.post("http://localhost:8000/buzz", json = {"player": pressed[i]})
                        reading = False
                        break
                    else:
                        print("Timeout")
            elif not reading:
                print("Not reading")
                for p in pressed:
                    timeouts[p] = time.time_ns() +  TIMEOUT
        

def create_controller_frame(root : tk.Tk, controller_index : int):
    """creates a virtual buzz controller

    Args:
        root (tk.Tk): canvas to add controller to
        controller_index (int): index of the controller
    """
    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    # Create the big red circle button
    red_button = tk.Button(frame, text="Red", bg="red", command=lambda: update_button_state(controller_index, "red"))
    red_button.pack(pady=10)

    # Create the remaining color buttons
    colors = ["yellow", "green", "orange", "blue"]
    for color in colors:
        color_button = tk.Button(frame, text=color.capitalize(), bg=color, command=lambda c=color: update_button_state(controller_index, c))
        color_button.pack(pady=5)

def buzz_thread():
    root = tk.Tk()
    root.title("Simulated Buzz Controllers")
    
    for i in range(4):
        create_controller_frame(root, i)
    
    root.mainloop()