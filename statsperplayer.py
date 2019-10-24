import altair as alt
import streamlit as st
import pandas as pd


def stats_per_player(df, player_list, readme_text):
    """ The stats per player page"""
    # Prepare layout
    player = prepare_layout(player_list, readme_text)

    # Visualizations
    selection = score_per_player(df, player)
    stats_per_game(selection, player)
    show_raw_data(df)


def show_raw_data(df):
    raw_data = st.sidebar.checkbox("Show raw data")
    if raw_data:
        st.write(df)


def stats_per_game(df, player):
    st.subheader("Select a game to explore")
    st.write("Here, you can select which game you want to explore further for this person. "
             "It will show you general information such as the minimum and maximum scores for a specific "
             "game. ")
    selected_game = st.selectbox("Select a game to explore.", df.Game.unique())
    selection = df.loc[(df.Game == selected_game), :]
    plot_min_max(selection, player)


def plot_min_max(df, player):
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

    bars = alt.Chart(to_plot,
                     height=200).mark_bar(color='#4db6ac').encode(
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
    st.subheader("Average scores per game")
    st.write("The graph below shows you the average score per game for a single player. ")
    selection = df.loc[(df.has_score == 1) &
                       (df.has_winner == 1) &
                       (df[select_player + "_played"] == 1), :]
    grouped = selection.groupby("Game").mean()[[select_player + '_score']]
    plot_bar(grouped, select_player)

    return selection


def prepare_layout(player_list, readme_text):
    """Prepare selection box, title and empty previous readme"""
    st.sidebar.subheader("Choose a player")
    readme_text.empty()
    select_player = st.sidebar.selectbox("To show the scores for this player", player_list, index=0)
    st.title("Stats for {}".format(select_player))
    st.write("Below you can see statistics for a single player. "
             "This can relate to things like min, maximum and average scores "
             "but also how the performance of this person relates to all others he/she "
             "has played against.")
    return select_player


def plot_bar(df, player):
    """Plot a barchart using altair"""
    df = df.reset_index()
    bars = alt.Chart(df,
                     height=100 + (20 * len(df)),
                     title="Average scores per game").mark_bar(color='#4db6ac').encode(
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
