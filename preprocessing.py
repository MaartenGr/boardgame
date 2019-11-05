import re
import numpy as np
import pandas as pd
from typing import List, Tuple


def prepare_data(link: str) -> Tuple[pd.DataFrame, List[str]]:
    """ Load and prepare/preprocess the data

    Parameters:
    -----------

    link : str
        Link to the dataset, which should be in excel and of the following format:

        |  Date        |  Players          |  Game        |  Scores                  |  Winner     | Version    |
        |  2018-11-18  |  Peter+Mike       |  Qwixx       |  Peter77+Mike77          |  Peter+Mike | Normal     |
        |  2018-11-18  |  Chris+Mike       |  Qwixx       |  Chris42+Mike99          |  Mike       | Big Points |
        |  2018-11-22  |  Mike+Chris       |  Jaipur      |  Mike84+Chris91          |  Chris      | Normal     |
        |  2018-11-30  |  Peter+Chris+Mike |  Kingdomino  |  Chris43+Mike37+Peter35  |  Chris      | 5x5        |

    Returns:
    --------

    df : pandas.core.frame.DataFrame
        The preprocessed data to be used for the analyses of played board game matches.

    player_list : list of str
        List of players
    """

    df = pd.read_excel(link)
    df.Date = pd.to_datetime(df.Date)

    player_list = extract_players(df)
    player_list.sort()

    for player in player_list:
        df[player + "_score"] = 0
        df[player + "_winner"] = 0
        df[player + "_played"] = 0
    df['has_score'] = 0
    df['has_winner'] = 0

    df = df.apply(lambda row: extract_score(row), 1)
    df = df.apply(lambda row: extract_winner(row, player_list), 1)
    df = df.apply(lambda row: extract_has_score(row, player_list), 1)
    df = df.apply(lambda row: extract_has_winner(row, player_list), 1)
    df = df.apply(lambda row: extract_has_played(row, player_list), 1)
    df['Nr_players'] = df.apply(lambda row: len(str(row.Players).split("+")), 1)

    return df, player_list


def extract_players(df: pd.DataFrame) -> List[str]:
    """ Extract a list of players

    Parameters:
    -----------
    df : pandas.core.frame.DataFrame
        The preprocessed data to be used for the analyses of played board game matches.

    Returns:
    --------
    player_list : list of str
        List of players
    """

    player_list = df.Players.unique()
    player_list = [players.split('+') for players in player_list]
    player_list = list(set([player for sublist in player_list for player in sublist]))
    return player_list


def extract_score(row: np.array) -> np.array:
    """ Extract the score per person by checking whether there are multiple players in the
    game which are connected with a + symbol
    """
    scores = str(row.Scores)

    if ("+" in scores) and (re.findall("\d+", scores)):
        scores = scores.split("+")

        scores_dict = {re.findall("[a-zA-Z]+", score)[0]:
                           re.findall("\d+", score)[0] for score in scores}

        for player in scores_dict.keys():
            row[player + '_score'] = int(scores_dict[player])

    return row


def extract_winner(row: np.array,
                   player_list: List[str]) -> np.array:
    """ Extract the winner(s) per game
    """

    winners = str(row.Winner).split("+")

    for winner in winners:
        if winner in player_list:
            row[winner + "_winner"] = 1

    return row


def extract_has_score(row: np.array,
                      player_list: List[str]) -> np.array:
    """Check whether the game actually has a score"""

    scores = 0

    for player in player_list:
        scores += row[player + "_score"]

    if scores > 0:
        row['has_score'] = 1

    return row


def extract_has_winner(row: np.array,
                       player_list: List[str]) -> np.array:
    """Check whether the game actually has a score"""

    for player in player_list:
        if row[player + "_winner"] == 1:
            row['has_winner'] = 1
            return row

    return row


def extract_has_played(row: np.array,
                       player_list: List[str]) -> np.array:
    """Check whether a person played in the game"""
    played = str(row.Players).split("+")

    for player in played:
        if player in player_list:
            row[player + "_played"] = 1

    return row
