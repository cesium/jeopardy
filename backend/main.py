"""Module for running Jeopardy"""

import os
import argparse
import logging
from dotenv import load_dotenv
from server import start

parser = argparse.ArgumentParser(description="Jeopardy Backend Controller")
parser.add_argument("--debug", action="store_true", help="Enable debug mode.")


if __name__ == "__main__":
    load_dotenv("backend/.env", override=True)
    SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
    CONTROLLERS_PORT = int(os.getenv("CONTROLLERS_PORT", "8001"))

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    start("0.0.0.0", SERVER_PORT, CONTROLLERS_PORT)
