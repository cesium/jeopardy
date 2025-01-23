"""Module for running Jeopardy"""

import os
import argparse
import logging
from threading import Thread
from dotenv import load_dotenv
from server import webserver_thread
from buzz import VirtualBuzz, Buzz
import shared_globals
from gamestate import GameState

parser = argparse.ArgumentParser(description="Jeopardy Backend Controller")
parser.add_argument(
    "--virtual", action="store_true", help="Enable virtual buzz buttons."
)
parser.add_argument("--debug", action="store_true", help="Enable debug mode.")


if __name__ == "__main__":
    load_dotenv("backend/.env", override=True)
    SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

    args = parser.parse_args()
    buzzController = VirtualBuzz() if args.virtual else Buzz()
    shared_globals.state = GameState(buzzController)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    webserver = Thread(
        target=webserver_thread,
        args=(
            "0.0.0.0",
            SERVER_PORT,
        ),
    )
    buzzs = Thread(target=buzzController.buzz_thread, args=())

    webserver.start()
    buzzs.start()

    webserver.join()
    buzzs.join()
