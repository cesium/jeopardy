import os
from question import Question
from player import Player
from enum import Enum
import json

class States(Enum):
    STARTING = 0
    SELECTING_QUESTION = 1
    READING_QUESTION = 2
    ANSWERING_QUESTION = 3
    PLAYER_SELECTED = 4
    OVER = 5
    
class GameState:
    def setPlayers(self, players):
        if self.state != States.STARTING:
            raise AssertionError("Cannot set players mid game")
        self.players = [Player(player) for player in players]
        self.state = States.SELECTING_QUESTION
        self.currentPlayer = self.players[0]

    def setCurrentPlayer(self, player):
        self.currentPlayer = self.players[player]
        self.state = States.PLAYER_SELECTED

    def __init__(self):
        self.players = []
        self.questions = [] 
        self.initQuestions()
        self.state = States.STARTING
        self.currentQuestion = None
        self.currentPlayer = Player("Ola")
    def initQuestions(self):
        id = 0
        for file in os.listdir("backend/perguntas"):
            category = file[:-4]
            value = 0
            f = open("backend/perguntas/"+file, "r", encoding="utf-8")
            while True:
                question = f.readline()
                answer = f.readline()
                value += 100
                if not question: #TODO: validar número de linhas par
                    break
                self.questions.append(Question(id, question.strip(), answer.strip(), value, category))
                id += 1
    def selectQuestion(self, id):
        if id < 0 or id >= len(self.questions):
            raise ValueError("Index out of bonds")
        self.currentQuestion = id
        self.state = States.READING_QUESTION
    
    def setAnswering(self):
        self.state = States.ANSWERING_QUESTION

    def is_over(self):
        return len(list(filter(lambda q: q.answered, self.questions))) == 0
    
    def answerQuestion(self, correct):
        if self.currentQuestion is None:
            raise ValueError("No question is being answered")
        elif self.currentPlayer is None:
            raise ValueError("No player chosen yet")
        self.questions[self.currentQuestion].answered = True

        if correct:
            self.currentPlayer.addPoints(self.questions[self.currentQuestion].value)
        else:
            self.currentPlayer.addPoints(-1 * self.questions[self.currentQuestion].value)
        
        self.currentPlayer = self.players[0]
        
        if self.is_over():
            self.state = States.OVER
        else:
            self.state = States.SELECTING_QUESTION

    def toJSON(self):
        dict = {
            "players": [p.__dict__ for p in self.players],
            "questions": [q.__dict__ for q in self.questions],
            "state": self.state.value,
            "currentQuestion": self.currentQuestion,
            "currentPlayer": None if self.currentPlayer is None else self.currentPlayer.__dict__
        }
        return json.dumps(dict)

