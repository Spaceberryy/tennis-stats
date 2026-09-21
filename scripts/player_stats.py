import pandas as pd
import os
import glob
from dotenv import load_dotenv
import numpy as np

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


class PlayerStats:
    def __init__(self, data: pd.DataFrame, player_name):

        if player_name not in data['winner_name'].values and player_name not in data['loser_name'].values:
            logger.error(f"Player name '{player_name}' not found in data")
            raise KeyError(f"Player name '{player_name}' not found in data")

        data.dropna(subset='surface')
        data = data.drop(data[data['score'] == 'W/O'].index)
        self.data = data
        self.player_name = player_name

    def _get_data_column_helper(self, col_name, use_opponent = False):
        winner_col = 'w_' + col_name
        loser_col = 'l_' + col_name

        for col in (winner_col, loser_col):
            if col not in self.data.columns:
                logger.error(f"Column '{col}' not found in data")
                raise KeyError(f"Column '{col}' not found in data")

        if not use_opponent:
            data_in_match_won = self.data.loc[self.data['winner_name'] == self.player_name, winner_col].sum()
            data_in_match_lost = self.data.loc[self.data['loser_name'] == self.player_name, loser_col].sum()
        else:
            data_in_match_won = self.data.loc[self.data['winner_name'] == self.player_name, loser_col].sum()
            data_in_match_lost = self.data.loc[self.data['loser_name'] == self.player_name, winner_col].sum()

        return data_in_match_won, data_in_match_lost

    def _check_nonzero_denominator(self, denominator, context):
        if denominator == 0:
            logger.error(f"{context} for '{self.player_name}'")
            raise ValueError(f"{context} for '{self.player_name}'")

    def get_ace_rate(self):
        aces_in_match_won, aces_in_match_lost = self._get_data_column_helper('ace', False)
        svpt_in_match_won, svpt_in_match_lost = self._get_data_column_helper('svpt', False)
        total_aces = aces_in_match_won + aces_in_match_lost
        total_svpt = svpt_in_match_won + svpt_in_match_lost

        return (total_aces / total_svpt) * 100
    

    def get_first_serve_percentage(self):
        total_service_points_match_won, total_service_points_match_lost = self._get_data_column_helper('svpt', False)

        total_first_serves_in_match_won, total_first_serves_in_match_lost = self._get_data_column_helper('1stIn', False)

        denominator =  total_service_points_match_won + total_service_points_match_lost
        self._check_nonzero_denominator(denominator, f"No first serves data found for '{self.player_name}'")

        first_serve_percentage = ((total_first_serves_in_match_lost + total_first_serves_in_match_won) / (total_service_points_match_won + total_service_points_match_lost)) * 100

        return first_serve_percentage


    def get_break_points_saved_rate(self):
        total_break_points_faced_in_matches_won, total_break_points_faced_in_matches_lost = self._get_data_column_helper('bpFaced', False)

        total_break_points_saved_in_matches_won, total_break_points_saved_in_matches_lost  = self._get_data_column_helper('bpSaved', False)
        denominator = total_break_points_faced_in_matches_won + total_break_points_faced_in_matches_lost
        self._check_nonzero_denominator(denominator, f"No break points data found for '{self.player_name}'")
        break_points_saved = ((total_break_points_saved_in_matches_won + total_break_points_saved_in_matches_lost) / denominator) * 100

        return break_points_saved


    def get_surface_win_rate(self, surface):
        total_surface_matches_won = len(self.data[(self.data['winner_name'] == self.player_name) & (self.data['surface'] == surface)])
        total_surface_matches_lost = len(self.data[(self.data['loser_name'] == self.player_name) & (self.data['surface'] == surface)])

        total = total_surface_matches_lost + total_surface_matches_won
        self._check_nonzero_denominator(total, f"No matches found on surface '{surface}'")
        surface_win_rate = (total_surface_matches_won / (total_surface_matches_won + total_surface_matches_lost)) * 100

        return surface_win_rate


    def head_to_head_record(self, player_two):
        no_matches_won_by_player_one = len(self.data[(self.data['winner_name'] == self.player_name) & (self.data['loser_name'] == player_two)])
        no_matches_won_by_player_two = len(self.data[(self.data['winner_name'] == player_two) & (self.data['loser_name'] == self.player_name)])

        total = no_matches_won_by_player_one + no_matches_won_by_player_two
        if total == 0:
            return None
        return no_matches_won_by_player_one, no_matches_won_by_player_two


        return no_matches_won_by_player_one, no_matches_won_by_player_two
    def get_break_points_conversion_rate(self):
        # formula for calculating breaking points won :-
        #     if the player won the match: loser_break_points_faced - loser_break_points_saved
        #     if the player lost the match: winner_break_points_faced - winner_break_points_saved

        break_points_faced_by_opponent_when_winning, break_points_faced_by_opponent_when_losing = self._get_data_column_helper('bpFaced', True)
        break_points_saved_by_opponent_when_winning, break_points_saved_by_opponent_when_losing = self._get_data_column_helper('bpSaved', True)

        bp_won = (break_points_faced_by_opponent_when_losing + break_points_faced_by_opponent_when_winning) - (break_points_saved_by_opponent_when_losing + break_points_saved_by_opponent_when_winning)
        total_bp = break_points_faced_by_opponent_when_losing + break_points_faced_by_opponent_when_winning

        self._check_nonzero_denominator(total_bp, f"No break points data found for '{self.player_name}'")

        bp_conversion_rate = (bp_won / total_bp) * 100

        return bp_conversion_rate


    def get_first_serve_win_percentage(self):
        first_serve_points_match_won, first_serve_points_match_lost = self._get_data_column_helper('1stIn', False)
        first_serves_won_in_match_won, first_serves_won_in_match_lost = self._get_data_column_helper('1stWon', False)

        denominator = (first_serve_points_match_won + first_serve_points_match_lost)
        self._check_nonzero_denominator(denominator, f"No first serve data found for '{self.player_name}'")

        first_serve_win_percentage = ((first_serves_won_in_match_lost + first_serves_won_in_match_won) / denominator) * 100

        return first_serve_win_percentage


    def get_second_serve_win_percentage(self):
        first_serve_points_match_won, first_serve_points_match_lost = self._get_data_column_helper('1stIn', False)
        second_serves_won_in_match_won, second_serves_won_in_match_lost = self._get_data_column_helper('2ndWon', False)
        total_service_points_match_won, total_service_points_match_lost = self._get_data_column_helper('svpt', False)


        second_serves_won = second_serves_won_in_match_lost + second_serves_won_in_match_won

        total_second_serves = (total_service_points_match_lost + total_service_points_match_won) - (first_serve_points_match_lost + first_serve_points_match_won)

        self._check_nonzero_denominator(total_second_serves, f"No second serve data found for '{self.player_name}'")

        second_serves_win_percentage = (second_serves_won / total_second_serves) * 100

        return second_serves_win_percentage

    def get_win_percentage(self):
        '''
        returns the winning percentage of the player along with the number of matches won and matches lost
        '''
        total_matches_won = len(self.data[(self.data['winner_name'] == self.player_name)])
        total_matches_lost = len(self.data[(self.data['loser_name'] == self.player_name)])

        self._check_nonzero_denominator(total_matches_won + total_matches_lost, f"No match data found for '{self.player_name}'")

        return (total_matches_won / (total_matches_lost + total_matches_won)) * 100, total_matches_won, total_matches_lost

    def get_last_N_win_percentage(self, N):
        total_matches = self.data[(self.data['winner_name'] == self.player_name) | (self.data['loser_name'] == self.player_name)]
        last_N_matches = total_matches[-N:]

        wins_in_last_N_matches = len(last_N_matches[last_N_matches['winner_name'] == self.player_name])

        self._check_nonzero_denominator(len(last_N_matches), f"No match data found for '{self.player_name}' for last {N} matches")

        return (wins_in_last_N_matches / len(last_N_matches)) * 100

    def get_return_points_win_rate(self):
        opp_1st_won_in_match_won, opp_1st_won_in_match_lost = self._get_data_column_helper('1stWon', True)
        opp_2nd_won_in_match_won, opp_2nd_won_in_match_lost = self._get_data_column_helper('2ndWon', True)

        p_1st_won_in_match_won, p_1st_won_in_match_lost = self._get_data_column_helper('1stWon')
        p_2nd_won_in_match_won, p_2nd_won_in_match_lost = self._get_data_column_helper('2ndWon')

        opp_total_svpt_match_won, opp_total_svpt_match_lost = self._get_data_column_helper('svpt', True)

        total_ret_pnts = (opp_total_svpt_match_won + opp_total_svpt_match_lost)
        ret_pnts_won =  total_ret_pnts - (opp_1st_won_in_match_lost + opp_1st_won_in_match_won + opp_2nd_won_in_match_won + opp_2nd_won_in_match_lost)

        return (ret_pnts_won / total_ret_pnts) * 100

    def display_player_stats(self, opponent_name = None):
        print(f"Displaying stats for {self.player_name}:-")
        print(f'Ace rate: {self.get_ace_rate()}')

        print(f'First serve percentage: {self.get_first_serve_percentage():.2f}%')

        print(f'Break points saved percentage: {self.get_break_points_saved_rate():.2f}%')

        surfaces = ['Hard', 'Clay', 'Grass']
        for surface in surfaces:
            print(f'win rate on {surface}: {self.get_surface_win_rate(surface):.2f}%')

        if opponent_name is not None:
            record = self.head_to_head_record(opponent_name)
            if record is None:
                print(f"No Head to Head record found for {self.player_name} and {opponent_name}")
            else:
                player_one_wins, player_two_wins = record
                print(f'{player_one_wins} - {player_two_wins} against {opponent_name}')

        print(f'Break point conversion rate: {self.get_break_points_conversion_rate():.2f}%')

        print(f'First serve win rate: {self.get_first_serve_win_percentage():.2f}%')

        print(f'Second serve win rate: {self.get_second_serve_win_percentage():.2f}%')

        print(f'Return points win rate: {self.get_return_points_win_rate():.2f}%')

        win_percentage, wins, losses = self.get_win_percentage()
        print(f"{wins}-{losses} at {win_percentage:.2f}%")

        N = 10
        print(f'Last {N} matches won: {self.get_last_N_win_percentage(N):.2f}%')


    def get_player_features(self, surface):
        features = [
            self.get_ace_rate(),
            self.get_break_points_saved_rate(),
            self.get_break_points_conversion_rate(),
            self.get_surface_win_rate(surface),
            self.get_first_serve_percentage(),
            self.get_first_serve_win_percentage(),
            self.get_second_serve_win_percentage(),
            self.get_return_points_win_rate(),
            self.get_win_percentage()[0]
        ]
        return np.array((features))


def get_head_to_head_stats(data, p1, p2):
    player_one = PlayerStats(data, p1)
    player_two = PlayerStats(data, p2)

    print(f'{p1} - {p2}')

    print(f'Ace rate: {player_one.get_ace_rate():.2f}% - {player_two.get_ace_rate():.2f}%')

    print(f'First serve percentage: {player_one.get_first_serve_percentage():.2f}% - {player_two.get_first_serve_percentage():.2f}%')

    print(f'Break points saved percentage: {player_one.get_break_points_saved_rate():.2f}% - {player_two.get_break_points_saved_rate():.2f}%')

    print(f'Break point conversion rate: {player_one.get_break_points_conversion_rate():.2f}% - {player_two.get_break_points_conversion_rate():.2f}%')

    print(f'First serve win rate: {player_one.get_first_serve_win_percentage():.2f}% - {player_two.get_first_serve_win_percentage():.2f}%')

    print(f'Second serve win rate: {player_one.get_second_serve_win_percentage():.2f}% - {player_two.get_second_serve_win_percentage():.2f}%')

    print(f'Return points win rate: {player_one.get_return_points_win_rate():.2f}% - {player_two.get_return_points_win_rate():.2f}%')

    record = player_one.head_to_head_record(p2)
    if record is None:
        print(f"No Head to Head record found for {p1} and {p2}")
    else:
        player_one_wins, player_two_wins = record
        print(f'{player_one_wins} - {player_two_wins} against {p2}')



