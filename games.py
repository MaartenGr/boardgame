import streamlit as st
import numpy as np
import pandas as pd
import altair as alt


def explore(df):
    selection, selected_game = prepare_layout(df)
    score_selection = plot_distribution(selection)
    show_min_max_stats(score_selection)


def show_min_max_stats(score_selection):
    score_matrix = np.array(score_selection)

    # Get max score
    max_x, max_y = np.unravel_index(np.argmax(score_matrix, axis=None), score_matrix.shape)
    max_player = score_selection.columns[max_y].split("_")[0]
    max_score = score_selection[score_selection.columns[max_y]].values[max_x]
    st.write("Highest score by {} with {} points".format(max_player, max_score))

    # Get min score
    min_x, min_y = np.unravel_index(np.argmin(score_matrix, axis=None), score_matrix.shape)
    min_player = score_selection.columns[min_y].split("_")[0]
    min_score = score_selection[score_selection.columns[min_y]].values[min_x]
    st.write("Lowest score by {} with {} points".format(min_player, min_score))
    st.write("Fix this, lowest score should be nonzero...")

def prepare_layout(df):
    st.title("Explore games")
    selected_game = st.selectbox("Select a game to explore.", df.Game.unique())
    selection = df.loc[(df.Game == selected_game), :]

    versions = selection.Version.unique()
    if len(versions) > 1:
        version = st.selectbox("Select a game to explore.", versions)
        selection = selection.loc[selection.Version == version, :]

    return selection, selected_game


def plot_distribution(df):
    df = df.loc[:, [column for column in df.columns if ('score' in column) & ('has_score' not in column)]]

    game_scores = np.array(df)
    game_scores = pd.DataFrame(game_scores[game_scores.nonzero()], columns=['Scores'])

    chart = alt.Chart(game_scores).mark_bar().encode(
        alt.X("Scores:Q"),
        y='count()',
    )

    st.altair_chart(chart)

    return df
