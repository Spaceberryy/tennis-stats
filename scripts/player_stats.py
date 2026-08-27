import pandas as pd

class PlayerStats:
    def __init__(self, data: pd.DataFrame, player_name):

        if player_name not in data['winner_name'] and player_name not in data['loser_name']:
            raise KeyError(f"Player name '{player_name}' not found in data")

        self.data = data
        self.player_name = player_name

    def _get_data_column_helper(self, col_name, use_opponent = False):
        winner_col = 'w_' + col_name
        loser_col = 'l_' + col_name

        for col in (winner_col, loser_col):
            if col not in self.data.columns:
                raise KeyError(f"Column '{col}' not found in data")

        if not use_opponent:
            data_in_match_won = self.data.loc[self.data['winner_name'] == self.player_name, winner_col].sum()
            data_in_match_lost = self.data.loc[self.data['loser_name'] == self.player_name, loser_col].sum()
        else:
            data_in_match_won = self.data.loc[self.data['winner_name'] == self.player_name, loser_col].sum()
            data_in_match_lost = self.data.loc[self.data['loser_name'] == self.player_name, winner_col].sum()

        return data_in_match_won, data_in_match_lost


    def get_ace_count(self):
        aces_in_match_won, aces_in_match_lost = self._get_data_column_helper('ace', False)
        total_aces = aces_in_match_won + aces_in_match_lost

        return total_aces
    

    def get_first_serve_percentage(self):
        total_service_points_match_won, total_service_points_match_lost = self._get_data_column_helper('svpt', False)

        total_first_serves_in_match_won, total_first_serves_in_match_lost = self._get_data_column_helper('1stIn', False)

        first_serve_percentage = ((total_first_serves_in_match_lost + total_first_serves_in_match_won) / (total_service_points_match_won + total_service_points_match_lost)) * 100

        return first_serve_percentage


    def get_break_points_saved_rate(self):
        total_break_points_faced_in_matches_won, total_break_points_faced_in_matches_lost = self._get_data_column_helper('bpFaced', False)

        total_break_points_saved_in_matches_won, total_break_points_saved_in_matches_lost  = self._get_data_column_helper('bpSaved', False)

        break_points_saved = ((total_break_points_saved_in_matches_won + total_break_points_saved_in_matches_lost) / (total_break_points_faced_in_matches_won + total_break_points_faced_in_matches_lost)) * 100

        return break_points_saved


    def get_surface_win_rate(self, surface):
        total_surface_matches_won = len(self.data[(self.data['winner_name'] == self.player_name) & (self.data['surface'] == surface)])
        total_surface_matches_lost = len(self.data[(self.data['loser_name'] == self.player_name) & (self.data['surface'] == surface)])

        # TODO: Will need to consider division by zero error here. Will Fix later if need be.
        surface_win_rate = (total_surface_matches_won / (total_surface_matches_won + total_surface_matches_lost)) * 100

        return surface_win_rate


    def head_to_head_record(self, player_two):
        no_matches_won_by_player_one = len(self.data[(self.data['winner_name'] == self.player_name) & (self.data['loser_name'] == player_two)])
        no_matches_won_by_player_two = len(self.data[(self.data['winner_name'] == player_two) & (self.data['loser_name'] == self.player_name)])

        total = no_matches_won_by_player_one + no_matches_won_by_player_two
        if total == 0:
            raise ValueError(f"No matches found for '{self.player_name}' and '{player_two}'")


        return no_matches_won_by_player_one, no_matches_won_by_player_two
    def get_break_points_conversion_rate(self):
        # formula for calculating breaking points won :-
        #     if the player won the match: loser_break_points_faced - loser_break_points_saved
        #     if the player lost the match: winner_break_points_faced - winner_break_points_saved

        break_points_faced_by_opponent_when_winning, break_points_faced_by_opponent_when_losing = self._get_data_column_helper('bpFaced', True)
        break_points_saved_by_opponent_when_winning, break_points_saved_by_opponent_when_losing = self._get_data_column_helper('bpSaved', True)

        bp_won = (break_points_faced_by_opponent_when_losing + break_points_faced_by_opponent_when_winning) - (break_points_saved_by_opponent_when_losing + break_points_saved_by_opponent_when_winning)
        total_bp = break_points_faced_by_opponent_when_losing + break_points_faced_by_opponent_when_winning

        bp_conversion_rate = (bp_won / total_bp) * 100

        return bp_conversion_rate


    def get_first_serve_win_percentage(self):
        first_serve_points_match_won, first_serve_points_match_lost = self._get_data_column_helper('1stIn', False)
        first_serves_won_in_match_won, first_serves_won_in_match_lost = self._get_data_column_helper('1stWon', False)

        first_serve_win_percentage = ((first_serves_won_in_match_lost + first_serves_won_in_match_won) / (first_serve_points_match_won + first_serve_points_match_lost)) * 100

        return first_serve_win_percentage


    def get_second_serve_win_percentage(self):
        first_serve_points_match_won, first_serve_points_match_lost = self._get_data_column_helper('1stIn', False)
        second_serves_won_in_match_won, second_serves_won_in_match_lost = self._get_data_column_helper('2ndWon', False)
        total_service_points_match_won, total_service_points_match_lost = self._get_data_column_helper('svpt', False)


        second_serves_won = second_serves_won_in_match_lost + second_serves_won_in_match_won

        total_second_serves = (total_service_points_match_lost + total_service_points_match_won) - (first_serve_points_match_lost + first_serve_points_match_won)

        second_serves_win_percentage = (second_serves_won / total_second_serves) * 100

        return second_serves_win_percentage

    def get_win_percentage(self):
        total_matches_won = len(self.data[(self.data['winner_name'] == self.player_name)])
        total_matches_lost = len(self.data[(self.data['loser_name'] == self.player_name)])

        return (total_matches_won / (total_matches_lost + total_matches_won)) * 100

    def get_last_N_win_percentage(self, N):
        total_matches = self.data[(self.data['winner_name'] == self.player_name) | (self.data['loser_name'] == self.player_name)]
        last_N_matches = total_matches[-N:]

        wins_in_last_N_matches = len(last_N_matches[last_N_matches['winner_name'] == self.player_name])

        return (wins_in_last_N_matches / len(last_N_matches)) * 100


data = pd.read_csv('../data/TML-Database/2006.csv')

def main():
    player = PlayerStats(data, 'Roger Federer')

    print("Displaying stats for Jannik Sinner:-")
    print(f'Ace count: {player.get_ace_count()}')

    print(f'First serve percentage: {player.get_first_serve_percentage()}')

    print(f'Break points saved percentage: {player.get_break_points_saved_rate()}')

    print(f'Surface win rate: {player.get_surface_win_rate('Hard')}')

    player_one_wins, player_two_wins = player.head_to_head_record('Carlos Alcaraz')
    print(f'{player_one_wins} - {player_two_wins}')

    print(f'Break point conversion rate: {player.get_break_points_conversion_rate()}')

    print(f'First serve win rate: {player.get_first_serve_win_percentage()}')

    print(f'Second serve in rate: {player.get_second_serve_win_percentage()}')

    print(f'Win percentage: {player.get_win_percentage()}')

    N = 10
    print(f'Last {N} matches won: {player.get_last_N_win_percentage(N)}')


if __name__ == '__main__':
    main()




