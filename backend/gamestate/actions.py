# pylint: disable=too-many-instance-attributes
"""
    This module contains the Actions class which is used to control the actions of the game
"""


class Actions:
    """Class for controling actions atributes withtin the game"""

    def __init__(self):
        self.play_correct_sound: bool = False
        self.play_wrong_sound: bool = False
        self.play_start_accepting: bool = False
        self.play_buzzer_sound: bool = False
        self.stop_countdown: bool = False
        self.play_end_sound: bool = False
        self.show_sos: bool = False
        self.show_tiebreaker: bool = False
        self.play_theme_song: bool = True
        self.play_question_selection_sound: bool = False

    def reset_sound(self):
        """
        Set both sound playing to false
        """
        self.play_correct_sound = False
        self.play_wrong_sound = False
        self.play_start_accepting = False
        self.play_buzzer_sound = False
        self.play_end_sound = False
        self.play_theme_song = False
        self.play_question_selection_sound = False

    def reset_countdown_timer(self):
        """reset the countdown timer"""
        self.stop_countdown = False

    def to_dict(self) -> dict:
        """
            cast the state as a dictionary to represent as json object
        Returns:
            dict: the gamestate data
        """
        return {
            "playCorrectSound": self.play_correct_sound,
            "playWrongSound": self.play_wrong_sound,
            "playStartAccepting": self.play_start_accepting,
            "playBuzzerSound": self.play_buzzer_sound,
            "playEndSound": self.play_end_sound,
            "playThemeSong": self.play_theme_song,
            "playQuestionSelectionSound": self.play_question_selection_sound,
            "stopTimer": self.stop_countdown,
            "showSOS": self.show_sos,
            "showTiebreaker": self.show_tiebreaker,
        }
