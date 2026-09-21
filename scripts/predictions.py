from player_stats import PlayerStats, get_head_to_head_stats
from elo import get_player_elo, get_all_players_data
from fetch_data import load_data, find_player_years
import numpy as np

def main():
    matches = load_data(years=2020, is_male = True)

    X_rows = []
    Y_rows = []

    for i in range(len(matches)):
        match = matches.iloc[i]
        p1, p2 = match['winner_name'], match['loser_name']
        surface = match['surface']

        past_data = matches.iloc[:i]

        try:
            p1_stats = PlayerStats(past_data, p1)
            p2_stats = PlayerStats(past_data, p2)

            p1_vect = p1_stats.get_player_features(surface)
            p2_vect = p2_stats.get_player_features(surface)

            X_rows.append((p1_vect - p2_vect))
            Y_rows.append(1)
            X_rows.append((p2_vect - p1_vect))
            Y_rows.append(0)

        except (KeyError, ValueError):
            continue

    X = np.array(X_rows)
    Y = np.array(Y_rows)

if __name__ == '__main__':
    main()



