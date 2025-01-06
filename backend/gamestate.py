import os
from models import Player, Question
from typing import List
from enum import Enum
import json

class States(Enum):
    STARTING = 0
    SELECTING_QUESTION = 1
    READING_QUESTION = 2
    ANSWERING_QUESTION = 3
    PLAYER_SELECTED = 4
    OVER = 5

class QuestionsController:
    """
        Controller for questions
    """
    def __init_questions(self):
        """Generate questions from questions.json

        Raises:
            ValueError: An even number of tiebreaker questions were given in the json
        """
        id = 0
        with open("backend/questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
            for category,questions in data["regular"].items():
                for question in questions:
                    self.questions.append(Question(id, question["question"], question["answer"], question["image"], question["value"], category))
                    id += 1
            for question in data["tiebreaker"]:
                self.tiebreak_questions.append(Question(id, question["question"], question["answer"], question["image"], 100, "Tiebreak", True))
                id += 1
            if len(self.tiebreak_questions) % 2 == 0: # Make sure there are an odd number of tiebreak questions
                raise ValueError("There must be an odd number of tiebreak questions")
            
            self.current_question_idx = 0

    def __init__(self):
        self.questions : List[Question] = []
        self.current_question_idx : int = None
        self.tiebreak_questions : List[Question] = []
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
        else:
            return self.questions[self.current_question_idx]
    
    def select_question(self, id : int = None):
        """Sets a new question as the one being played

        Args:
            id (int, optional): the index of the question aka its id. Defaults to None.

        Raises:
            ValueError: Id is invalid
        """
        if id is None and not self.in_tiebreak:
            raise ValueError("No question selected")
        if self.in_tiebreak:
            self.current_question_idx+=1
        else:
            if id < 0 or id >= len(self.questions):
                raise ValueError("Index out of bonds")
            self.current_question_idx = id
    
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
        makes the game be in a tiebreak state either setting it as a tiebreak selecting the next question
        """
        if not self.in_tiebreak:
            self.current_question_idx = 0
            self.in_tiebreak = True
        else:
            self.current_question_idx += 1
    
    def __answer_correctly(self,player:Player):
        """action for a player answering a question correctly

        Args:
            player (Player): player that answered the question
        """
        self.questions[self.current_question_idx].answerCorrectly(player)
    
    def __answer_incorreclty(self,player:Player):
        """action for a player answering a question incorrectly

        Args:
            player (Player): player that answered the question
        """
        self.questions[self.current_question_idx].answerIncorreclty(player)
    
    def everyone_answered_current(self) ->  bool:
        """ check if everyone already answered the current question

        Returns:
            bool: everyone already answered the current question
        """
        return self.questions[self.current_question_idx].everyone_answered()

    
    def answer(self,player:Player,correct:bool):
        """action for answering a question

        Args:
            player (Player): player that answered
            correct (bool): the answer is correct
        """
        if correct:
            self.__answer_correctly(player)
        else:
            self.__answer_incorreclty(player)
    
    def list_questions(self)-> List[Question]:
        """lists all question in the game

        Returns:
            List[Question]: list of all question in the game
        """
        return self.questions.copy()
    def get_players_answered(self) -> List[Player]:
        """ list all players that answered the question

        Returns:
            List[Question]: list of players that answered the current question
        """
        return self.questions[self.current_question_idx].playersAnswered.copy()
    def player_answered(self,player: Player) -> bool:
        """ check if player answered question

        Args:
            player (Player): player to check if answered

        Returns:
            bool: player already answered
        """
        return player in self.questions[self.current_question_idx].playersAnswered
        
        

class PlayersController:
    def __init__(self):
        self.players : List[Player] = []
        self.current_playing_idx : int = 0
        self.selecting_idx : int = 0
        self.playing : List[int] = []
    
    def get_current_player(self) -> Player:
        """get the player playing

        Returns:
            Player: the player playing
        """
        if self.players==[]:
            return None
        return self.players[self.current_playing_idx]
    def get_player(self, idx: int) -> Player:
        """get player with given id

        Args:
            idx (int): id of player

        Returns:
            Player: player with given id
        """
        if self.players==[]:
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
    
    def set_players(self, players_names : List[str]):
        """creates the players with the given names 

        Args:
            players_names (List[str]): list of names
        """
        self.players = [Player(idx,name) for idx,name in enumerate(players_names)]
        self.current_playing_idx = 0
        self.selecting_idx = 0
        self.playing = list(range(4))
    
    def set_selecting(self, idx: int):
        """set player with given id as selecting

        Args:
            idx (int): id of player to set as selecting
        """
        self.selecting_idx = idx
    
    def set_current_playing(self, idx : int):
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
        max_tokens = max([p.balance for p in self.players])
        players_with_max_tokens = [p.id for p in self.players if p.balance == max_tokens]
        if len(players_with_max_tokens) > 1:
            self.playing = players_with_max_tokens
            return True
        else:
            return False
    def next_selecting(self):
        """make the next player in line be the selecting one
        """
        self.selecting_idx = (self.selecting_idx + 1) % 4
    def set_selecting_as_current(self):
        """make the player playing as the selecting
        """
        self.selecting_idx = self.current_playing_idx
    def list_pLayers(self) -> List[Player]:
        """ return the list of the players in the game

        Returns:
            List[Player]: list of players in the game
        """
        return self.players.copy()

    
class GameState:
    def __init__(self):
        self.questionsController = QuestionsController()
        self.playersController = PlayersController()
        self.state : States = States.STARTING
        self.playCorrectSound : bool = False
        self.playWrongSound : bool = False
        
    def get_current_question(self) -> Question:
        """ return the question being used at the moment

        Returns:
            Question: the question being used
        """
        return self.questionsController.get_current_question()
    
    def get_current_player(self) -> Player:
        """ return the player playing

        Returns:
            Player: the player playing
        """
        return self.playersController.get_current_player()
    
    def get_players_answered_current_question(self) -> List[Player]:
        """ return the players that answered the current question

        Returns:
            List[Player]: list of players that answered the current question
        """
        return self.questionsController.get_players_answered()

    def get_allowed_players(self) -> List[int]:
        """ return the players that are allowed to play

        Returns:
            List[int]: list of players that are allowed to play
        """
        return self.playersController.playing
        
    def set_players(self, players_names : List[str]):
        """sets the players playing

        Args:
            players_names (List[str]): list of the names of the players

        Raises:
            AssertionError: if players are set mid game
        """
        if self.state != States.STARTING:
            raise AssertionError("Cannot set players mid game")
        self.playersController.set_players(players_names)
        self.state = States.SELECTING_QUESTION

    def set_current_player(self, player_idx : int):
        """ set a new player as playing
    
        Args:
            player_idx (int): the id of the player
        """
        self.playersController.set_current_playing(player_idx)
        self.state = States.PLAYER_SELECTED

    def select_question(self, id:int):
        """ select a new question

        Args:
            id (int): id of the question to select
        """
        print(id)
        self.questionsController.select_question(id)
        self.state = States.READING_QUESTION
    
    def skip_question(self):
        """skip the current question
        """
        self.questionsController.skip()
        self.playersController.set_current_playing(0)
        
        if self.questionsController.questions_over():
            if self.playersController.is_tie():
                self.questionsController.tiebreak()
                self.state = States.READING_QUESTION
            else:
                self.state = States.OVER
        else:
            self.state = States.SELECTING_QUESTION


    def set_answering(self):
        """set the state as someone answering
        """
        self.state = States.ANSWERING_QUESTION
    
    def answer_question(self, correct:bool):
        """action for player answering question

        Args:
            correct (bool): the answer is correct
        """
        self.playCorrectSound = False
        self.playWrongSound = False
        
        self.questionsController.answer(self.get_current_player(), correct)

        if correct:
            self.playCorrectSound = True
            self.someoneAnsweredCorrectly = True     
            self.playersController.set_selecting_as_current()
        else:
            self.playWrongSound = True
            
            if self.questionsController.everyone_answered_current(): # if all players answered incorrectly
                self.playersController.next_selecting()
    
        #self.playersController.set_current_playing(0)
        
        
        if not correct and not self.questionsController.everyone_answered_current():
            self.state = States.READING_QUESTION
        else:
            self.state = States.SELECTING_QUESTION

        if self.questionsController.questions_over():
            if self.playersController.is_tie():
                self.state = States.READING_QUESTION
                self.questionsController.tiebreak()
            else:
                self.state = States.OVER

    def to_JSON(self):
        selecting_player = self.playersController.get_selecting_player()
        current_player = self.playersController.get_current_player()
        dict = {
            "players": [p.toDict() for p in self.playersController.list_pLayers()],
            "questions": [q.toDict() for q in self.questionsController.list_questions()],
            "state": self.state.value,
            "currentQuestion": self.questionsController.get_current_question().toDict(),
            "currentPlayer": current_player.id if current_player is not None else None,
            "selectingPlayer": selecting_player.id if selecting_player is not None else None,
            "alreadyAnswered": [p.id for p in self.questionsController.get_current_question().playersAnswered],
            "playCorrectSound": self.playCorrectSound,
            "playWrongSound": self.playWrongSound,
        }
        return json.dumps(dict)
    
    def player_allowed_to_play(self, player_id):
        return player_id in self.get_allowed_players()
    
    def player_already_answered(self, player_id):
        
        return self.playersController.get_player(player_id) in self.get_players_answered_current_question()

