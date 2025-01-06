from threading import Thread
from server import webserver_thread
from websocket_thread import websockets_thread
import argparse
from dotenv import load_dotenv
import os



parser = argparse.ArgumentParser(description="Jeopardy Backend Controller")
parser.add_argument("--simulated", action="store_true", help="Enable simulated buzz buttons.")




if __name__ == "__main__":
    args = parser.parse_args()
    load_dotenv("backend/.env",override=True)
    
    if args.simulated:
        import simulated_buzz as buzz
    else:
        import buzz
    SERVER_PORT = int(os.getenv("SERVER_PORT",8000))
    WS_PORT = int(os.getenv("WS_PORT",8001))
    
    webserver  = Thread(target=webserver_thread, args=('127.0.0.1',SERVER_PORT,))
    websockets = Thread(target=websockets_thread, args=('127.0.0.1',WS_PORT,))
    buzzs      = Thread(target=buzz.buzz_thread, args=())
    buzzs_notifications  = Thread(target=buzz.buzz_notification_thread, args=())

    webserver.start()
    websockets.start()
    buzzs.start()
    buzzs_notifications.start()

    webserver.join()
    websockets.join()
    buzzs.join()
    buzzs_notifications.join()
