from easyhid import Enumeration
import globals
import time
import requests
import os


TIMEOUT = os.get_env("TIMEOUT",5) * 1e9
TIME_TO_ANSWER = os.get_env("TIME_TO_ANSWER",20) * 1e9


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
    global buttonState
    ls = []
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
    reset_state()
    readingUntil = time.time_ns()
    while True:
        with globals.buzz_condition:
            globals.buzz_condition.wait()
            reading = True
            readingUntil = time.time_ns() + TIME_TO_ANSWER

def buzz_thread():
    """
        Thread that reads the buzzes
    """
    global reading,buttonState,readingUntil
    reading = False
    en = Enumeration()
    devices = en.find(manufacturer="Namtai")
    dev = devices[0]
    dev.open()
    dev.set_nonblocking(True)
    while True:
        data = dev.read(5)
        with globals.buzz_condition:
            if data:
                buttonState[0]["red"] = ((data[2] & 0x01) != 0) #red
                buttonState[0]["yellow"] = ((data[2] & 0x02) != 0) #yellow
                buttonState[0]["green"] = ((data[2] & 0x04) != 0) #green
                buttonState[0]["orange"] = ((data[2] & 0x08) != 0) #orange
                buttonState[0]["blue"] = ((data[2] & 0x10) != 0) #blue
                buttonState[1]["red"] = ((data[2] & 0x20) != 0) #red
                buttonState[1]["yellow"] = ((data[2] & 0x40) != 0) #yellow
                buttonState[1]["green"] = ((data[2] & 0x80) != 0) #green
                buttonState[1]["orange"] = ((data[3] & 0x01) != 0) #orange
                buttonState[1]["blue"] = ((data[3] & 0x02) != 0) #blue
                buttonState[2]["red"] = ((data[3] & 0x04) != 0) #red
                buttonState[2]["yellow"] = ((data[3] & 0x08) != 0) #yellow
                buttonState[2]["green"] = ((data[3] & 0x10) != 0) #green
                buttonState[2]["orange"] = ((data[3] & 0x20) != 0) #orange
                buttonState[2]["blue"] = ((data[3] & 0x40) != 0) #blue
                buttonState[3]["red"] = ((data[3] & 0x80) != 0) #red
                buttonState[3]["yellow"] = ((data[4] & 0x01) != 0) #yellow
                buttonState[3]["green"] = ((data[4] & 0x02) != 0) #green
                buttonState[3]["orange"] = ((data[4] & 0x04) != 0) #orange
                buttonState[3]["blue"] = ((data[4] & 0x08) != 0) #blue

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
        time.sleep(0.001)