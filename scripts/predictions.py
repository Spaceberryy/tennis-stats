from collections import defaultdict
import numpy as np
from fetch_data import load_data, clean_data

STAT_COLS = [
    'ace',
    'svpt',
    '1stIn',
    '1stWon',
    '2ndWon',
    'bpFaced',
    'bpSaved'
]


def get_features(player_stats, surface_wins, surface_losses):
    """Calculate features from one player's running statistics."""

    second_serve_points = player_stats['svpt'] - player_stats['1stIn']

    return np.array([
        player_stats['ace'] / player_stats['svpt'] * 100,  # Ace rate

        player_stats['bpSaved'] / player_stats['bpFaced'] * 100,  # BP saved %

        # Break points converted on return
        (player_stats['opp_bpFaced'] - player_stats['opp_bpSaved']) / player_stats['opp_bpFaced'] * 100,

        # Win rate on the current surface
        surface_wins / (surface_wins + surface_losses) * 100,

        player_stats['1stIn'] / player_stats['svpt'] * 100,  # 1st serve %

        player_stats['1stWon'] / player_stats['1stIn'] * 100,  # 1st serve win %

        player_stats['2ndWon'] / second_serve_points * 100,  # 2nd serve win %

        # Return points won
        (player_stats['opp_svpt'] - player_stats['opp_1stWon'] - player_stats['opp_2ndWon']) / player_stats['opp_svpt'] * 100,
        # Overall win rate
        player_stats['wins'] / (player_stats['wins'] + player_stats['losses']) * 100,
    ])


def add_match_stats(player_stats, own_stats, opponent_stats):
    """Add a match's statistics to a player's running totals."""

    for stat in STAT_COLS:
        player_stats[stat] += own_stats[stat]
        player_stats['opp_' + stat] += opponent_stats[stat]


def get_X_Y_rows():
    matches = clean_data(load_data(years=2023)).reset_index(drop=True)

    stat_columns = [
        player_prefix + stat
        for player_prefix in ('w_', 'l_')
        for stat in STAT_COLS
    ]

    # Missing match statistics are treated as zero.
    matches[stat_columns] = matches[stat_columns].fillna(0)

    match_rows = matches.to_dict('records')

    # Running career/match totals for each player.
    player_stats = defaultdict(lambda: defaultdict(float))

    # (player, surface) -> [wins, losses]
    surface_records = defaultdict(lambda: [0, 0])

    X_rows = []
    Y_rows = []
    skipped_matches = 0

    for match in match_rows:
        winner = match['winner_name']
        loser = match['loser_name']
        surface = match['surface']

        try:
            winner_surface_wins, winner_surface_losses = (
                surface_records[(winner, surface)]
            )
            loser_surface_wins, loser_surface_losses = (
                surface_records[(loser, surface)]
            )

            winner_features = get_features(
                player_stats[winner],
                winner_surface_wins,
                winner_surface_losses
            )

            loser_features = get_features(
                player_stats[loser],
                loser_surface_wins,
                loser_surface_losses
            )

            # Add both perspectives so the model sees winner and loser examples.
            X_rows.append(winner_features - loser_features)
            Y_rows.append(1)

            X_rows.append(loser_features - winner_features)
            Y_rows.append(0)

        except ZeroDivisionError:
            skipped_matches += 1

        winner_match_stats = {
            stat: match['w_' + stat]
            for stat in STAT_COLS
        }

        loser_match_stats = {
            stat: match['l_' + stat]
            for stat in STAT_COLS
        }

        # Update running statistics only AFTER generating this match's features.
        add_match_stats(
            player_stats[winner],
            winner_match_stats,
            loser_match_stats
        )

        add_match_stats(
            player_stats[loser],
            loser_match_stats,
            winner_match_stats
        )

        player_stats[winner]['wins'] += 1
        player_stats[loser]['losses'] += 1

        surface_records[(winner, surface)][0] += 1
        surface_records[(loser, surface)][1] += 1

    X = np.array(X_rows)
    Y = np.array(Y_rows)

    return X, Y


if __name__ == '__main__':
    main()