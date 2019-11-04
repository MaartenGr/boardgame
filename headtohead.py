import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from typing import List, Tuple

SPACES = '&nbsp;' * 10


def load_page(df: pd.DataFrame,
              player_list: List[str]) -> None:
    """ In this section you can compare two players against each other based on their respective performances.

    Please note that the Head to Head section is meant for games that were played with 2 players against each other.

    Sections:
        * The Winner
        * Stats per Game

    Parameters:
    -----------

    df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.

    player_list : list of str
        List of players that participated in the board games
    """

    player_one, player_two = prepare_layout(player_list)
    two_player_matches, matches_df = check_if_two_player_matches_exist(df, player_one, player_two)

    if two_player_matches:
        sidebar_frequency_graph(matches_df)
        extract_winner(df, player_one, player_two)
        stats_per_game(matches_df, player_one, player_two)
    else:
        st.header("🏳️ Error")
        st.write("No two player matches were played with **{}** and **{}**. "
                 "Please select different players".format(player_one, player_two))


def prepare_layout(player_list: List[str]) -> Tuple[str, str]:
    """ Create the layout for the page including general selection options

    Parameters:
    -----------

    player_list : list of str
        List of players that participated in the board games
    """

    # Choose players
    st.title("🎲 Head to Head")
    st.write("In this section you can compare two players against each other based on their"
             "respective performances. Please note that the *Head to Head* section is meant for "
             "games that were played with 2 players against each other. ")

    st.sidebar.subheader("Please select two players")
    player_one = st.sidebar.selectbox("Select player one", player_list, index=0)
    player_two = st.sidebar.selectbox("Select player two", player_list, index=1)
    return player_one, player_two


def check_if_two_player_matches_exist(df: pd.DataFrame,
                                      player_one: str,
                                      player_two: str) -> Tuple[bool, pd.DataFrame]:
    """ Checks if player_one and player_two have played against each other in two player games


    Parameters:
    -----------

    df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.

    player_one : str
        One of the players in the game

    player_two : str
        One of the players in the game

    Returns:
    --------

    boolean
        True if there are matches played between player_one and player_two
        False otherwise

    matches_df: pandas.core.frame.DataFrame
        Data with only the two players selected and where two player games have been played
    """

    matches_df = df.loc[(df[player_one + "_played"] == 1) &
                        (df[player_two + "_played"] == 1) &
                        (df["Nr_players"] == 2), :]

    if (len(matches_df) == 0) | (player_one == player_two):
        return False, matches_df
    else:
        return True, matches_df


def sidebar_frequency_graph(matches_df: pd.DataFrame) -> None:
    """ Extracts and visualizes the frequency of games

    Parameters:
    -----------

    matches_df: pandas.core.frame.DataFrame
        Data with only the two players selected and where two player games have been played
    """

    to_plot = matches_df.sort_values("Date").set_index("Date").resample("3D").count().reset_index()
    chart = alt.Chart(to_plot).mark_area(
        color='goldenrod',
        opacity=1
    ).encode(
        x='Date',
        y=alt.Y('Players', title='Number of Games'),
    ).properties(background='transparent')

    if len(to_plot) > 0:
        st.sidebar.altair_chart(chart)


def extract_winner(df: pd.DataFrame,
                   player_one: str,
                   player_two: str) -> None:
    """ Extract the winner of the two players

    Parameters:
    -----------

    df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.

    player_one : str
        One of the players in the game

    player_two : str
        One of the players in the game
    """

    # Extract common games
    games = df.loc[(df[player_one + "_played"] == 1) &
                   (df[player_two + "_played"] == 1) &
                   (df["Nr_players"] == 2), :]
    player_one_won = len(games[games[player_one + "_winner"] == 1])
    player_two_won = len(games[games[player_two + "_winner"] == 1])
    to_plot = pd.DataFrame([[player_one_won, player_one],
                            [player_two_won, player_two]], columns=['Results', 'Player'])

    if player_one_won != player_two_won:
        if player_one_won > player_two_won:
            percentage = round(player_one_won / len(games) * 100, 2)
            winner = player_one
        else:
            percentage = round(player_two_won / len(games) * 100, 2)
            winner = player_two

        st.header("**♟** The Winner - {}**♟**".format(winner))
        st.write("The winner is decided simply by the amount of games won one by either player.")
        st.write("{}🔹 Out of {} games, {} games were won by **{}** "
                 "whereas {} games were won by **{}**".format(SPACES, len(games), player_one_won, player_one,
                                                              player_two_won, player_two))

        st.write("{}🔹 In other words, {}% of games were won by **{}** who is the clear winner!".format(SPACES,
                                                                                                        percentage,
                                                                                                        winner))
    else:
        winner = player_one + " and " + player_two
        st.header("**♟** The Winners - {}**♟**".format(winner))
        st.write("The winner is decided simply by the amount of games won one by either player.")
        st.write("{}🔹 Out of {} games, {} games were won by **{}** "
                 "whereas {} games were won by **{}**".format(SPACES, len(games), player_one_won, player_one,
                                                              player_two_won, player_two))
        st.write("{}🔹 In other words, it is a **tie**!".format(SPACES))

    bars = alt.Chart(to_plot).mark_bar().encode(
        x='Results:Q',
        y='Player:O',
        color='Player:O'
    )

    text = bars.mark_text(
        align='left',
        baseline='middle',
        dx=3  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text='Results:Q'
    )

    st.write(bars + text)


def stats_per_game(matches_df: pd.DataFrame,
                   player_one: str,
                   player_two: str) -> None:
    """ Show statistics per game


    Parameters:
    -----------

    matches_df : pandas.core.frame.DataFrame
        Data with only the two players selected and where two player games have been played

    player_one : str
        One of the players in the game

    player_two : str
        One of the players in the game
    """

    st.header("**♟** Stats per Game **♟**")
    st.write("Please select a game below to see the statistics for both players.")
    game_selection_df = game_selection(matches_df)
    scores_over_time(player_one, player_two, game_selection_df)
    general_stats_game(player_one, player_two, game_selection_df)


def game_selection(matches_df: pd.DataFrame) -> pd.DataFrame:
    """ Select game and filter data based on the game

    Parameters:
    -----------

    matches_df: pandas.core.frame.DataFrame
        Data with only the two players selected and where two player games have been played

    Returns:
    --------

    game_selection_df : pandas.core.frame.DataFrame
        Filtered data based on the selected game

    """
    games = list(matches_df.Game.unique())
    games.sort()
    game = st.selectbox("Select a game", games)
    game_selection_df = matches_df.loc[(matches_df.Game == game), :]
    return game_selection_df


def scores_over_time(player_one: str,
                     player_two: str,
                     game_selection_df: pd.DataFrame) -> None:
    """ Visualize scores over time for a specific game for two players

    Parameters:
    -----------

    player_one : str
        One of the players in the game

    player_two : str
        One of the players in the game

    game_selection_df : pandas.core.frame.DataFrame
        Filtered data based on the selected game
    """

    player_one_vals = list(game_selection_df[player_one + '_score'].values)
    player_two_vals = list(game_selection_df[player_two + '_score'].values)
    vals = player_one_vals + player_two_vals
    player_indices = [player_one if i < len(player_one_vals) else player_two for i, _ in enumerate(vals)]
    indices = list(np.arange(len(vals) / 2))
    indices = indices + indices

    to_plot = pd.DataFrame(np.array([indices, vals, player_indices]).T, columns=['Indices', 'Scores', 'Players'])
    to_plot.Indices = to_plot.Indices.astype(float)
    to_plot.Scores = to_plot.Scores.astype(float)

    st.write("Here you can see how games have progressed since the beginning. There is purposefully"
             " no time displayed as that might clutter the visualization. All scores on the left hand side"
             " were the first matches and scores on the right are the last.")
    colors = ['#2196F3', '#FF5722']
    chart = alt.Chart(to_plot,
                      title="Scores over time").mark_line().encode(
        alt.X('Indices', axis=None, scale=alt.Scale(domain=(0, max(to_plot.Indices)))),
        y='Scores:Q',
        color=alt.Color('Players', scale=alt.Scale(range=colors))
    ).configure_axis(
        grid=False
    ).configure_view(
        strokeOpacity=0
    )
    st.altair_chart(chart)


def general_stats_game(player_one: str,
                       player_two: str,
                       game_selection_df: pd.DataFrame) -> None:
    """ Show general statistics of a specific game for two players

    Parameters:
    -----------

    player_one : str
        One of the players in the game

    player_two : str
        One of the players in the game

    game_selection_df : pandas.core.frame.DataFrame
        Filtered data based on the selected game
    """

    result = pd.DataFrame(columns=['Player', 'Avg', 'Min', 'Max', 'Number'])

    for player in [player_one, player_two]:
        values = game_selection_df.loc[(game_selection_df[player + "_played"] == 1), player + "_score"].values
        result.loc[len(result), :] = [player, round(np.mean(values)), min(values),
                                      max(values), len(values)]

    st.write("You can see the average statistics for each player such that comparison is possible.")
    bars = alt.Chart(result).mark_bar().encode(
        x='Avg:Q',
        y='Player:O',
        color='Player:O'
    ).properties(
        title='Statistics'
    )

    text = bars.mark_text(
        align='left',
        baseline='middle',
        dx=3  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text='Avg:Q'
    )

    st.write(bars + text)
