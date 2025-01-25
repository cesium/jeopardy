""" Module for controlling the teams in the game """

from typing import List
import logging
from .models import Team


class TeamsController:
    """Class for controling teams atributes withtin the game"""

    def __init__(self):
        self.teams: List[Team] = []
        self.current_playing_id: int = 0
        self.selecting_id: int = 0
        self.playing: List[int] = []

    def get_current_team(self) -> Team:
        """get the team playing

        Returns:
            Team: the team playing
        """
        if self.teams == []:
            return None
        return self.teams[self.current_playing_id]

    def get_team(self, idx: int) -> Team:
        """get team with given id

        Args:
            idx (int): id of team

        Returns:
            Team: team with given id
        """
        if self.teams == []:
            return None
        return self.teams[idx]

    def get_selecting_team(self) -> Team:
        """get the team selecting

        Returns:
            Team: the team selecting
        """
        if self.teams == []:
            return None
        return self.teams[self.selecting_id]

    def set_teams(self, player_teams_names: List[List[str]]):
        """creates the teams with the given names

        Args:
            teams_names (List[str]): list of names
        Raises:
            ValueError: Too many teams (max 4)
            ValueError: Too many players in a team (max 4)
        """
        if len(player_teams_names) > 4:
            raise ValueError("Too many teams (max 4)")
        for t in player_teams_names:
            if len(t) > 4:
                raise ValueError("Too many players in a team (max 4)")
        self.teams = [Team(idx, names) for idx, names in enumerate(player_teams_names)]
        self.current_playing_id = 0
        self.selecting_id = 0
        self.playing = list(range(len(player_teams_names)))

    def split_or_steal(self, votes: List[int]):
        """split or steal the balance of the team

        Args:
            members (List[int]): list of members that stole.
        """
        logging.debug("Split or Steal: [%s]", ",".join(str(v) for v in votes))
        team = self.get_winning_team()
        if len(votes) > 1:
            team.balance = 0
        elif len(votes) == 1:
            stealer = votes[0]
            new_id = len(self.teams)
            self.teams.append(Team(new_id, [team.names[stealer]]))
            self.teams[new_id].balance = team.balance
            team.balance = 0
            del team.names[stealer]

    def set_selecting(self, idx: int):
        """set team with given id as selecting

        Args:
            idx (int): id of team to set as selecting
        """
        self.selecting_id = idx

    def set_current_playing(self, idx: int):
        """set team with given id as playing

        Args:
            idx (int): id of team to set as playing
        """
        self.current_playing_id = idx

    def is_tie(self) -> bool:
        """check if the teams are in a tie

        Returns:
            bool: the teams are in a tie
        """
        max_tokens = max(p.balance for p in self.teams)
        teams_with_max_tokens = [p.id for p in self.teams if p.balance == max_tokens]
        if len(teams_with_max_tokens) > 1:
            self.playing = teams_with_max_tokens
            return True
        return False

    def get_winning_team(self) -> Team:
        """get the winning team

        Returns:
            Team: the winning team
        """
        if self.teams == []:
            return None
        c = self.teams[0]
        for t in self.teams[1:]:
            if t.balance > c.balance:
                c = t
        return c

    def next_selecting(self):
        """make the next team in line be the selecting one"""
        self.selecting_id = (self.selecting_id + 1) % 4

    def set_selecting_as_current(self):
        """make the team playing as the selecting"""
        self.selecting_id = self.current_playing_id

    def list_teams(self) -> List[Team]:
        """return the list of the teams in the game

        Returns:
            List[Team]: list of teams in the game
        """
        return self.teams.copy()
