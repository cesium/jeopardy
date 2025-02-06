# pylint: disable=too-many-instance-attributes
"""Module responsable for storing the state of the game"""

from enum import Enum
from typing import List
import os
import time
import logging
from buzz_interface import Buzz
from requests.exceptions import ConnectionError as requests_ConnectionError
from .questions_controller import QuestionsController
from .teams_controller import TeamsController
from .actions import Actions
from .models import Team, Question

SPLIT_OR_STEAL = bool(os.getenv("USE_SPLIT_OR_STEAL", "True"))
BUZZ_PENALTY_TIMEOUT = int(os.getenv("BUZZ_PENALTY_TIMEOUT", "5")) * 1e9
TIME_TO_ANSWER = int(os.getenv("TIME_TO_ANSWER", "20")) * 1e9


class States(Enum):
    """Enumeration for possible states of the game"""

    STARTING = 0
    SELECTING_QUESTION = 1
    READING_QUESTION = 2
    ANSWERING_QUESTION = 3
    TEAM_SELECTED = 4
    SPLIT_OR_STEAL = 5
    OVER = 6


class GameState:
    """Class to store the state of the game"""

    def __init__(self, controllers: Buzz):
        self.questions_controller = QuestionsController()
        self.teams_controller = TeamsController()
        self.state: States = States.STARTING
        self.actions = Actions()

        self.controllers_used_in_current_question = []

        self.sos_steal = {}

        self.controllers = controllers
        self.reading = False
        self.__set_reading(False)
        self.reading_until = time.time_ns()
        self.timeouts = [time.time_ns()] * 4

    def set_state(self, state: int):
        """set the state of the game

        Args:
            state (int): the state to set
        """
        self.state = States(state)

    def set_selecting(self, team_idx: int):
        """set a team as selecting

        Args:
            team_idx (int): the id of the team
        """
        self.teams_controller.set_selecting(team_idx)

    def __game_over(self):
        self.state = States.OVER
        self.actions.play_end_sound = True

    def get_current_team(self) -> Team:
        """return the team playing

        Returns:
            Team: the team playing
        """
        return self.teams_controller.get_current_team()

    def __get_allowed_controllers(self) -> List[int]:
        """return the controllers that are allowed to play

        Returns:
            List[int]: list of controllers that are allowed to play
        """
        return self.teams_controller.playing

    def set_teams(self, teams_names: List[str]):
        """sets the teams playing

        Args:
            teams_names (List[str]): list of the names of the teams

        Raises:
            AssertionError: if teams are set mid game
        """
        logging.debug("Setting Teams")
        if self.state != States.STARTING:
            raise AssertionError("Cannot set teams mid game")
        self.teams_controller.set_teams(teams_names)
        self.state = States.SELECTING_QUESTION

    def set_current_team(self, team_idx: int):
        """set a new team as playing

        Args:
            team_idx (int): the id of the team
        """
        logging.debug("Set %d as team playing", team_idx)
        self.reading = False
        self.controllers.turn_light_off(list({0, 1, 2, 3} - {team_idx}))

        self.controllers_used_in_current_question.append(team_idx)
        self.teams_controller.set_current_playing(team_idx)
        self.state = States.TEAM_SELECTED
        self.actions.play_buzzer_sound = True

    def __split_or_steal(self, controller: int, option: bool):
        """split or steal the balance of the team

        Args:
            controller (int): controller that is splitting or stealing
            option (bool): controller chose steal
        """
        logging.debug("Split or Steal: %d %s", controller, option)
        self.controllers_used_in_current_question.append(controller)
        self.sos_steal[controller] = option
        self.actions.play_buzzer_sound = True

    def show_sos(self):
        """show the split or steal options"""
        if len(self.sos_steal) == len(self.teams_controller.playing):
            self.actions.show_sos = True
            # stealers = [i for i, k in self.sos_steal.items() if k]
            # self.teams_controller.split_or_steal(stealers)

    def end_game(self):
        """end the game"""
        if self.state == States.SPLIT_OR_STEAL and self.actions.show_sos:
            self.__game_over()

    def __get_sos_values(self):
        l = []
        for i in self.teams_controller.playing:
            l.append(self.sos_steal[i] if i in self.sos_steal else None)
        return l

    def __handle_normal_buzz(self, controller: int, color: str):
        if color == "red":
            if self.reading:
                if self.reading_until >= time.time_ns():
                    if self.timeouts[controller] >= time.time_ns():
                        logging.info("TIMEOUT")
                    else:
                        self.set_current_team(controller)
            else:
                logging.info("NOT READING")
                self.timeouts[controller] = time.time_ns() + BUZZ_PENALTY_TIMEOUT

    def __handle_sos_buzz(self, controller: int, color: str):
        if self.reading:
            if color in {"green", "orange"}:
                self.controllers_used_in_current_question.append(controller)
            if color == "green":
                logging.info("SOS SPLIT")
                self.__split_or_steal(controller, False)
            elif color == "orange":
                logging.info("SOS STEAL")
                self.__split_or_steal(controller, True)
        else:
            logging.info("NOT READING")

    def buzz(self, controller: int, color: str):
        """action for a team buzzing

        Args:
            controller (int): the id of the controller
            color (str): color pressed
        """
        logging.info("BUZZ: %d %s", controller, color)

        if self.__team_allowed_to_play(controller):
            if self.state == States.SPLIT_OR_STEAL:
                self.__handle_sos_buzz(controller, color)
            else:
                self.__handle_normal_buzz(controller, color)

    def select_question(self, identifier: int):
        """select a new question

        Args:
            identifier (int): id of the question to select
        """
        logging.debug("SELECT QUESTION: %d", identifier)
        self.questions_controller.select_question(identifier)
        self.state = States.READING_QUESTION

    def skip_question(self):
        """skip the current question"""
        logging.debug("SKIP QUESTION")

        self.questions_controller.skip()
        self.controllers_used_in_current_question = []
        self.teams_controller.set_current_playing(0)

        if self.questions_controller.questions_over():
            if self.teams_controller.is_tie():
                self.questions_controller.tiebreak()
                self.state = States.READING_QUESTION
            else:
                self.__goto_end_game()
        else:
            self.state = States.SELECTING_QUESTION
        self.__set_reading(False)
        self.actions.reset_countdown_timer()

    def __goto_end_game(self):
        t = self.teams_controller.get_winning_team()
        if len(t.names) > 1 and SPLIT_OR_STEAL:
            self.teams_controller.playing = list(range(len(t.names)))
            self.state = States.SPLIT_OR_STEAL
        else:
            self.__game_over()

    def __set_reading(self, value: bool):
        self.reading = value
        try:
            if value:
                self.controllers.turn_light_on(self.__get_teams_allowed_to_play())
            else:
                self.controllers.turn_light_off([0, 1, 2, 3])
        except requests_ConnectionError:
            logging.error("Failed to connect to buzz controllers")

    def set_answering(self):
        """set the state as someone answering"""
        logging.debug("Waiting for answer")
        if self.state != States.SPLIT_OR_STEAL:
            self.state = States.ANSWERING_QUESTION
            self.reading_until = time.time_ns() + TIME_TO_ANSWER
        self.actions.play_start_accepting = True
        self.__set_reading(True)

    def answer_question(self, correct: bool):
        """action for team answering question

        Args:
            correct (bool): the answer is correct
        """
        logging.debug("Question answered %s", correct)
        self.reset_sound()

        self.questions_controller.answer(self.get_current_team(), correct)

        if correct:
            self.actions.play_correct_sound = True
            self.teams_controller.set_selecting_as_current()
        else:
            self.actions.play_wrong_sound = True

            if (
                len(self.controllers_used_in_current_question) == 4
            ):  # if all teams answered incorrectly
                self.teams_controller.next_selecting()

        if not correct and len(self.controllers_used_in_current_question) != 4:
            self.state = States.READING_QUESTION
        else:
            self.state = States.SELECTING_QUESTION
            self.controllers_used_in_current_question = []

        if self.questions_controller.questions_over():
            if self.teams_controller.is_tie():
                self.questions_controller.tiebreak()
                self.state = States.READING_QUESTION
            else:
                self.__goto_end_game()
        self.__set_reading(False)
        self.actions.reset_countdown_timer()

    def __return_sos_answers(self):
        return self.state in {States.SPLIT_OR_STEAL, States.OVER}

    def to_dict(self) -> dict:
        """
            cast the state as a dictionary to represent as json object
        Returns:
            dict: the gamestate data
        """
        selecting_team = self.teams_controller.get_selecting_team()
        current_team = self.teams_controller.get_current_team()

        return {
            "teams": [p.to_dict() for p in self.list_teams()],
            "questions": [q.to_dict() for q in self.list_questions()],
            "state": self.state.value,
            "currentQuestion": self.questions_controller.get_current_question().to_dict(),
            "currentTeam": current_team.id if current_team is not None else None,
            "selectingTeam": (
                selecting_team.id if selecting_team is not None else None
            ),
            "alreadyAnswered": self.controllers_used_in_current_question,
            "SOSAnswers": (
                self.__get_sos_values() if self.__return_sos_answers() else []
            ),
            "actions": self.actions.to_dict(),
        }

    def add_points(self, team_id: int, points: int):
        """add points to a team

        Args:
            team_id (int): the id of the team
            points (int): the points to add
        """
        self.teams_controller.add_points(team_id, points)

    def __team_allowed_to_play(self, team_id: int) -> bool:
        """check if a team is allowed to play

        Args:
            team_id (int): id of the team to check

        Returns:
            bool: if the team can play
        """
        return (
            not self.team_already_answered(team_id)
            and team_id in self.__get_allowed_controllers()
        )

    def __get_teams_allowed_to_play(self) -> List[int]:
        """list teams allowed to play

        Returns:
            List[int]: teams allowed to play
        """
        return list(
            set(self.__get_allowed_controllers())
            - set(self.controllers_used_in_current_question)
        )

    def team_already_answered(self, team_id: int) -> bool:
        """check if team already answered

        Args:
            team_id (int): the id of the team to check if already answered

        Returns:
            bool: if the team already answered
        """
        return team_id in self.controllers_used_in_current_question

    def list_teams(self) -> List[Team]:
        """return the list of teams

        Returns:
            List[Team]: the teams in the game
        """
        return self.teams_controller.list_teams()

    def list_questions(self) -> List[Question]:
        """return the list of questions"""
        return self.questions_controller.list_questions()

    def reset_sound(self):
        """
        Set sounds playing to false
        """
        self.actions.reset_sound()

    def stop_countdown_timer(self):
        """stop the countdown timer"""
        self.actions.stop_countdown = True

    def get_question(self, idx: int) -> Question:
        """set a question by idstop_countdown

        Args:
            idx (int): the index of the question
        """
        return self.questions_controller.get_question(idx)
