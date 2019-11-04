import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

SPACES = '&nbsp;' * 10


def load_page(df, player_list):
    selection_df, selected_game = prepare_layout(df)
    plot_distribution(selection_df)
    frequent_players(selection_df, player_list)
    show_min_max_stats(selection_df, selected_game)
    sidebar_activity_plot(selection_df)


def prepare_layout(df):
    st.title("🎲 Explore games")
    st.write("In this section you can explore the games that were played in the last year. "
             "Note that some games have different versions wich are needed to select in order to continue. "
             "For example, Qwixx also has a 'Big Points' version which typically leads to much higher points. ")
    st.markdown("There are several things you see on this page:".format(SPACES))
    st.markdown("{}🔹 On the **left** you can see how often the selected game was played "
                "in the last year. ".format(SPACES))
    st.markdown("{}🔹 You can see the **distribution** of scores for the selected game. ".format(SPACES))
    st.markdown("{}🔹 The **frequency** of matches for each player. ".format(SPACES))
    st.markdown("{}🔹 The **top** and **bottom** players for the selected game.".format(SPACES))

    # Prepare ordered selection of games
    games = list(df.Game.unique())
    games.sort()

    # Select game and possibly a version of it
    selected_game = st.selectbox("Select a game to explore.", games)
    selection = df.loc[(df.Game == selected_game), :]
    versions = list(selection.Version.unique())
    versions.sort()
    if len(versions) > 1:
        version = st.selectbox("Select a game to explore.", versions)
        selection = selection.loc[selection.Version == version, :]

    return selection, selected_game


def plot_distribution(df):
    if sum(df.has_score.values) > 0:
        st.header("**♟** Distribution of Scores **♟**")
        st.write("Here, you can see the distribution of all scores that were achieved in the game. ")

        score_selection_df = df.loc[:, [column for column in df.columns
                                        if ('score' in column) & ('has_score' not in column)]]
        game_scores = np.array(score_selection_df)
        game_scores = pd.DataFrame(game_scores[game_scores.nonzero()], columns=['Scores'])

        chart = alt.Chart(game_scores).mark_bar().encode(
            alt.X("Scores:Q"),
            y='count()',
        )

        st.altair_chart(chart)


def show_min_max_stats(selection, selected_game):
    score_selection = selection.loc[:, [column for column in selection.columns
                                        if ('score' in column) & ('has_score' not in column)]]

    score_matrix = np.array(score_selection)

    # Calculate average scores per player
    averages = []
    for column in score_selection.columns:
        vals = score_selection[column].to_numpy()
        average_nonzero = np.mean(vals[vals.nonzero()])
        averages.append(average_nonzero)

    if not all(np.isnan(averages)):
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

        # Top players
        st.header("**♟** Top players **♟**")
        st.write("Here are the best players for the game **{}**:".format(selected_game))
        st.write("{}🔹 Highest score by **{}** with {} points".format(SPACES, max_player, max_score))
        st.write("{}🔸 Highest average score by **{}** with {} points".format(SPACES, high_avg_player, high_avg_player_val))
        st.write(" ")

        # Bottom players
        st.header("**♟** Bottom players **♟**")
        st.write("Here are the worst players for the game **{}**:".format(selected_game))
        st.write("{}🔹 Lowest (non-zero) score by **{}** with {} points".format(SPACES, min_player, min_score))
        st.write("{}🔸 Lowest average score by **{}** with {} points".format(SPACES, low_avg_player, low_avg_player_val))


def frequent_players(selection_df, player_list):
    st.header("**♟** Frequency of Matches **♟**")
    st.write("For each player, their total number of matches is displayed below.")

    # Calculate Frequencies
    frequency = [len(selection_df.loc[selection_df[player + "_played"] == 1, :]) for player in player_list]
    frequency = pd.DataFrame(np.array([player_list, frequency]).T, columns=['Player', 'Frequency'])

    # Visualize Results
    bars = alt.Chart(frequency,
                     height=200).mark_bar(color='#4db6ac').encode(
        x='Frequency:Q',
        y="Player:O"
    )

    text = bars.mark_text(
        align='left',
        baseline='middle',
        dx=3
    ).encode(
        text='Frequency:Q'
    )

    st.altair_chart(bars + text)


def sidebar_activity_plot(selection_df):
    selection_df = selection_df.sort_values("Date").set_index("Date").resample("3D").count().reset_index()
    chart = alt.Chart(selection_df).mark_area(
        color='goldenrod',
        opacity=1
    ).encode(
        x='Date',
        y=alt.Y('Players', title='Number of Games'),
    ).properties(background='transparent')

    st.sidebar.altair_chart(chart)

