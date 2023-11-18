import os

class GameState:
    def __init__(self):
        self.players = []
        self.questions = {} 
    def initQuestions(self):
        os.list