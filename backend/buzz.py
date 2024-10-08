from easyhid import Enumeration
import globals
import time
import requests

defaultState = [
    {"red": False, "yellow": False, "green": False, "orange": False, "blue": False},
    {"red": False, "yellow": False, "green": False, "orange": False, "blue": False},
    {"red": False, "yellow": False, "green": False, "orange": False, "blue": False},
    {"red": False, "yellow": False, "green": False, "orange": False, "blue": False}
]

buttonState = defaultState
reading = False
readingUntil = time.time_ns()

def get_pressed(state):
    ls = []
    for i in range(0,4):
        if state[i]["red"]:
            print("=====================================")
            print(f"Already Answered: {globals.state.alreadyAnswered}")
            print(f"Allowed: {globals.state.allowedPlayers}")
            print(f"Player: {i}")
            print("=====================================")
        
        if state[i]["red"] and i not in globals.state.alreadyAnswered and i in globals.state.allowedPlayers:
            ls = ls + [i]

    return ls

def buzz_notification_thread():
    global reading
    reading = False
    global readingUntil
    buttonState = defaultState
    readingUntil = time.time_ns()
    while True:
        with globals.buzz_condition:
            globals.buzz_condition.wait()
            reading = True
            readingUntil = time.time_ns() + 1e10

def buzz_thread():
    global reading
    global buttonState
    global readingUntil
    reading = False
    en = Enumeration()
    devices = en.find(manufacturer="Namtai")
    dev = devices[0]
    dev.open()
    dev.set_nonblocking(True)

    timeouts = [time.time_ns()] * 4
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

                pressed = get_pressed(buttonState)

                if pressed != []:
                    if reading and readingUntil >= time.time_ns():
                        for i in range(0,len(pressed)):
                            if timeouts[pressed[i]] < time.time_ns():
                                buttonState = defaultState
                                requests.post("http://localhost:8000/buzz", json = {"player": pressed[i]})
                                reading = False
                                break
                        print("Timeout")
                    elif not reading:
                        print("Not reading")
                        for p in pressed:
                            timeouts[p] = time.time_ns() + 5e9
                    
        time.sleep(0.001)