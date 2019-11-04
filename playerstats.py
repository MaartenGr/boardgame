import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from scipy.stats import wilcoxon
from typing import List, Tuple

SPACES = '&nbsp;' * 10
SPACES_NO_EMOJI = '&nbsp;' * 15


def load_page(df: pd.DataFrame,
              player_list: List[str]) -> None:
    """ The Player Statistics Page

    After filtering for a player, it includes the following sections:
        * Average Score per Game
            * Shows average score for all games played
        * Explore a Game
            * Gives general statistics for a specific game
        * Statistical Difference
            * Checks if there is a significant difference between scores of the user
            for a specific game and the average score
        * Performance
            * This section describes the performance of the player based on how
            frequently this person has won a game.

    Parameters:
    -----------

    df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.

    player_list : list of str
        List of players that participated in the board games
    """

    # Prepare layout
    selected_player = prepare_layout(player_list)
    player_selection_df, grouped_per_game_df = score_per_player(df, selected_player)

    # Visualizations
    plot_average_score_per_game(grouped_per_game_df, selected_player)
    calculate_stats_per_game(player_selection_df, selected_player)
    calculate_performance(player_selection_df, selected_player)


def calculate_stats_per_game(selection_df: pd.DataFrame,
                             selected_player: str) -> None:
    """ The Player Statistics for a specific game

    Parameters:
    -----------

    selection_df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.
        Note,

    player : str
        The selected player
    """

    # Prepare layout
    st.header("**♟** Explore a Game **♟**")
    st.write("Here, you can select which game you want to explore further for this person. "
             "It will show you general information such as the minimum and maximum scores for a specific "
             "game. ")
    games = list(selection_df.Game.unique())
    games.sort()
    selected_game = st.selectbox("Select a game to explore.", games)
    selected_game_df = selection_df.loc[(selection_df.Game == selected_game), :]

    # Create visualizations
    plot_general_stats(selected_game_df, selected_player)
    plot_scores_over_time(selected_game_df, selected_player)
    calculate_statistical_difference(selected_game_df, selected_player)


def plot_scores_over_time(selected_game_df: pd.DataFrame,
                          selected_player: str) -> None:
    """ Create a visualization allowing for scores to be shown over time

    Note that the x-axis does not show any time since it is based merely
    on subsequent games. Allowing for time to be displayed on the x-axis
    would likely result in many points clustered together as games are typically
    played multiple times on a day.


    Parameters:
    -----------

    selected_game_df : pandas.core.frame.DataFrame
        Data for the selected game

    selected_player : str
        The selected player
    """

    game_scores = selected_game_df[selected_player + '_score'].values
    to_plot = pd.DataFrame(np.array([game_scores, np.arange(len(game_scores))]).T, columns=['Score', 'Player'])

    chart = alt.Chart(to_plot,
                      title="Scores over time").mark_line(color='#4db6ac').encode(
        alt.X('Player', axis=None, scale=alt.Scale(domain=(0, max(to_plot.Player)))),
        y='Score'
    ).configure_axis(
        grid=False
    ).configure_view(
        strokeOpacity=0
    )

    st.altair_chart(chart)


def calculate_statistical_difference(selection: pd.DataFrame,
                                     selected_player: str) -> None:
    """ Calculate, for one board game, if there is a significant difference
    between the average score (excluded the selected player) and all scores of a player
    across all matches of the selected board game.

    This was calculated using the Wilcoxon signed rank test due to the expectation
    of non-normally distributed data.

    Parameters:
    -----------

    selected_game_df : pandas.core.frame.DataFrame
        Data for the selected game

    selected_player : str
        The selected player
    """

    st.header("**♟** Statistical Difference **♟**")
    st.markdown("Here, you can see if there is a statistical difference between the scores"
                "of the selected person and the selected game, and the average score of all other "
                "players for the same game.")
    # Extract average score of game without player and player values for game
    score_selection = selection.loc[:, [column for column in selection.columns
                                        if (('score' in column) &
                                            ('has_score' not in column) &
                                            (selected_player + '_score' not in column))]]
    score_selection = score_selection.to_numpy()
    average_score = np.mean(score_selection[np.nonzero(score_selection)])
    player_values = selection[selected_player + "_score"].values

    # Use an one-sample Wilcoxon signed-rank test if sufficient n
    if len(player_values) > 15:
        p = wilcoxon(player_values-average_score)
        if p[1] < 0.05:
            st.write("{}🔹 According to a **one-sample Wilcoxon signed-rank test**".format(SPACES))
            st.write("{}🔹 there **is** a significant difference between the scores of **{}** "
                     "(mean score of {}) ".format(SPACES, selected_player, round(np.mean(player_values), 2)))
            st.write("{}🔹 and the average (score of {}).".format(SPACES, round(average_score, 2)))

        else:
            st.write("{}🔹 According to an one-sample Wilcoxon signed-rank test there "
                     "is no significant difference between the scores of {} (mean score "
                     "of {}) and the average (score of {}).".format(SPACES,
                                                                    selected_player,
                                                                    round(np.mean(player_values), 2),
                                                                    round(average_score, 2)))
    else:
        st.write("{}🔹 Insufficient data to run statistical test. A minimum of "
                 "**15** matches is necessary.".format(SPACES))
    st.write(" ")


def plot_general_stats(selected_game_df: pd.DataFrame,
                       selected_player: str) -> None:
    """ Plot several statistics for the selected board game

    Parameters:
    -----------

    selected_game_df : pandas.core.frame.DataFrame
        Data for the selected game

    selected_player : str
        The selected player
    """

    # Prepare statistics
    min_score = selected_game_df[selected_player+"_score"].min()
    max_score = selected_game_df[selected_player+"_score"].max()
    mean_score = selected_game_df[selected_player + "_score"].mean()
    median_score = selected_game_df[selected_player + "_score"].median()
    nr_played = len(selected_game_df)
    to_plot = pd.DataFrame([[min_score, 'Minimum score'],
                            [max_score, 'Maximum score'],
                            [mean_score, 'Mean score'],
                            [median_score, 'Median score'],
                            [nr_played, 'Times played']], columns=['Score', 'Name'])

    # Visualize results
    st.write("Below you can see general statistisc for the selected game.")
    bars = alt.Chart(to_plot,
                     height=200,
                     title="General Statistics").mark_bar(color='#4db6ac').encode(
        x='Score:Q'.format(selected_player),
        y="Name:O"
    )
    text = bars.mark_text(
        align='left',
        baseline='middle',
        dx=3  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text='Score:Q'
    )

    st.altair_chart(bars + text)


def score_per_player(df: pd.DataFrame,
                     selected_player: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Plot score per player

    Parameters:
    -----------

    selected_game_df : pandas.core.frame.DataFrame
        Data for the selected game

    selected_player : str
        The selected player

    Returns:
    --------

    player_selection_df : pandas.core.frame.DataFrame
        Data for the selected player that has a score and a winner

    grouped_per_game_df : pandas.core.frame.DataFrame
        Data for the selected player where the average score
        per game were extracted
    """

    st.header("**♟** Average Score per Game **♟**")
    st.write("The graph below shows you the average score per game for a single player. ")
    player_selection_df = df.loc[(df.has_score == 1) &
                                 (df.has_winner == 1) &
                                 (df[selected_player + "_played"] == 1), :]
    grouped_per_game_df = player_selection_df.groupby("Game").mean()[[selected_player + '_score']]

    return player_selection_df, grouped_per_game_df


def prepare_layout(player_list: List[str]) -> str:
    """Prepare selection box, title and empty previous readme


    Parameters:
    -----------

    player_list : list of str
        List of players

    Returns:
    --------

    selected_player : str
    """

    st.sidebar.subheader("Choose a player")
    selected_player = st.sidebar.selectbox("To show the scores for this player", player_list, index=0)
    st.title("🎲 Player Statistics for {}".format(selected_player))
    st.write("Below you can see statistics for a single player. "
             "This can relate to things like min, maximum and average scores "
             "but also how the performance of this person relates to all others he/she "
             "has played against.")

    st.markdown("There are several things you see on this page:".format(SPACES))
    st.markdown("{}🔹 An overview of the **average** scores per game.".format(SPACES))
    st.markdown("{}🔹 An **in-depth** overview of statistics per game.".format(SPACES))
    st.markdown("{}🔹 Whether there is a **significant** difference in scores for a game.".format(SPACES))
    st.markdown("{}🔹 The **performance** of a player across all games.".format(SPACES))
    st.write(" ")
    return selected_player


def plot_average_score_per_game(grouped_per_game_df: pd.DataFrame,
                                selected_player: str) -> None:
    """Plot a barchart using altair

    Parameters:
    -----------

    grouped_per_game_df : pandas.core.frame.DataFrame
        Data for the selected game

    selected_player : str
        The selected player
    """

    grouped_per_game_df = grouped_per_game_df.reset_index()
    bars = alt.Chart(grouped_per_game_df,
                     height=100 + (20 * len(grouped_per_game_df)),
                     title="Average score per game").mark_bar(color='#4db6ac').encode(
        x='{}_score:Q'.format(selected_player),
        y="Game:O"
    )

    text = bars.mark_text(
        align='left',
        baseline='middle',
        dx=3  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text='{}_score:Q'.format(selected_player)
    )

    st.altair_chart(bars + text)


def calculate_performance(player_selection_df: pd.DataFrame,
                          selected_player: str) -> None:
    """ Calculate the performance of a player

    Parameters:
    -----------

    player_selection_df : pandas.core.frame.DataFrame
        Data for the selected player that has a score and a winner

    selected_player : str
        The selected player
    """

    played = len(player_selection_df)
    won = len(player_selection_df.loc[player_selection_df[selected_player + '_winner'] == 1, :])
    percentage = round(won / played * 100, 1)
    st.header("**♟** Performance **♟**")
    st.write("This section describes the performance of the player based on "
             "how frequently this person has won a game.")
    st.markdown("{}🔹 Player **{}** has won **{}** out of **{}** "
                "games which is **{}** percent of games".format(SPACES, selected_player, won, played, percentage))
