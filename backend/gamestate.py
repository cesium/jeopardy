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
        self.allowedPlayers = [0,1,2,3]

    def setCurrentPlayer(self, player):
        self.currentPlayer = self.players[player]
        self.state = States.PLAYER_SELECTED

    def __init__(self):
        self.players = []
        self.questions = [] 
        self.tiebreakQuestions = []
        self.initQuestions()
        self.state = States.STARTING
        self.currentQuestion = None
        self.currentPlayer = Player("Ola")
        self.selectingPlayer = 0
        self.oneAnsweredCorrectly = False
        self.alreadyAnswered = []
        self.tiebreakIndex = -1
        self.allowedPlayers = []

    def initQuestions(self):
        id = 0
        for file in os.listdir("backend/perguntas/regular"):
            category = file[:-4]
            value = 0
            f = open("backend/perguntas/regular/"+file, "r", encoding="utf-8")
            while True:
                question = f.readline()
                answer = f.readline()
                value += 100
                if not question: #TODO: validar número de linhas par
                    break
                self.questions.append(Question(id, question.strip(), answer.strip(), value, category))
                id += 1

        f = open("backend/perguntas/tiebreak.txt", "r", encoding="utf-8")
        while True:
            question = f.readline()
            answer = f.readline()
            if not question: #TODO: validar número de linhas par
                break
            self.tiebreakQuestions.append(Question(id, question.strip(), answer.strip(), 100, "Tiebreak"))
            id += 1

    def selectQuestion(self, id):
        print(id)
        if id < 0 or id >= len(self.questions):
            raise ValueError("Index out of bonds")
        self.currentQuestion = self.questions[id]
        self.state = States.READING_QUESTION
    
    def skipQuestion(self):
        self.currentQuestion.answered = True
        self.currentPlayer = self.players[0]
        self.alreadyAnswered = []
        
        if self.is_over():
            if(self.is_tiebreak()):
                self.state = States.READING_QUESTION
                self.tiebreakIndex += 1
                self.currentQuestion = self.tiebreakQuestions[self.tiebreakIndex]
            else:
                self.state = States.OVER
        else:
            self.state = States.SELECTING_QUESTION


    def setAnswering(self):
        self.state = States.ANSWERING_QUESTION

    def is_over(self):
        return len(list(filter(lambda q: not q.answered, self.questions))) == 0
    
    def is_tiebreak(self):
        maxTokens = -1e9
        maxPlayers = []

        for i,p in enumerate(self.players):
            if p.balance > maxTokens:
                maxTokens = p.balance
                maxPlayers = [i]
            elif p.balance == maxTokens:
                maxPlayers = maxPlayers + [i]
        
        if(len(maxPlayers) > 1):
            self.allowedPlayers = maxPlayers
        
        return len(maxPlayers) > 1
    
    def answerQuestion(self, correct):
        if self.currentQuestion is None:
            raise ValueError("No question is being answered")
        elif self.currentPlayer is None:
            raise ValueError("No player chosen yet")
        
        self.currentQuestion.answered = True

        if correct:
            self.oneAnsweredCorrectly = True
            self.selectingPlayer = self.players.index(self.currentPlayer)
            self.currentPlayer.addPoints(self.currentQuestion.value)
        else:
            self.alreadyAnswered = self.alreadyAnswered + [self.players.index(self.currentPlayer)]
            if self.tiebreakIndex == -1:
                self.currentPlayer.addPoints(-1 * self.currentQuestion.value)
            if len(self.alreadyAnswered) == 4 and not self.oneAnsweredCorrectly:
                self.selectingPlayer = (self.selectingPlayer + 1) % 4
        
        self.currentPlayer = self.players[0]
        
        if self.is_over():
            if(self.is_tiebreak()):
                self.state = States.READING_QUESTION
                self.alreadyAnswered = []
                self.tiebreakIndex += 1
                self.currentQuestion = self.tiebreakQuestions[self.tiebreakIndex]
            else:
                self.state = States.OVER
        elif not correct and len(self.alreadyAnswered) != 4:
            self.state = States.READING_QUESTION
        else:
            self.alreadyAnswered = []
            self.state = States.SELECTING_QUESTION

    def toJSON(self):
        dict = {
            "players": [p.__dict__ for p in self.players],
            "questions": [q.__dict__ for q in self.questions],
            "state": self.state.value,
            "currentQuestion": None if self.currentQuestion is None else self.currentQuestion.__dict__,
            "currentPlayer": None if self.currentPlayer is None else self.currentPlayer.__dict__,
            "selectingPlayer": self.selectingPlayer,
            "alreadyAnswered": self.alreadyAnswered
        }
        return json.dumps(dict)

