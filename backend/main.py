"""Module for running Jeopardy"""

import os
import argparse
from threading import Thread
from dotenv import load_dotenv
from server import webserver_thread
from buzz import VirtualBuzz, Buzz


parser = argparse.ArgumentParser(description="Jeopardy Backend Controller")
parser.add_argument(
    "--virtual", action="store_true", help="Enable virtual buzz buttons."
)


if __name__ == "__main__":
    load_dotenv("backend/.env", override=True)
    SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

    args = parser.parse_args()
    buzzController = VirtualBuzz() if args.virtual else Buzz()

    webserver = Thread(
        target=webserver_thread,
        args=(
            "0.0.0.0",
            SERVER_PORT,
        ),
    )
    buzzs = Thread(target=buzzController.buzz_thread, args=())
    buzzs_notifications = Thread(
        target=buzzController.buzz_notification_thread, args=()
    )

    webserver.start()
    buzzs.start()
    buzzs_notifications.start()

    webserver.join()
    buzzs.join()
    buzzs_notifications.join()
