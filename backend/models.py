# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-positional-arguments
"""Module of classes used in gamestate"""


class Player:
    """
    Player class
    """

    def __init__(self, idx: int, name: str):
        self.id: int = idx
        self.name: str = name
        self.balance: int = 0

    def add_points(self, points: int):
        """add points to the player

        Args:
            points (int): number of points to add
        """
        self.balance += points

    def to_dict(self) -> dict:
        """represent the player as a dictionary

        Returns:
            dict: the representation of the player
        """
        return {"name": self.name, "balance": self.balance}

    def __repr__(self) -> str:
        """
            represent a player
        Returns:
            str: the player
        """
        return f"{self.id}"


class Question:
    """
    Question class
    """

    def __init__(
        self,
        idx: int,
        statement: str,
        answer: str,
        image: str,
        value: int,
        category: str,
        tie_breaker: bool = False,
    ):
        self.id: int = idx
        self.statement: str = statement
        self.answer: str = answer
        self.image: str = image
        self.value: int = value
        self.category: str = category
        self.answered: bool = False
        self.tie_breaker: bool = tie_breaker
        self.players_answered: list[Player] = []

    def answer_incorreclty(self, player: Player):
        """action for playing answering incorrectly

        Args:
            player (Player): the player that answered
        """
        self.players_answered.append(player)
        if not self.tie_breaker:
            player.add_points(-self.value)

    def everyone_answered(self) -> bool:
        """check if all players answered the question

        Returns:
            bool: all players answered the question
        """
        return len(self.players_answered) == 4

    def answer_correctly(self, player: Player):
        """action for playing answering correctly

        Args:
            player (Player): the player that answered
        """
        self.players_answered.append(player)
        player.add_points(self.value)
        self.answered = True

    def skip(self):
        """action for skipping the question"""
        self.answered = True

    def to_dict(self) -> dict:
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
            "answered": self.answered,
        }
