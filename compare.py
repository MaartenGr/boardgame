import altair as alt
import streamlit as st
import pandas as pd
import numpy as np


def compare_players(df, player_list):
    general_stats()
    compare_bars(df, player_list)


def compare_bars(df, player_list):
    """ Compare the average performance between players
    """
    # Choose players
    st.sidebar.subheader("Please select two players")
    player_one = st.sidebar.selectbox("Select player one", player_list, index=0)
    player_two = st.sidebar.selectbox("Select player two", player_list, index=1)
    players = [player_one, player_two]

    # Extract common games
    player_one_games = set(df.loc[df[player_one + "_played"] == 1, "Game"].unique())
    player_two_games = set(df.loc[df[player_two + "_played"] == 1, "Game"].unique())
    common_games = list(set.intersection(player_one_games, player_two_games))

    # Calculate statistics per game and player for comparison purposes
    selection = df.loc[((df[player_one + "_played"] == 1) | (df[player_two + "_played"] == 1)), :]
    intersection = pd.DataFrame(columns=['Player', 'Game', 'Avg', 'Min', 'Max', 'Number'])
    for game in common_games:
        for player in players:
            values = selection.loc[(selection['Game'] == game) &
                                   (selection[player + "_played"] == 1), player + "_score"].values
            intersection.loc[len(intersection), :] = [player, game, round(np.mean(values)), min(values),
                                                      max(values), len(values)]

    # Make sure values are correct format
    for column in ['Avg', 'Min', 'Max', 'Number']:
        intersection[column] = intersection[column].astype(float)
    intersection.Game = intersection.Game.astype(object)
    intersection.Player = intersection.Player.astype(object)

    # Plot barchart for each game as grouped bar is currently
    # not working in streamlit
    for game in intersection.Game.unique():
        # Chart graph
        to_plot = intersection.loc[intersection.Game == game, :]
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

        st.write(bars+text)


def general_stats():
    st.write("Player one has defeated player two in X times out of X games.")
