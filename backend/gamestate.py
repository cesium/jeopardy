"""Module responsable for storing the state of the game"""

from enum import Enum
from typing import List
import json
from models import Player, Question


class States(Enum):
    """Enumeration for possible states of the game"""

    STARTING = 0
    SELECTING_QUESTION = 1
    READING_QUESTION = 2
    ANSWERING_QUESTION = 3
    PLAYER_SELECTED = 4
    OVER = 5


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

    def __answer_correctly(self, player: Player):
        """action for a player answering a question correctly

        Args:
            player (Player): player that answered the question
        """
        self.questions[self.current_question_idx].answer_correctly(player)

    def __answer_incorreclty(self, player: Player):
        """action for a player answering a question incorrectly

        Args:
            player (Player): player that answered the question
        """
        self.questions[self.current_question_idx].answer_incorreclty(player)

    def everyone_answered_current(self) -> bool:
        """check if everyone already answered the current question

        Returns:
            bool: everyone already answered the current question
        """
        return self.questions[self.current_question_idx].everyone_answered()

    def answer(self, player: Player, correct: bool):
        """action for answering a question

        Args:
            player (Player): player that answered
            correct (bool): the answer is correct
        """
        if correct:
            self.__answer_correctly(player)
        else:
            self.__answer_incorreclty(player)

    def list_questions(self) -> List[Question]:
        """lists all question in the game

        Returns:
            List[Question]: list of all question in the game
        """
        return self.questions.copy()

    def get_players_answered(self) -> List[Player]:
        """list all players that answered the question

        Returns:
            List[Question]: list of players that answered the current question
        """
        return self.questions[self.current_question_idx].players_answered.copy()

    def player_answered(self, player: Player) -> bool:
        """check if player answered question

        Args:
            player (Player): player to check if answered

        Returns:
            bool: player already answered
        """
        return player in self.questions[self.current_question_idx].players_answered

    def get_question(self, idx: int):
        """gets a question by id

        Args:
            idx (int): the index of the question

        Raises:
            ValueError: idx is none
            ValueError: idx is invalid
        """
        if idx is None:
            raise ValueError("Invalid")
        if self.in_tiebreak:
            self.current_question_idx += 1
        else:
            if idx < 0 or idx >= len(self.questions):
                raise ValueError("Index out of bonds")
            self.current_question_idx = idx


class PlayersController:
    """Class for controling players atributes withtin the game"""

    def __init__(self):
        self.players: List[Player] = []
        self.current_playing_idx: int = 0
        self.selecting_idx: int = 0
        self.playing: List[int] = []

    def get_current_player(self) -> Player:
        """get the player playing

        Returns:
            Player: the player playing
        """
        if self.players == []:
            return None
        return self.players[self.current_playing_idx]

    def get_player(self, idx: int) -> Player:
        """get player with given id

        Args:
            idx (int): id of player

        Returns:
            Player: player with given id
        """
        if self.players == []:
            return None
        return self.players[idx]

    def get_selecting_player(self) -> Player:
        """get the player selecting

        Returns:
            Player: the player selecting
        """
        if self.players == []:
            return None
        return self.players[self.selecting_idx]

    def set_players(self, players_names: List[str]):
        """creates the players with the given names

        Args:
            players_names (List[str]): list of names
        """
        self.players = [Player(idx, name) for idx, name in enumerate(players_names)]
        self.current_playing_idx = 0
        self.selecting_idx = 0
        self.playing = list(range(4))

    def set_selecting(self, idx: int):
        """set player with given id as selecting

        Args:
            idx (int): id of player to set as selecting
        """
        self.selecting_idx = idx

    def set_current_playing(self, idx: int):
        """set player with given id as playing

        Args:
            idx (int): id of player to set as playing
        """
        self.current_playing_idx = idx

    def is_tie(self) -> bool:
        """check if the players are in a tie

        Returns:
            bool: the players are in a tie
        """
        max_tokens = max(p.balance for p in self.players)
        players_with_max_tokens = [
            p.id for p in self.players if p.balance == max_tokens
        ]
        if len(players_with_max_tokens) > 1:
            self.playing = players_with_max_tokens
            return True
        return False

    def next_selecting(self):
        """make the next player in line be the selecting one"""
        self.selecting_idx = (self.selecting_idx + 1) % 4

    def set_selecting_as_current(self):
        """make the player playing as the selecting"""
        self.selecting_idx = self.current_playing_idx

    def list_players(self) -> List[Player]:
        """return the list of the players in the game

        Returns:
            List[Player]: list of players in the game
        """
        return self.players.copy()


class GameState:
    """Class to store the state of the game"""

    def __init__(self):
        self.questions_controller = QuestionsController()
        self.players_controller = PlayersController()
        self.state: States = States.STARTING
        self.play_correct_sound: bool = False
        self.play_wrong_sound: bool = False

    def get_current_question(self) -> Question:
        """return the question being used at the moment

        Returns:
            Question: the question being used
        """
        return self.questions_controller.get_current_question()

    def get_current_player(self) -> Player:
        """return the player playing

        Returns:
            Player: the player playing
        """
        return self.players_controller.get_current_player()

    def get_players_answered_current_question(self) -> List[Player]:
        """return the players that answered the current question

        Returns:
            List[Player]: list of players that answered the current question
        """
        return self.questions_controller.get_players_answered()

    def get_allowed_players(self) -> List[int]:
        """return the players that are allowed to play

        Returns:
            List[int]: list of players that are allowed to play
        """
        return self.players_controller.playing

    def set_players(self, players_names: List[str]):
        """sets the players playing

        Args:
            players_names (List[str]): list of the names of the players

        Raises:
            AssertionError: if players are set mid game
        """
        if self.state != States.STARTING:
            raise AssertionError("Cannot set players mid game")
        self.players_controller.set_players(players_names)
        self.state = States.SELECTING_QUESTION

    def set_current_player(self, player_idx: int):
        """set a new player as playing

        Args:
            player_idx (int): the id of the player
        """
        self.players_controller.set_current_playing(player_idx)
        self.state = States.PLAYER_SELECTED

    def select_question(self, identifier: int):
        """select a new question

        Args:
            identifier (int): id of the question to select
        """
        print(identifier)
        self.questions_controller.select_question(identifier)
        self.state = States.READING_QUESTION

    def skip_question(self):
        """skip the current question"""
        self.questions_controller.skip()
        self.players_controller.set_current_playing(0)

        if self.questions_controller.questions_over():
            if self.players_controller.is_tie():
                self.questions_controller.tiebreak()
                self.state = States.READING_QUESTION
            else:
                self.state = States.OVER
        else:
            self.state = States.SELECTING_QUESTION

    def set_answering(self):
        """set the state as someone answering"""
        self.state = States.ANSWERING_QUESTION

    def answer_question(self, correct: bool):
        """action for player answering question

        Args:
            correct (bool): the answer is correct
        """
        self.reset_sound()

        self.questions_controller.answer(self.get_current_player(), correct)

        if correct:
            self.play_correct_sound = True
            self.players_controller.set_selecting_as_current()
        else:
            self.play_wrong_sound = True

            if (
                self.questions_controller.everyone_answered_current()
            ):  # if all players answered incorrectly
                self.players_controller.next_selecting()

        # self.players_controller.set_current_playing(0)

        if not correct and not self.questions_controller.everyone_answered_current():
            self.state = States.READING_QUESTION
        else:
            self.state = States.SELECTING_QUESTION

        if self.questions_controller.questions_over():
            if self.players_controller.is_tie():
                self.state = States.READING_QUESTION
                self.questions_controller.tiebreak()
            else:
                self.state = States.OVER

    def to_dict(self) -> dict:
        """
            cast the state as a dictionary to represent as json object
        Returns:
            dict: the gamestate data
        """
        selecting_player = self.players_controller.get_selecting_player()
        current_player = self.players_controller.get_current_player()

        return {
            "players": [p.to_dict() for p in self.list_players()],
            "questions": [q.to_dict() for q in self.list_questions()],
            "state": self.state.value,
            "currentQuestion": self.get_current_question().to_dict(),
            "currentPlayer": current_player.id if current_player is not None else None,
            "selectingPlayer": (
                selecting_player.id if selecting_player is not None else None
            ),
            "alreadyAnswered": [
                p.id
                for p in self.questions_controller.get_current_question().players_answered
            ],
            "playCorrectSound": self.play_correct_sound,
            "playWrongSound": self.play_wrong_sound,
        }

    def player_allowed_to_play(self, player_id: int) -> bool:
        """check if player is allowed to play"""
        return player_id in self.get_allowed_players()

    def player_already_answered(self, player_id: int) -> bool:
        """check if player already answered"""
        return (
            self.players_controller.get_player(player_id)
            in self.get_players_answered_current_question()
        )

    def list_players(self) -> List[Player]:
        """return the list of players"""
        return self.players_controller.list_players()

    def list_questions(self) -> List[Question]:
        """return the list of questions"""
        return self.questions_controller.list_questions()

    def reset_sound(self):
        """
        Set both sound playing to false
        """
        self.play_correct_sound = False
        self.play_wrong_sound = True

    def get_question(self, idx: int) -> Question:
        """get a question by id

        Args:
            idx (int): the index of the question
        """
        return self.questions_controller.get_question(idx)
