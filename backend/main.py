from threading import Thread
from server import webserver_thread
from websocket_thread import websockets_thread
import globals

if __name__ == "__main__":
    webserver = Thread(target=webserver_thread, args=())
    websockets = Thread(target=websockets_thread, args=())

    webserver.start()
    websockets.start()

    webserver.join()
    websockets.join()
