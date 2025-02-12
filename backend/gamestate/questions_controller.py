""" Module for controlling questions in the game """

from typing import List, Tuple
import json
import os
from .models import Question, Team

MIN_TIME = int(os.getenv("TIME_TO_ANSWER_MIN_TIME", "10"))
MAX_TIME = int(os.getenv("TIME_TO_ANSWER_MAX_TIME", "30"))


class QuestionsController:
    """Class for controling questions atributes withtin the game"""

    def __get_min_max_values(self, questions: List[dict]) -> Tuple[int, int]:
        """Get the minimum and maximum value of the questions

        Args:
            questions (List[dict]): the questions in dict form to get the values from

        Returns:
            Tuple[int,int]: the minimum and maximum value
        """
        values = list(map(lambda x: x["value"], questions))
        return (min(values), max(values))

    def __get_time_to_answer(self, value: int, min_value: int, max_value: int) -> int:
        """Get the time to answer a question

        Args:
            value (int): the value of the question
            min_value (int): the minimum value of the questions
            max_value (int): the maximum value of the questions

        Returns:
            int: the time to answer the question
        """
        percentage = (value - min_value) / (max_value - min_value)
        return MIN_TIME + (MAX_TIME - MIN_TIME) * percentage

    def __init_questions(self):
        """Generate questions from questions.json

        Raises:
            ValueError: An even number of tiebreaker questions were given in the json
        """
        idx = 0
        with open("backend/questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)

            for category, questions in data["regular"].items():
                min_v, max_v = self.__get_min_max_values(questions)
                for question in questions:
                    self.questions.append(
                        Question(
                            idx,
                            question["question"],
                            question["answer"],
                            question["image"],
                            question["value"],
                            category,
                            self.__get_time_to_answer(question["value"], min_v, max_v),
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
                        120,
                        tie_breaker=True,
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
        self.get_current_question().skip()

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
        self.get_current_question().answer_correctly(team)

    def __answer_incorreclty(self, team: Team):
        """action for a team answering a question incorrectly

        Args:
            team (Team): team that answered the question
        """
        self.get_current_question().answer_incorreclty(team)

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
