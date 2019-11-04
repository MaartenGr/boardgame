import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

SPACES = '&nbsp;' * 10


def load_page(df, player_list):
    player_one, player_two = prepare_layout(player_list)
    two_player_matches, matches_df = check_if_two_player_matches_exist(df, player_one, player_two)

    if two_player_matches:
        sidebar_graph(matches_df, player_one, player_two)
        general_stats(df, player_one, player_two)
        stats_per_game(player_one, player_two, matches_df)
    else:
        st.header("🏳️ Error")
        st.write("No two player matches were played with **{}** and **{}**. "
                 "Please select different players".format(player_one, player_two))


def check_if_two_player_matches_exist(df, player_one, player_two):
    games = df.loc[(df[player_one + "_played"] == 1) &
                   (df[player_two + "_played"] == 1) &
                   (df["Nr_players"] == 2), :]

    if (len(games) == 0) | (player_one == player_two):
        return False, games
    else:
        return True, games


def prepare_layout(player_list):
    # Choose players
    st.title("🎲 Head to Head")
    st.write("In this section you can compare two players against each other based on their"
             "respective performances. Please note that the *Head to Head* section is meant for "
             "games that were played with 2 players against each other. ")

    st.sidebar.subheader("Please select two players")
    player_one = st.sidebar.selectbox("Select player one", player_list, index=0)
    player_two = st.sidebar.selectbox("Select player two", player_list, index=1)
    return player_one, player_two


def sidebar_graph(df, player_one, player_two):
    to_plot = df.sort_values("Date").set_index("Date").resample("3D").count().reset_index()

    chart = alt.Chart(to_plot).mark_area(
        color='goldenrod',
        opacity=1
    ).encode(
        x='Date',
        y=alt.Y('Players', title='Number of Games'),
    ).properties(background='transparent')

    if len(to_plot) > 0:
        st.sidebar.altair_chart(chart)


def compare_bars(df, player_one, player_two):
    """ Compare the average performance between players
    """
    st.header("**♟** Stats per Game **♟**")
    st.write("Check the box below if you want to see aggregate statistics for each board game.")

    compare = st.checkbox("Show stats per game")
    if compare:
        players = [player_one, player_two]
        selection = df.loc[(df[player_one + "_played"] == 1) &
                           (df[player_two + "_played"] == 1) &
                           (df["has_score"] > 0) &
                           (df["Nr_players"] == 2), :]
        games = selection.Game.unique()
        result = pd.DataFrame(columns=['Player', 'Game', 'Avg', 'Min', 'Max', 'Number'])

        for player in players:
            for game in games:
                values = selection.loc[(selection['Game'] == game) &
                                       (selection[player + "_played"] == 1), player + "_score"].values
                result.loc[len(result), :] = [player, game, round(np.mean(values)), min(values),
                                              max(values), len(values)]

        # Make sure values are correct format
        for column in ['Avg', 'Min', 'Max', 'Number']:
            result[column] = result[column].astype(float)
        result.Game = result.Game.astype(object)
        result.Player = result.Player.astype(object)

        # Plot barchart for each game as grouped bar is currently
        # not working in streamlit
        for game in result.Game.unique():
            # Chart graph
            to_plot = result.loc[result.Game == game, :]
            bars = alt.Chart(to_plot).mark_bar().encode(
                x='Avg:Q',
                y='Player:O',
                color='Player:O'
            ).properties(
                title='{}'.format(game)
            )

            text = bars.mark_text(
                align='left',
                baseline='middle',
                dx=3  # Nudges text to right so it doesn't appear on top of the bar
            ).encode(
                text='Avg:Q'
            )

            st.write(bars + text)


def general_stats(df, player_one, player_two):
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


def score_comparison(player_one, player_two, selection):
    player_one_vals = list(selection[player_one + '_score'].values)
    player_two_vals = list(selection[player_two + '_score'].values)
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


def game_selection(matches_df):
    games = list(matches_df.Game.unique())
    games.sort()
    game = st.selectbox("Select a game", games)
    selection = matches_df.loc[(matches_df.Game == game), :]

    return selection, game


def stats_per_game(player_one, player_two, matches_df):
    st.header("**♟** Stats per Game **♟**")
    st.write("Please select a game below to see the statistics for both players.")
    selection, _ = game_selection(matches_df)
    score_comparison(player_one, player_two, selection)
    general_stats_game(player_one, player_two, selection)


def general_stats_game(player_one, player_two, selection):
    result = pd.DataFrame(columns=['Player', 'Avg', 'Min', 'Max', 'Number'])

    for player in [player_one, player_two]:
        values = selection.loc[(selection[player + "_played"] == 1), player + "_score"].values
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
