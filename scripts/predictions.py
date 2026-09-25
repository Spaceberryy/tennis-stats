from collections import defaultdict
import numpy as np
from fetch_data import load_data, clean_data, get_player_rows
from collections import deque
from elo import process_match, get_k_factor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

STAT_COLS = [
    'ace',
    'svpt',
    '1stIn',
    '1stWon',
    '2ndWon',
    'bpFaced',
    'bpSaved'
]


def get_features(player_stats, surface_wins, surface_losses, h2h_win_pct, recent_form_pct, elo, opp_elo):
    """Calculate features from one player's running statistics."""

    second_serve_points = player_stats['svpt'] - player_stats['1stIn']
    first_serve_win_pct = player_stats['1stWon'] / player_stats['1stIn'] * 100  # 1st serve win %
    return_pts_won_pct = (player_stats['opp_svpt'] - player_stats['opp_1stWon'] - player_stats['opp_2ndWon']) / player_stats['opp_svpt'] * 100
    second_service_win_pct = player_stats['2ndWon'] / second_serve_points * 100  # 2nd serve win %
    total_service_pts_won_pct = ((player_stats['1stWon'] + player_stats['2ndWon']) / player_stats['svpt']) * 100

    return np.array([
        player_stats['ace'] / player_stats['svpt'] * 100,  # Ace rate
        player_stats['bpSaved'] / player_stats['bpFaced'] * 100,  # BP saved %
        (player_stats['opp_bpFaced'] - player_stats['opp_bpSaved']) / player_stats['opp_bpFaced'] * 100, # Break points converted on return
        (surface_wins / (surface_wins + surface_losses)) * 100, # Win rate on the current surface
        (player_stats['1stIn'] / player_stats['svpt']) * 100,  # 1st serve %
        first_serve_win_pct,
        return_pts_won_pct,
        second_service_win_pct,
        player_stats['wins'] / (player_stats['wins'] + player_stats['losses']) * 100, # Overall win rate
        h2h_win_pct,
        return_pts_won_pct / (100 - total_service_pts_won_pct) if total_service_pts_won_pct < 100 else 0, # dominance ratio
        recent_form_pct,
        elo - opp_elo,
    ])

def add_match_stats(player_stats, own_stats, opponent_stats):
    """Add a match's statistics to a player's running totals."""

    for stat in STAT_COLS:
        player_stats[stat] += own_stats[stat]
        player_stats['opp_' + stat] += opponent_stats[stat]


def get_h2d_win_pct(player, opponent, h2h_record):
    wins_for = h2h_record[player][opponent]
    wins_against = h2h_record[opponent][player]
    total = wins_for + wins_against
    return wins_for / total * 100 if total > 0 else 50.0

def get_recent_form_pct(player, recent_form):
    history = recent_form[player]
    return sum(history) / len(history) * 100 if history else 50.0


def get_X_Y_rows(matches):
    stat_columns = [
        player_prefix + stat
        for player_prefix in ('w_', 'l_')
        for stat in STAT_COLS
    ]

    # Missing match statistics are treated as zero.
    matches = matches.dropna(subset = stat_columns)

    match_rows = matches.to_dict('records')

    # Running career/match totals for each player.
    player_stats = defaultdict(lambda: defaultdict(float))

    # (player, surface) -> [wins, losses]
    surface_records = defaultdict(lambda: [0, 0])

    X_rows = []
    Y_rows = []

    surfaces = ['Hard', 'Clay', 'Grass', 'Carpet', 'Overall']
    default_elo = 1500

    h2h_record = defaultdict(lambda: defaultdict(int))
    recent_form = defaultdict(lambda: deque(maxlen=10))
    elo_data = {
        surface: defaultdict(lambda: {'elo': default_elo, 'matches_played': 0, 'peak_elo': 0})
        for surface in surfaces
    }

    skipped_matches = 0


    for match in match_rows:
        winner = match['winner_name']
        loser = match['loser_name']
        surface = match['surface']

        winner_h2h = get_h2d_win_pct(winner, loser, h2h_record)
        loser_h2h = get_h2d_win_pct(loser, winner, h2h_record)

        winner_form = get_recent_form_pct(winner, recent_form)
        loser_form = get_recent_form_pct(loser, recent_form)

        winner_elo = elo_data[surface][winner]['elo']
        loser_elo = elo_data[surface][loser]['elo']

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
                winner_surface_losses,
                winner_h2h,
                winner_form,
                winner_elo,
                loser_elo
            )

            loser_features = get_features(
                player_stats[loser],
                loser_surface_wins,
                loser_surface_losses,
                loser_h2h,
                loser_form,
                loser_elo,
                winner_elo
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

        h2h_record[winner][loser] += 1

        recent_form[winner].append(1)
        recent_form[loser].append(0)

        process_match(elo_data[surface], winner, loser, match['tourney_level'])
        process_match(elo_data['Overall'], winner, loser, match['tourney_level'])


    X = np.array(X_rows)
    Y = np.array(Y_rows)

    return X, Y

def main():
    matches = clean_data(load_data(from_year=2010)).reset_index(drop=True)
    X, Y = get_X_Y_rows(matches)

    split = int(len(X) * 0.8) // 2 * 2
    X_train, X_test = X[:split], X[split:]
    Y_train, Y_test = Y[:split], Y[split:]


    model = make_pipeline(StandardScaler(), LogisticRegression())
    model.fit(X_train, Y_train)
    print(f"accuracy: {model.score(X_test, Y_test)}")
    print(model[-1].coef_)

if __name__ == '__main__':
    main()