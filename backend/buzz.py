from easyhid import Enumeration
import time
import random
import threading
import datetime

class BuzzController:
    light_array     = [0x00, 0x00, 0x00, 0x00, 0x00]
    light_blinking = False
    buttonState = [
        {"red": False, "blue": False, "orange": False, "green": False, "yellow": False},
        {"red": False, "blue": False, "orange": False, "green": False, "yellow": False},
        {"red": False, "blue": False, "orange": False, "green": False, "yellow": False},
        {"red": False, "blue": False, "orange": False, "green": False, "yellow": False}
    ]

    def __init__(self,dev):
        self.dev = dev
        self.dev.open()
        
        self.dev.set_nonblocking(True)

        #Clear the Buzz Controller LEDs
        self.dev.write(bytearray(self.light_array))

    def light_blink(self, controller):
        blink_lights_off = [0x00, 0x00, 0x00, 0x00, 0x00]
        self.blink_lights_on = [0x00, 0x00, 0x00, 0x00, 0x00]

        for i in controller:
            self.blink_lights_on[i] = 0xFF

        if (not self.light_blinking):
            self.light_blinking = True
            blink = True
            while self.light_blinking:
                if (blink):
                    self.dev.write(bytearray(self.blink_lights_on))
                else:
                    self.dev.write(bytearray(blink_lights_off))
                blink = not blink
                time.sleep(0.5)

            self.dev.write(bytearray(self.light_array))
    
    def get_button_status(self):
        data = self.dev.read(5)
        if data:
            self.buttonState[0]["red"] = ((data[2] & 0x01) != 0) #red
            self.buttonState[0]["yellow"] = ((data[2] & 0x02) != 0) #yellow
            self.buttonState[0]["green"] = ((data[2] & 0x04) != 0) #green
            self.buttonState[0]["orange"] = ((data[2] & 0x08) != 0) #orange
            self.buttonState[0]["blue"] = ((data[2] & 0x10) != 0) #blue

            self.buttonState[1]["red"] = ((data[2] & 0x20) != 0) #red
            self.buttonState[1]["yellow"] = ((data[2] & 0x40) != 0) #yellow
            self.buttonState[1]["green"] = ((data[2] & 0x80) != 0) #green
            self.buttonState[1]["orange"] = ((data[3] & 0x01) != 0) #orange
            self.buttonState[1]["blue"] = ((data[3] & 0x02) != 0) #blue

            self.buttonState[2]["red"] = ((data[3] & 0x04) != 0) #red
            self.buttonState[2]["yellow"] = ((data[3] & 0x08) != 0) #yellow
            self.buttonState[2]["green"] = ((data[3] & 0x10) != 0) #green
            self.buttonState[2]["orange"] = ((data[3] & 0x20) != 0) #orange
            self.buttonState[2]["blue"] = ((data[3] & 0x40) != 0) #blue

            self.buttonState[3]["red"] = ((data[3] & 0x80) != 0) #red
            self.buttonState[3]["yellow"] = ((data[4] & 0x01) != 0) #yellow
            self.buttonState[3]["green"] = ((data[4] & 0x02) != 0) #green
            self.buttonState[3]["orange"] = ((data[4] & 0x04) != 0) #orange
            self.buttonState[3]["blue"] = ((data[4] & 0x08) != 0) #blue
        return self.buttonState
    
    def get_button_pressed(self, controller):
        buttons = self.get_button_status()
        for key, value in buttons[controller].items():
            if (value):
                return key
    
    def controller_get_first_pressed(self, buzzButton, controllers = [0, 1, 2, 3]):
        while True:
            buttons = self.get_button_status()
            for i in controllers:
                if (buttons[i-1][buzzButton]):
                    return i
    def reset(self):
        self.light_blink_stop()
        for i in range(1,5): self.light_set(i, False)
        self.pressed={
            1:datetime.datetime.now(),
            2:datetime.datetime.now(),
            3:datetime.datetime.now(),
            4:datetime.datetime.now()
        }
        
    def detect_premature_pressing(self,event):
        while not event.is_set():
            self.pressed[self.controller_get_first_pressed("red",[1,2,3,4])] = datetime.datetime.now()
            
    def get_winner(self):
        while True:
            i = self.controller_get_first_pressed("red",[1,2,3,4])
            currTime = datetime.datetime.now()
            if (currTime > self.pressed[i] + datetime.timedelta(seconds=5) ):
                return i
    
    
    def light_blink_stop(self):
        self.light_blinking = False
        
    def light_set(self, controller, status):
        self.light_array[controller] = 0xFF if status else 0x00
        self.dev.write(bytearray(self.light_array))





class Jeperty():
    def __init__(self):
        en = Enumeration()
        devices = en.find(manufacturer="Namtai")
        dev = devices[0]
        
        self.controller = BuzzController(dev)
        
        
    def start(self):
        self.controller.reset()
        stop_event = threading.Event()
        prematureThread = threading.Thread(target=self.controller.detect_premature_pressing,args=(stop_event,))
        prematureThread.start()

        time.sleep(random.randint(3, 10))
        stop_event.set()
        blinkThread = threading.Thread(target=self.controller.light_blink,args=([1,2,3,4],))
        blinkThread.start()

        i=self.controller.get_winner()
        self.controller.light_blink_stop()
        self.controller.light_set(i,True)

        prematureThread.join()
        blinkThread.join()
    
Jeperty().start()