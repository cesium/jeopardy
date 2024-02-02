
from gamestate import GameState
from threading import Condition

state = GameState()

buzz_condition = Condition()
to_read = False
state_condition = Condition()
