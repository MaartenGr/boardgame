import streamlit as st
import altair as alt
import numpy as np


def explore_data(df, readme_text):
    prepare_layout(readme_text, df)
    sidebar_activity_plot(df)
    plot_play_count_graph(df)
    longest_break_between_games(df)
    most_subsequent_days_played(df)
    most_games(df)


def sidebar_activity_plot(df):

    to_plot = df.sort_values("Date").set_index("Date").resample("3D").count().reset_index()

    chart = alt.Chart(to_plot).mark_area(
        color='goldenrod',
        opacity=1
    ).encode(
        x='Date',
        y='Players',
    )

    st.sidebar.altair_chart(chart)


def prepare_layout(readme_text, df):
    readme_text.empty()
    st.header("Data Exploration")
    st.write("This page contains basic exploratory data analyses for the purpose of getting a general "
             "feeling of what the data contains."
             " "
             " "
             " ")
    show_raw_data(df)

    st.subheader("Total amount of times a game has been played")
    st.write("Below you can see the total amount of time a game has been played. I should note that these games"
             "can also be played with different number of people.")


def plot_play_count_graph(df):
    grouped_by_game = df.groupby("Game").count().reset_index()

    order_by = st.selectbox("Order by:", ["Name", "Amount"])
    if order_by == "Amount":
        bars = alt.Chart(grouped_by_game,
                         height=100+(20*len(grouped_by_game))).mark_bar(color='#4db6ac').encode(
            x=alt.X('Players:Q', axis=alt.Axis(title='Total times played')),
            y=alt.Y('Game:O',
                    sort=alt.EncodingSortField(
                        field="Players",  # The field to use for the sort
                        order="descending"  # The order to sort in
                        )
                    )
            )
    else:
        bars = alt.Chart(grouped_by_game,
                         height=100+(20*len(grouped_by_game))).mark_bar(color='#4db6ac').encode(
            x=alt.X('Players:Q', axis=alt.Axis(title='Total times played')),
            y='Game:O',
        )

    text = bars.mark_text(
        align='left',
        baseline='middle',
        dx=3  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text='Players:Q'
    )

    st.write(bars + text)


def show_raw_data(df):
    checkbox = st.sidebar.checkbox("Show raw data")
    if checkbox:
        st.write(df)


def longest_break_between_games(df):
    """ Extract the longest nr of days between games """

    longest_not_played = 0
    day_previous = ""
    day_next = ""
    values = df.Date.values

    for i in range(len(df)-1):
        days = values[i+1] - values[i]
        days = days.astype('timedelta64[D]') / np.timedelta64(1, 'D')

        if days > longest_not_played:
            longest_not_played = int(days)
            day_previous = str(values[i]).split("T")[0]
            day_next = str(values[i+1]).split("T")[0]

    st.subheader("Longest break between games")
    st.write("The longest break between games was {} days between {} and {}.".format(longest_not_played,
                                                                                     day_previous,
                                                                                     day_next))


def most_subsequent_days_played(df):
    """ The largest number of subsequent days that games were played. """

    count = 0
    dates = df.Date.unique()
    most_subsequent_days = 0
    day_previous = ""
    day_next = ""

    for i in range(len(dates) - 1):
        days = dates[i + 1] - dates[i]
        days = days.astype('timedelta64[D]') / np.timedelta64(1, 'D')

        if days == 1:
            count += 1
        else:
            if count > most_subsequent_days:
                most_subsequent_days = count + 1  # Needed because it counts the days between and not the actual days

                day_next = str(dates[i + 1]).split("T")[0]
                day_previous = str(dates[i + 1] - np.timedelta64(count, 'D')).split("T")[0]
            count = 0

    st.subheader("Longest chain of games played")
    st.write("We played board games at most {} days in a row between {} and {}.".format(most_subsequent_days,
                                                                                        day_previous,
                                                                                        day_next))


def most_games(df):
    # Extract on which day the most games have been played
    grouped_date = df.groupby("Date").count()
    most_games_idx = grouped_date.Players.to_numpy().argmax()
    nr_games = grouped_date.Players.to_numpy().max()
    date = str(grouped_date.index[most_games_idx]).split(" ")[0]

    # Extract players in these games
    played = [column for column in df.columns if "_played" in column]
    played = df.loc[df.Date == date, played]
    played_idx = np.where(played.any(axis=0))[0]
    players = [player.split("_")[0] for player in played.columns[played_idx]]

    st.subheader("Most games")
    st.write("The most games were played on {} with {} games.".format(date, nr_games))
    st.write("Players involved: ")
    for player in players:
        st.write("  "*10+player)
