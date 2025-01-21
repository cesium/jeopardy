"""Module for storing globals shared by all the threads"""

from threading import Condition
from gamestate import GameState

state = GameState()
buzz_condition = Condition()
