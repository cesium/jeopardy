import os
from question import Question
from player import Player
from enum import Enum

class States(Enum):
    STARTING = 0
    SELECTING_QUESTION = 1
    ANSWERING_QUESTION = 2
    
class GameState:
    def setPlayers(players):
        self.players = [Player(player) for player in players]
        self.state = States.SELECTING_QUESTION
    def __init__(self):
        self.players = []
        self.questions = {} 
        self.initQuestions()
        self.state = States.STARTING
    def initQuestions(self):
        for file in os.listdir("backend/perguntas"):
            category = file[:-4]
            self.questions[category] = []
            value = 0
            f = open("backend/perguntas/"+file, "r", encoding="utf-8")
            while True:
                question = f.readline()
                answer = f.readline()
                value += 100
                if not question: #TODO: validar número de linhas par
                    break
                self.questions[category].append(Question(question.strip(), answer.strip(), value))
    def selectQuestion(self, category, value):
        self.currentQuestion = self.questions[category][value/100-1]
        self.state = States.ANSWERING_QUESTION
    
    def answerQuestion(self, correct):
        correct = False

        

if __name__ == "__main__":
    game = GameState()
