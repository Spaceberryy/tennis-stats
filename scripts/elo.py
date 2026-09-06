import numpy as np
import pandas as pd
import math


def get_expected_probability(R_A, R_B):
    return 1 / (1 + math.pow(10, (R_B - R_A) / 400))


def get_new_rating(S_A, E_A, R_A):
    K = 32
    return R_A + K * (S_A - E_A)


def get_new_ratings(R_A, R_B, S_A):
    E_A = get_expected_probability(R_A, R_B)
    E_B = 1 - E_A
    S_B = 1 - S_A
    R_A = get_new_rating(S_A, E_A, R_A)
    R_B = get_new_rating(S_B, E_B, R_B)
    return R_A, R_B


def process_match(player_elos, winner_name, loser_name):
    win = 1
    loss = 0

    R_winner = player_elos[winner_name]
    R_loser = player_elos[loser_name]
    new_R_winner, new_R_loser = get_new_ratings(R_winner, R_loser, win)
    player_elos[winner_name] = new_R_winner
    player_elos[loser_name] = new_R_loser


def main():
    data = pd.read_csv('../data/TML-Database/2025.csv')

    player_names = pd.concat([data['winner_name'], data['loser_name']]).unique()

    default_elo = 1500

    all_surface_elos = {
        'Hard': dict.fromkeys(player_names, default_elo),
        'Clay': dict.fromkeys(player_names, default_elo),
        'Grass': dict.fromkeys(player_names, default_elo),
    }

    for row in data.sort_values('tourney_date').itertuples():
        process_match(all_surface_elos[row.surface], row.winner_name, row.loser_name)

    print(all_surface_elos['Hard']['Carlos Alcaraz'])
    print(all_surface_elos['Clay']['Carlos Alcaraz'])
    print(all_surface_elos['Grass']['Carlos Alcaraz'])


if __name__ == '__main__':
    main()



