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


def load_data(years = None, from_year = None):
    # years = int, list of ints, or None
    if from_year is not None:
        year_files = glob.glob(os.path.join(DATA_DIR, '[0-9][0-9][0-9][0-9].csv'))
        available_years = sorted(int(os.path.splitext(os.path.basename(f))[0]) for f in year_files)
        files = sorted(
            os.path.join(DATA_DIR, f'{year}.csv')
            for year in available_years
            if year >= from_year
        )
        if not files:
            raise FileNotFoundError(f"No data files found from {from_year} onward")
    elif years is None:
        year_files = glob.glob(os.path.join(DATA_DIR, '[0-9][0-9][0-9][0-9].csv'))
        if not year_files:
            raise FileNotFoundError(f"No year CSV files found in {DATA_DIR}")
        files = year_files
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


