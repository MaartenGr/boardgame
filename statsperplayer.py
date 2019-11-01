import altair as alt
import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

SPACES = '&nbsp;' * 10
SPACES_NO_EMOJI = '&nbsp;' * 15


def stats_per_player(df, player_list):
    """ The stats per player page"""
    # Prepare layout
    player = prepare_layout(player_list)
    selection, grouped = score_per_player(df, player)

    # Visualizations
    plot_bar(grouped, player)
    selected_game_df = stats_per_game(selection, player)
    statistical_difference(selected_game_df, player)
    performance(selection, player)


def stats_per_game(df, player):
    st.header("**♟** Explore a Game **♟**")
    st.write("Here, you can select which game you want to explore further for this person. "
             "It will show you general information such as the minimum and maximum scores for a specific "
             "game. ")
    games = list(df.Game.unique())
    games.sort()
    selected_game = st.selectbox("Select a game to explore.", games)
    selection = df.loc[(df.Game == selected_game), :]
    plot_min_max(selection, player)
    plot_scores_over_time(selection, player)
    return selection


def plot_scores_over_time(selection, player):
    selection = selection[player + '_score'].values
    to_plot = pd.DataFrame(np.array([selection, np.arange(len(selection))]).T, columns=['Score', 'Player'])

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


def statistical_difference(selection, player):
    """ Calculate, for one board game, if there is a significant difference
    between the average score (excluded the selected player) and all scores of a player
    across all matches of the selected board game.

    This was calculated using the Wilcoxon signed rank test due to the expectation
    of non-normally distributed data.
    """
    st.header("**♟** Statistical Difference **♟**")
    st.markdown("Here, you can see if there is a statistical difference between the scores"
                "of the selected person and the selected game, and the average score of all other"
                "players for the same game.")
    # Extract average score of game without player and player values for game
    score_selection = selection.loc[:, [column for column in selection.columns
                                        if (('score' in column) &
                                            ('has_score' not in column) &
                                            (player + '_score' not in column))]]
    score_selection = score_selection.to_numpy()
    average_score = np.mean(score_selection[np.nonzero(score_selection)])
    player_values = selection[player + "_score"].values

    # Use an one-sample Wilcoxon signed-rank test if sufficient n
    if len(player_values) > 15:
        p = wilcoxon(player_values-average_score)
        if p[1] < 0.05:
            st.write("{}🔹 According to a **one-sample Wilcoxon signed-rank test**".format(SPACES))
            st.write("{}🔹 there **is** a significant difference between the scores of **{}** "
                     "(mean score of {}) ".format(SPACES, player, round(np.mean(player_values), 2)))
            st.write("{}🔹 and the average (score of {}).".format(SPACES, round(average_score, 2)))

        else:
            st.write("{}🔹 According to an one-sample Wilcoxon signed-rank test there "
                     "is no significant difference between the scores of {} (mean score "
                     "of {}) and the average (score of {}).".format(SPACES,
                                                                    player,
                                                                    round(np.mean(player_values), 2),
                                                                    round(average_score, 2)))
    else:
        st.write("{}🔹 Insufficient data to run statistical test. A minimum of "
                 "**15** matches is necessary.".format(SPACES))
    st.write(" ")


def plot_min_max(df, player):
    """ Plot several statistics for a board game """
    # Prepare statistics
    min_score = df[player+"_score"].min()
    max_score = df[player+"_score"].max()
    mean_score = df[player + "_score"].mean()
    median_score = df[player + "_score"].median()
    nr_played = len(df)
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
        x='Score:Q'.format(player),
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


def score_per_player(df, select_player):
    """Plot score per player"""
    st.header("**♟** Average Score per Game **♟**")
    st.write("The graph below shows you the average score per game for a single player. ")
    selection = df.loc[(df.has_score == 1) &
                       (df.has_winner == 1) &
                       (df[select_player + "_played"] == 1), :]
    grouped = selection.groupby("Game").mean()[[select_player + '_score']]

    return selection, grouped


def prepare_layout(player_list):
    """Prepare selection box, title and empty previous readme"""
    st.sidebar.subheader("Choose a player")
    select_player = st.sidebar.selectbox("To show the scores for this player", player_list, index=0)
    st.title("🎲 Player Statistics for {}".format(select_player))
    st.write("Below you can see statistics for a single player. "
             "This can relate to things like min, maximum and average scores "
             "but also how the performance of this person relates to all others he/she "
             "has played against.")

    st.markdown("There are several things you see on this page:".format(SPACES))
    st.markdown("{}🔹 An overview of the **average** scores per game.".format(SPACES))
    st.markdown("{}🔹 An **in-depth** overview of statistics per game.".format(SPACES))
    st.markdown("{}🔹 Whether there is a **significant** difference in scores for a game.".format(SPACES))
    st.markdown("{}🔹 The **performance** of a player across all games.".format(SPACES))
    st.markdown("<br>", unsafe_allow_html=True)
    return select_player


def plot_bar(df, player):
    """Plot a barchart using altair"""
    df = df.reset_index()
    bars = alt.Chart(df,
                     height=100 + (20 * len(df)),
                     title="Average score per game").mark_bar(color='#4db6ac').encode(
        x='{}_score:Q'.format(player),
        y="Game:O"
    )

    text = bars.mark_text(
        align='left',
        baseline='middle',
        dx=3  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text='{}_score:Q'.format(player)
    )

    st.altair_chart(bars + text)


def performance(selection, player):
    played = len(selection)
    won = len(selection.loc[selection[player + '_winner'] == 1, :])
    percentage = round(won / played * 100, 1)
    st.header("**♟** Performance **♟**")
    st.write("This section describes the performance of the player based on "
             "how frequently this person has won a game.")
    st.markdown("{}🔹 Player **{}** has won **{}** out of **{}** "
                "games which is **{}** percent of games".format(SPACES, player, won, played, percentage))
