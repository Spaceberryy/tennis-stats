from player_stats import PlayerStats, get_head_to_head_stats
from elo import get_player_elo, get_all_players_data
from fetch_data import load_data, find_player_years


def top_X_elo_rankings(player_data, X):
    categories = [
        ('Hard', 'elo', 'Top {} best hard court players according to elo:'),
        ('Clay', 'elo', 'Top {} best clay court players according to elo:'),
        ('Grass', 'elo', 'Top {} best grass court players according to elo:'),
        ('Carpet', 'elo', 'Top {} best carpet court players according to elo:'),
        ('Overall', 'elo', 'Top {} best players according to overall elo:'),
        ('Overall', 'peak_elo', 'Top {} best players according to overall peak elo:'),
    ]
    for surface, key, title in categories:
        print(title.format(X))
        ranked = sorted(player_data[surface].items(), key=lambda x: x[1][key], reverse=True)
        for name, info in ranked[:X]:
            print(f"{name}: {info[key]:.1f} ({info['matches_played']} matches)")
        print()

def single_player_elo(player_name):
    # Getting a single player's elo rating
    player_career_years = find_player_years(player_name)
    data = load_data(player_career_years)
    player_name = 'Novak Djokovic'
    print(f'Elo on Hard: {get_player_elo(data, player_name, 'Hard'):.1f}')
    print(f'Elo on Clay: {get_player_elo(data, player_name, 'Clay'):.1f}')
    print(f'Elo on Grass: {get_player_elo(data, player_name, 'Grass'):.1f}')
    print(f'Elo overall: {get_player_elo(data, player_name, 'Overall'):.1f}')

def top_X_elo(data):
    # Getting top X elo rankings
    players_data = get_all_players_data(data)
    top_X_elo_rankings(players_data, 10)

def single_player_stats(player_name, opponent_name = None):
    # Getting an individual player's stats
    player_career_years = find_player_years(player_name)

    data = load_data(player_career_years)

    player = PlayerStats(data, player_name)
    player.display_player_stats(opponent_name)
    npfeatures = player.get_player_features('Clay')
    print(npfeatures)

def head_to_head_stats(p1, p2, full_career = True):
    data = load_data()

    if not full_career:
        mask = ((data['winner_name'] == p1) & (data['loser_name'] == p2) | (data['winner_name'] == p2) & (data['loser_name'] == p1))
        data = data[mask]

    get_head_to_head_stats(data, p1, p2)


def main():
    data = load_data()

    # single_player_elo('Novak Djokovic')
    # top_X_elo(data)
    single_player_stats('Roger Federer', opponent_name = 'Novak Djokovic')
    # head_to_head_stats('Roger Federer', 'Novak Djokovic', full_career=True)



if __name__ == '__main__':
    main()

