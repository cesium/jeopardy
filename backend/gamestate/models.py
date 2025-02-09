# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-positional-arguments
"""Module of classes used in gamestate"""
from typing import List


class Team:
    """
    Team class
    """

    def __init__(self, idx: int, names: List[str], controller: int = None):
        self.id: int = idx
        self.names: List[str] = names
        self.balance: int = 0
        self.controller: int = idx if controller is None else controller

    def add_points(self, points: int):
        """add points to the team

        Args:
            points (int): number of points to add
        """
        self.balance += points

    def to_dict(self) -> dict:
        """represent the team as a dictionary

        Returns:
            dict: the representation of the team
        """
        return {"names": self.names, "balance": self.balance}

    def __repr__(self) -> str:
        """
            represent a team
        Returns:
            str: the team
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
        time_to_answer: int,
        tie_breaker: bool = False,
    ):
        self.id: int = idx
        self.statement: str = statement
        self.answer: str = answer
        self.image: str = image
        self.value: int = value
        self.category: str = category
        self.answered: bool = False
        self.time_to_answer: int = time_to_answer
        self.tie_breaker: bool = tie_breaker

    def answer_incorreclty(self, team: Team):
        """action for playing answering incorrectly

        Args:
            team (Team): the team that answered
        """
        if not self.tie_breaker:
            team.add_points(-self.value)

    def answer_correctly(self, team: Team):
        """action for playing answering correctly

        Args:
            team (Team): the team that answered
        """
        team.add_points(self.value)
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
            "tta": self.time_to_answer,
        }
