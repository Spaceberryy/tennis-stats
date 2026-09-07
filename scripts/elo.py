import numpy as np
import pandas as pd
import math


def get_expected_probability(R_A, R_B):
    return 1 / (1 + math.pow(10, (R_B - R_A) / 400))


def get_new_rating(S_A, E_A, R_A, K_factor):
    K = K_factor
    return R_A + K * (S_A - E_A)


def get_new_ratings(R_A, R_B, S_A, K_winner, K_loser):
    E_A = get_expected_probability(R_A, R_B)
    E_B = 1 - E_A
    S_B = 1 - S_A
    R_A = get_new_rating(S_A, E_A, R_A, K_winner)
    R_B = get_new_rating(S_B, E_B, R_B, K_loser)
    return R_A, R_B


def get_k_factor(rating, matches_played):
    if matches_played < 30:
        return 40  # provisional / new player, rating not yet reliable
    elif rating < 2100:
        return 20  # most players
    else:
        return 10  # elite tier, rating should be sticky


def process_match(player_data, winner_name, loser_name):
    win = 1
    loss = 0

    R_winner = player_data[winner_name]['elo']
    R_loser = player_data[loser_name]['elo']

    K_winner = get_k_factor(R_winner, player_data[winner_name]['matches_played'])
    K_loser = get_k_factor(R_loser, player_data[loser_name]['matches_played'])

    new_R_winner, new_R_loser = get_new_ratings(R_winner, R_loser, win, K_winner, K_loser)

    if player_data[winner_name]['peak_elo'] < new_R_winner:
        player_data[winner_name]['peak_elo'] = new_R_winner

    if player_data[loser_name]['peak_elo'] < new_R_loser:
        player_data[loser_name]['peak_elo'] = new_R_loser

    player_data[winner_name]['elo'] = new_R_winner
    player_data[loser_name]['elo'] = new_R_loser

    player_data[winner_name]['matches_played'] += 1
    player_data[loser_name]['matches_played'] += 1


def calculate_elo(data):

    player_names = pd.concat([data['winner_name'], data['loser_name']]).unique()

    default_elo = 1500
    surfaces = ['Hard', 'Clay', 'Grass', 'Carpet', 'Overall']

    player_data = {
        surface: {name: {'elo': default_elo, 'matches_played': 0, 'peak_elo': 0} for name in player_names}
        for surface in surfaces
    }

    # dropping the rows which have nan for surface
    data = data.dropna(subset='surface')

    for row in data.sort_values('tourney_date').itertuples():
        process_match(player_data[row.surface], row.winner_name, row.loser_name)
        process_match(player_data['Overall'], row.winner_name, row.loser_name)

    return player_data

def get_player_elo(data, player_name, surface):
    player_data = calculate_elo(data)
    return player_data[surface][player_name]['elo']

def get_all_players_data(data):
    return calculate_elo(data)



