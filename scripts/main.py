from player_stats import get_player_stats
from elo import get_player_elo, get_all_players_data
from fetch_data import load_data


def top_10_elo(player_data):
    sorted_players_hard = sorted(
        player_data['Hard'].items(),
        key=lambda x: x[1]['elo'],
        reverse=True
    )

    sorted_players_clay = sorted(
        player_data['Clay'].items(),
        key=lambda x: x[1]['elo'],
        reverse=True
    )

    sorted_players_grass = sorted(
        player_data['Grass'].items(),
        key=lambda x: x[1]['elo'],
        reverse=True
    )

    sorted_players_overall = sorted(
        player_data['Overall'].items(),
        key=lambda x: x[1]['elo'],
        reverse=True
    )

    sorted_players_overall_peak_elo = sorted(
        player_data['Overall'].items(),
        key=lambda x: x[1]['peak_elo'],
        reverse=True
    )

    print("Top 10 best hard court players of all time according to elo: ")
    for name, info in sorted_players_hard[:10]:
        print(f"{name}: {info['elo']:.1f} ({info['matches_played']} matches)")
    print()

    print("Top 10 best clay court players of all time according to elo: ")
    for name, info in sorted_players_clay[:10]:
        print(f"{name}: {info['elo']:.1f} ({info['matches_played']} matches)")
    print()

    print("Top 10 best grass court players of all time according to elo: ")
    for name, info in sorted_players_grass[:10]:
        print(f"{name}: {info['elo']:.1f} ({info['matches_played']} matches)")
    print()

    print("Top 10 best players of all time according to overall elo: ")
    for name, info in sorted_players_overall[:10]:
        print(f"{name}: {info['elo']:.1f} ({info['matches_played']} matches)")
    print()

    print("Top 10 best players of all time according to overall peak elo: ")
    for name, info in sorted_players_overall_peak_elo[:10]:
        print(f"{name}: {info['peak_elo']:.1f} ({info['matches_played']} matches)")
    print()

def main():
    data = load_data()

    # player_name = 'Novak Djokovic'
    # print(f'Elo on Hard: {get_player_elo(data, player_name, 'Hard'):.1f}')
    # print(f'Elo on Clay: {get_player_elo(data, player_name, 'Clay'):.1f}')
    # print(f'Elo on Grass: {get_player_elo(data, player_name, 'Grass'):.1f}')
    # print(f'Elo overall: {get_player_elo(data, player_name, 'Overall'):.1f}')

    players_data = get_all_players_data(data)
    top_10_elo(players_data)


if __name__ == '__main__':
    main()

