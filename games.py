import streamlit as st
import numpy as np
import pandas as pd
import altair as alt


def explore(df):
    selection_df, selected_game = prepare_layout(df)
    score_selection = plot_distribution(selection_df)
    show_min_max_stats(score_selection)
    sidebar_activity_plot(selection_df)


def show_min_max_stats(score_selection):
    score_matrix = np.array(score_selection)

    # Calculate average scores per player
    averages = []
    for column in score_selection.columns:
        vals = score_selection[column].to_numpy()
        average_nonzero = np.mean(vals[vals.nonzero()])
        averages.append(average_nonzero)

    # Extract player with lowest average score
    low_avg_player_idx = np.nanargmin(averages)
    low_avg_player_val = averages[low_avg_player_idx]
    low_avg_player = score_selection.columns[low_avg_player_idx].split("_")[0]

    # Extract player with highest average score
    high_avg_player_idx = np.nanargmax(averages)
    high_avg_player_val = averages[high_avg_player_idx]
    high_avg_player = score_selection.columns[high_avg_player_idx].split("_")[0]

    # Get max score
    max_x, max_y = np.unravel_index(np.argmax(score_matrix, axis=None), score_matrix.shape)
    max_player = score_selection.columns[max_y].split("_")[0]
    max_score = score_selection[score_selection.columns[max_y]].values[max_x]

    # Get min score
    min_x, min_y = np.where(
                            score_matrix == np.min(
                                score_matrix[np.nonzero(score_matrix)]))  # get indices of non-zero minimum
    min_player = score_selection.columns[min_y[0]].split("_")[0]
    min_score = score_matrix[min_x[0]][min_y[0]]

    # Write results
    st.subheader("Top players")
    st.write("Highest score by {} with {} points".format(max_player, max_score))
    st.write("Highest average score by {} with {} points".format(high_avg_player,
                                                                 high_avg_player_val))
    st.subheader("Bottom players")
    st.write("Lowest (non-zero) score by {} with {} points".format(min_player, min_score))
    st.write("Lowest average score by {} with {} points".format(low_avg_player,
                                                                low_avg_player_val))


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


def sidebar_activity_plot(selection_df):
    selection_df = selection_df.sort_values("Date").set_index("Date").resample("3D").count().reset_index()

    chart = alt.Chart(selection_df).mark_area(
        color='goldenrod',
        opacity=1
    ).encode(
        x='Date',
        y='Players',
    )

    st.sidebar.altair_chart(chart)

