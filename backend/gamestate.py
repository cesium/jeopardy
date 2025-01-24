# pylint: disable=too-many-instance-attributes
"""Module responsable for storing the state of the game"""

from enum import Enum
from typing import List
import json
import os
import time
import logging
from models import Team, Question
from buzz_interface import Buzz
from requests.exceptions import ConnectionError as requests_ConnectionError


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


class QuestionsController:
    """Class for controling questions atributes withtin the game"""

    def __init_questions(self):
        """Generate questions from questions.json

        Raises:
            ValueError: An even number of tiebreaker questions were given in the json
        """
        idx = 0
        with open("backend/questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)

            for category, questions in data["regular"].items():
                for question in questions:
                    self.questions.append(
                        Question(
                            idx,
                            question["question"],
                            question["answer"],
                            question["image"],
                            question["value"],
                            category,
                        )
                    )
                    idx += 1
            for question in data["tiebreaker"]:
                self.tiebreak_questions.append(
                    Question(
                        idx,
                        question["question"],
                        question["answer"],
                        question["image"],
                        100,
                        "Tiebreak",
                        True,
                    )
                )
                idx += 1
            if (
                len(self.tiebreak_questions) % 2 == 0
            ):  # Make sure there are an odd number of tiebreak questions
                raise ValueError("There must be an odd number of tiebreak questions")

            self.current_question_idx = 0

    def __init__(self):
        self.questions: List[Question] = []
        self.current_question_idx: int = None
        self.tiebreak_questions: List[Question] = []
        self.in_tiebreak = False
        self.__init_questions()

    def get_current_question(self) -> Question:
        """
            Fetches the question being played

        Returns:
            Question: The current question
        """
        if self.in_tiebreak:
            return self.tiebreak_questions[self.current_question_idx]
        return self.questions[self.current_question_idx]

    def select_question(self, idx: int = None):
        """Sets a new question as the one being played

        Args:
            idx (int, optional): the index of the question aka its id. Defaults to None.

        Raises:
            ValueError: idx is invalid
        """
        if idx is None and not self.in_tiebreak:
            raise ValueError("No question selected")
        if self.in_tiebreak:
            self.current_question_idx += 1
        else:
            if idx < 0 or idx >= len(self.questions):
                raise ValueError("Index out of bonds")
            self.current_question_idx = idx

    def questions_over(self) -> bool:
        """checks if all questions have benn answered

        Returns:
            bool: are all questions answered
        """
        return all(map(lambda q: q.answered, self.questions))

    def skip(self):
        """
        Skips the current question
        """
        self.questions[self.current_question_idx].skip()

    def tiebreak(self):
        """
        makes the game be in a tiebreak state
        if already in a tiebreak state selects the next question
        """
        if not self.in_tiebreak:
            self.current_question_idx = 0
            self.in_tiebreak = True
        else:
            self.current_question_idx += 1

    def __answer_correctly(self, team: Team):
        """action for a team answering a question correctly

        Args:
            team (Team): team that answered the question
        """
        self.questions[self.current_question_idx].answer_correctly(team)

    def __answer_incorreclty(self, team: Team):
        """action for a team answering a question incorrectly

        Args:
            team (Team): team that answered the question
        """
        self.questions[self.current_question_idx].answer_incorreclty(team)

    def answer(self, team: Team, correct: bool):
        """action for answering a question

        Args:
            team (Team): team that answered
            correct (bool): the answer is correct
        """
        if correct:
            self.__answer_correctly(team)
        else:
            self.__answer_incorreclty(team)

    def list_questions(self) -> List[Question]:
        """lists all question in the game

        Returns:
            List[Question]: list of all question in the game
        """
        return self.questions.copy()

    def get_question(self, idx: int) -> Question:
        """gets a question by id

        Args:
            idx (int): the index of the question

        Raises:
            ValueError: idx is none
            ValueError: idx is invalid
        """
        if idx is None or idx < 0 or idx >= len(self.questions):
            return None
        return self.questions[idx]


class TeamsController:
    """Class for controling teams atributes withtin the game"""

    def __init__(self):
        self.teams: List[Team] = []
        self.current_playing_id: int = 0
        self.selecting_id: int = 0
        self.playing: List[int] = []

    def get_current_team(self) -> Team:
        """get the team playing

        Returns:
            Team: the team playing
        """
        if self.teams == []:
            return None
        return self.teams[self.current_playing_id]

    def get_team(self, idx: int) -> Team:
        """get team with given id

        Args:
            idx (int): id of team

        Returns:
            Team: team with given id
        """
        if self.teams == []:
            return None
        return self.teams[idx]

    def get_selecting_team(self) -> Team:
        """get the team selecting

        Returns:
            Team: the team selecting
        """
        if self.teams == []:
            return None
        return self.teams[self.selecting_id]

    def set_teams(self, player_teams_names: List[List[str]]):
        """creates the teams with the given names

        Args:
            teams_names (List[str]): list of names
        Raises:
            ValueError: Too many teams (max 4)
            ValueError: Too many players in a team (max 4)
        """
        if len(player_teams_names) > 4:
            raise ValueError("Too many teams (max 4)")
        for t in player_teams_names:
            if len(t) > 4:
                raise ValueError("Too many players in a team (max 4)")
        self.teams = [Team(idx, names) for idx, names in enumerate(player_teams_names)]
        self.current_playing_id = 0
        self.selecting_id = 0
        self.playing = list(range(len(player_teams_names)))

    def split_or_steal(self, votes: List[int]):
        """split or steal the balance of the team

        Args:
            members (List[int]): list of members that stole.
        """
        logging.debug("Split or Steal: [%s]", ",".join(str(v) for v in votes))
        team = self.get_winning_team()
        if len(votes) > 1:
            team.balance = 0
        elif len(votes) == 1:
            stealer = votes[0]
            new_id = len(self.teams)
            self.teams.append(Team(new_id, [team.names[stealer]]))
            self.teams[new_id].balance = team.balance
            team.balance = 0
            del team.names[stealer]

    def set_selecting(self, idx: int):
        """set team with given id as selecting

        Args:
            idx (int): id of team to set as selecting
        """
        self.selecting_id = idx

    def set_current_playing(self, idx: int):
        """set team with given id as playing

        Args:
            idx (int): id of team to set as playing
        """
        self.current_playing_id = idx

    def is_tie(self) -> bool:
        """check if the teams are in a tie

        Returns:
            bool: the teams are in a tie
        """
        max_tokens = max(p.balance for p in self.teams)
        teams_with_max_tokens = [p.id for p in self.teams if p.balance == max_tokens]
        if len(teams_with_max_tokens) > 1:
            self.playing = teams_with_max_tokens
            return True
        return False

    def get_winning_team(self) -> Team:
        """get the winning team

        Returns:
            Team: the winning team
        """
        if self.teams == []:
            return None
        c = self.teams[0]
        for t in self.teams[1:]:
            if t.balance > c.balance:
                c = t
        return c

    def next_selecting(self):
        """make the next team in line be the selecting one"""
        self.selecting_id = (self.selecting_id + 1) % 4

    def set_selecting_as_current(self):
        """make the team playing as the selecting"""
        self.selecting_id = self.current_playing_id

    def list_teams(self) -> List[Team]:
        """return the list of the teams in the game

        Returns:
            List[Team]: list of teams in the game
        """
        return self.teams.copy()


class Actions:
    """Class for controling actions atributes withtin the game"""

    def __init__(self):
        self.play_correct_sound: bool = False
        self.play_wrong_sound: bool = False
        self.play_start_accepting: bool = False
        self.play_buzzer_sound: bool = False
        self.stop_countdown: bool = False

    def reset_sound(self):
        """
        Set both sound playing to false
        """
        self.play_correct_sound = False
        self.play_wrong_sound = False
        self.play_start_accepting = False
        self.play_buzzer_sound = False

    def reset_countdown_timer(self):
        """reset the countdown timer"""
        self.stop_countdown = False

    def to_dict(self) -> dict:
        """
            cast the state as a dictionary to represent as json object
        Returns:
            dict: the gamestate data
        """
        return {
            "playCorrectSound": self.play_correct_sound,
            "playWrongSound": self.play_wrong_sound,
            "playStartAccepting": self.play_start_accepting,
            "playBuzzerSound": self.play_buzzer_sound,
            "stopTimer": self.stop_countdown,
        }


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

    def get_current_team(self) -> Team:
        """return the team playing

        Returns:
            Team: the team playing
        """
        return self.teams_controller.get_current_team()

    def get_controllers_answered_current_question(self) -> List[int]:
        """return the controllers that answered the current question

        Returns:
            List[int]: list of controllers that answered the current question
        """
        return self.controllers_used_in_current_question

    def get_allowed_controllers(self) -> List[int]:
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
            option (bool): the option the controller chose
        """
        logging.debug("Split or Steal: %d %s", controller, option)
        self.controllers_used_in_current_question.append(controller)
        self.sos_steal[controller] = option
        print(self.sos_steal)
        print(self.teams_controller.playing)
        if len(self.sos_steal) == len(self.teams_controller.playing):
            stealers = [i for i, k in self.sos_steal.items() if k]
            self.teams_controller.split_or_steal(stealers)
            self.state = States.OVER

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

        if self.team_allowed_to_play(controller):
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
                self.__end_game()
        else:
            self.state = States.SELECTING_QUESTION
        self.__set_reading(False)
        self.actions.reset_countdown_timer()

    def __end_game(self):
        t = self.teams_controller.get_winning_team()
        if len(t.names) > 1 and SPLIT_OR_STEAL:
            self.teams_controller.playing = list(range(len(t.names)))
            self.state = States.SPLIT_OR_STEAL
        else:
            self.state = States.OVER

    def __set_reading(self, value: bool):
        self.reading = value
        try:
            if value:
                self.controllers.turn_light_on(self.get_teams_allowed_to_play())
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
                self.__end_game()
        self.__set_reading(False)
        self.actions.reset_countdown_timer()

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
            "actions": self.actions.to_dict(),
        }

    def team_allowed_to_play(self, team_id: int) -> bool:
        """check if a team is allowed to play

        Args:
            team_id (int): id of the team to check

        Returns:
            bool: if the team can play
        """
        return (
            not self.team_already_answered(team_id)
            and team_id in self.get_allowed_controllers()
        )

    def get_teams_allowed_to_play(self) -> List[int]:
        """list teams allowed to play

        Returns:
            List[int]: teams allowed to play
        """
        return list(
            set(self.get_allowed_controllers())
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
        """set a question by id

        Args:
            idx (int): the index of the question
        """
        return self.questions_controller.get_question(idx)
