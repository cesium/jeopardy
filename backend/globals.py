
from gamestate import GameState
from threading import Condition

state = GameState()

buzz_condition = Condition()
state_condition = Condition()
