import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

SPACES = '&nbsp;' * 10


def load_page(df: pd.DataFrame) -> None:
    """ The Data Exploration Page

    Sections:
        * On the left you can see how often games were played in the last year of matches.
        * You can see the total amount certain board games have been played.
        * The longest break between board games.
        * The longest chain of games played in days.
        * The day most games have been played.

    Parameters:
    -----------

    df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.
    """

    prepare_layout()
    sidebar_activity_plot(df)
    plot_play_count_graph(df)
    longest_break_between_games(df)
    most_subsequent_days_played(df)
    most_games_on_one_day(df)


def sidebar_activity_plot(df: pd.DataFrame) -> None:
    """ Show the frequency of played games in the sidebar

    Parameters:
    -----------

    df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.
    """

    to_plot = df.sort_values("Date").set_index("Date").resample("3D").count().reset_index()
    chart = alt.Chart(to_plot).mark_area(
        color='goldenrod',
        opacity=1
    ).encode(
        x='Date',
        y=alt.Y('Players', title='Number of Games'),
    ).properties(background='transparent')

    st.sidebar.altair_chart(chart)


def prepare_layout() -> None:
    """ Prepare the text of the page at the top """
    st.title("🎲 Data Exploration")
    st.write("This page contains basic exploratory data analyses for the purpose of getting a general "
             "feeling of what the data contains. ".format(SPACES))
    st.markdown("There are several things you see on this page:".format(SPACES))
    st.markdown("{}🔹 On the **left** you can see how often games were played "
                "in the last year of matches. ".format(SPACES))
    st.markdown("{}🔹 You can see the **total amount** certain board games have been played. ".format(SPACES))
    st.markdown("{}🔹 The longest **break** between board games. ".format(SPACES))
    st.markdown("{}🔹 The **longest chain** of games played in days. ".format(SPACES))
    st.markdown("{}🔹 The **day** most games have been played. ".format(SPACES))
    st.write(" ")


def plot_play_count_graph(df: pd.DataFrame) -> None:
    """ Shows how often games were played

    Parameters:
    -----------

    df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.
    """

    st.header("**♟** Board Game Frequency **♟**")
    st.write("Below you can see the total amount of time a game has been played. I should note that these games "
             "can also be played with different number of people.")

    grouped_by_game = df.groupby("Game").count().reset_index()

    order_by = st.selectbox("Order by:", ["Amount", "Name"])
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

    average_nr_games_per_day = round(np.mean(df.groupby('Date').count().has_score), 2)
    st.write("On average {} games per day were played on days "
             "that there were board game matches".format(average_nr_games_per_day))


def longest_break_between_games(df: pd.DataFrame) -> None:
    """ Extract the longest nr of days between games

    Parameters:
    -----------

    df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.
    """

    dates = df.groupby("Date").count().index
    differences = [(dates[i],
                    dates[i + 1],
                    int((dates[i + 1] - dates[i]) / np.timedelta64(1, 'D')))
                   for i in range(len(dates) - 1)]
    differences = pd.DataFrame(differences, columns=['Start_date',
                                                     'End_date',
                                                     'Count']).sort_values('Count', ascending=False).head(5)

    st.header("**♟** Longest Break between Games **♟**")
    st.write("The longest breaks between games were:")

    for row in differences.iterrows():
        start_date = str(row[1].Start_date).split(" ")[0]
        end_date = str(row[1].End_date).split(" ")[0]
        st.markdown("{}🔹 **{}** days between **{}** and **{}**".format(SPACES, row[1].Count, start_date, end_date))
    st.write(" ")


def most_subsequent_days_played(df: pd.DataFrame) -> None:
    """ The largest number of subsequent days that games were played.

    Parameters:
    -----------

    df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.

    """

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

    st.header("**♟** Longest Chain of Games Played **♟**")
    st.write("The longest number of subsequent days we played games was:")
    st.write("{}🔸 **{}** days".format(SPACES, most_subsequent_days))
    st.write("{}🔹 between **{}** and **{}**".format(SPACES, day_previous, day_next))
    st.markdown("<br>", unsafe_allow_html=True)


def most_games_on_one_day(df: pd.DataFrame) -> None:
    """ Extract when the most games have been played on one day and how many

    Parameters:
    -----------

    df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.
    """

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

    # Write results to streamlit
    st.header("**♟** Most Games Played in One Day **♟**")
    st.write("The most games on a single day were played on:")
    st.write("{}🔸 **{}** with **{}** games.".format(SPACES, date, nr_games))
    st.write("Players that took in a part in at least one of the games: ")
    players = ["**" + player + "**" for player in players]
    players[-1] = 'and ' + players[-1]
    st.write("{}🔹 {}".format(SPACES, ", ".join(players)))
