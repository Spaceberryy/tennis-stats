import pandas as pd
import os
import glob
from dotenv import load_dotenv

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
DATA_DIR = os.getenv('DATA_DIR')

if DATA_DIR is None:
    raise ValueError("Environment variable DATA_DIR not set")

def load_data(years = None):
    # years = int, list of ints, or None
    if years is None:
        year_files = glob.glob(os.path.join(DATA_DIR, '[0-9][0-9][0-9][0-9].csv'))
        if not year_files:
            raise FileNotFoundError(f"No year CSV files found in {DATA_DIR}")
        latest_file = max(year_files, key=lambda f: int(os.path.splitext(os.path.basename(f))[0]))
        files = [latest_file]
    elif isinstance(years, int):
        files = [os.path.join(DATA_DIR, f'{years}.csv')]
    else:
        files = [os.path.join(DATA_DIR, f'{year}.csv') for year in years]

    missing = [f for f in files if not os.path.exists(f)]
    if missing:
        raise FileNotFoundError(f"Mising data files: {missing}")

    return pd.concat((pd.read_csv(f) for f in files), ignore_index = True)

def find_player_years(player_name):
    matching_years = []
    for f in sorted(glob.glob(os.path.join(DATA_DIR, '[0-9][0-9][0-9][0-9].csv'))):
        year = int(os.path.splitext(os.path.basename(f))[0])
        names = pd.read_csv(f, usecols=['winner_name', 'loser_name'])
        if player_name in names['winner_name'].values or player_name in names['loser_name'].values:
            matching_years.append(year)

    if not matching_years:
        logger.error(f"Player '{player_name}' not found in any year's data")
        raise ValueError(f"player '{player_name}' not found in any year's data")

    return matching_years



class PlayerStats:
    def __init__(self, data: pd.DataFrame, player_name):

        if player_name not in data['winner_name'].values and player_name not in data['loser_name'].values:
            logger.error(f"Player name '{player_name}' not found in data")
            raise KeyError(f"Player name '{player_name}' not found in data")

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

    def get_ace_count(self):
        aces_in_match_won, aces_in_match_lost = self._get_data_column_helper('ace', False)
        total_aces = aces_in_match_won + aces_in_match_lost

        return total_aces
    

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


def main():
    player_name = 'Pete Sampras'

    player_career_years = find_player_years(player_name)

    data = load_data(player_career_years)

    player = PlayerStats(data, player_name)

    print(f"Displaying stats for {player_name}:-")
    print(f'Ace count: {player.get_ace_count()}')

    print(f'First serve percentage: {player.get_first_serve_percentage():.2f}%')

    print(f'Break points saved percentage: {player.get_break_points_saved_rate():.2f}%')

    surface = 'Clay' # please make sure that the first letter of the surface name is capital
    print(f'win rate: {player.get_surface_win_rate(surface):.2f}%')

    opponent_name = 'Bjorn Borg'
    record = player.head_to_head_record(opponent_name)
    if record is None:
        print(f"No Head to Head record found for {player_name} and {opponent_name}")
    else:
        player_one_wins, player_two_wins = record
        print(f'{player_one_wins} - {player_two_wins} against {opponent_name}')

    print(f'Break point conversion rate: {player.get_break_points_conversion_rate():.2f}%')

    print(f'First serve win rate: {player.get_first_serve_win_percentage():.2f}%')

    print(f'Second serve win rate: {player.get_second_serve_win_percentage():.2f}%')

    win_percentage, wins, losses = player.get_win_percentage()
    print(f"{wins}-{losses} at {win_percentage:.2f}%")

    N = 10
    print(f'Last {N} matches won: {player.get_last_N_win_percentage(N):.2f}%')


if __name__ == '__main__':
    main()




