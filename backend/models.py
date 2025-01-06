class Player:
    def __init__(self,id: int, name : str):
        self.id : int = id
        self.name : str = name
        self.balance : int = 0

    def addPoints(self, points: int):
        """add points to the player

        Args:
            points (int): number of points to add
        """
        self.balance += points
    
    def toDict(self) -> dict:
        """represent the player as a dictionary

        Returns:
            dict: the representation of the player
        """
        return {
            "name": self.name,
            "balance": self.balance
        }


class Question:
    def __init__(self, id : int, statement : str, answer : str, image : str, value : int, category : str, tieBreaker : bool = False):
        self.id : int = id
        self.statement : str = statement
        self.answer : str = answer
        self.image : str = image
        self.value : int = value
        self.category : str = category
        self.answered : bool = False
        self.tieBreaker : bool = tieBreaker
        self.playersAnswered : list[Player] = []
    
    def answerIncorreclty(self, player : Player):
        """action for playing answering incorrectly

        Args:
            player (Player): the player that answered
        """
        self.playersAnswered.append(player)
        if not self.tieBreaker:
            player.addPoints(-self.value)
    
    def everyone_answered(self) -> bool:
        """check if all players answered the question

        Returns:
            bool: all players answered the question
        """
        return len(self.playersAnswered) == 4
    
    def answerCorrectly(self, player : Player):
        """action for playing answering correctly

        Args:
            player (Player): the player that answered
        """
        self.playersAnswered.append(player)
        player.addPoints(self.value)
        self.answered = True
    
    def skip(self):
        """action for skipping the question
        """
        self.answered = True
    
    def toDict(self) -> dict:
        """represent the question as a dictionary

        Returns:
            dict: the representation of the question
        """
        return {
            "id": self.id,
            "statement": self.statement,
            "answer": self.answer,
            "image": self.image,
            "value": self.value,
            "category": self.category,
            "answered": self.answered
        }

        
