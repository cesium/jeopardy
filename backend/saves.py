""" Module for saving and loading game states"""

import os
import pickle
from time import time
from typing import List, Tuple
from gamestate.gamestate import GameState


def get_file_timestamp(name: str) -> int:
    """get the timestamp of a save file

    Args:
        name (str): the name of the save file

    Returns:
        int: the timestamp of the save file
    """
    return int(name.split(".")[0])


def delete_future_saves(name: str):
    """delete any save files with a timestamp greater than the given name
    Args:
        name: filename of the save file
    """
    timestamp = get_file_timestamp(name)
    saves = get_saves_names()
    for save_timestamp, save_name in saves:
        if save_timestamp > timestamp:
            os.remove(f"backend/saves/{save_name}")


def get_saves_names() -> List[Tuple[int, str]]:
    """get all saved game states

    Returns:
        List[Tuple[int,str]]: list of saved game states with their timestamps
    """
    l = os.listdir("backend/saves")
    return sorted(map(lambda x: (get_file_timestamp(x), x), l))


def save_state(state: GameState, action: str):
    """save the current game state

    Args:
        state (GameState): the current game state
        action (str): the action that led to this state
    """
    with open(f"backend/saves/{int(time())}.{action}.pkl", "wb") as f:
        pickle.dump(state, f)


def load_save(name: str) -> GameState | None:
    """load a saved game state and delete any future saves

    Args:
        name (str): the name of the saved game state

    Returns:
        GameState: the loaded game state
    """
    if os.path.exists(f"backend/saves/{name}") and os.path.isfile(
        f"backend/saves/{name}"
    ):

        delete_future_saves(name)
        with open(f"backend/saves/{name}", "rb") as f:
            return pickle.load(f)
    return None


def get_last_save() -> GameState | None:
    """get the last saved game state

    Returns:
        GameState | None: the last saved game state | None if there is no saved state
    """
    saves = get_saves_names()
    if saves:
        _, last_save = saves[-1]
        return load_save(last_save)
    return None
