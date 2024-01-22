from threading import Thread
from server import webserver_thread
from websocket_thread import websockets_thread
from buzz import buzz_thread, buzz_notification_thread

if __name__ == "__main__":
    webserver  = Thread(target=webserver_thread, args=())
    websockets = Thread(target=websockets_thread, args=())
    buzzs      = Thread(target=buzz_thread, args=())
    buzzs_not  = Thread(target=buzz_notification_thread, args=())

    webserver.start()
    websockets.start()
    buzzs.start()
    buzzs_not.start()

    webserver.join()
    websockets.join()
    buzzs.join()
    buzzs_not.join()
