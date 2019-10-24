import streamlit as st
import plotly.graph_objects as go
import altair as alt
import numpy as np
import pandas as pd


def explore_data(df, readme_text):
    prepare_layout(readme_text, df)
    sidebar(df)
    plot_graph(df)


def sidebar(df):

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

    st.header("Total amount of times a game has been played")
    st.write("Below you can see the total amount of time a game has been played. I should note that these games"
             "can also be played with different number of people.")


def plot_graph(df):
    grouped_by_game = df.groupby("Game").count().reset_index()

    order_by = st.selectbox("Order by:", ["Name", "Amount"])
    if order_by == "Amount":
        bars = alt.Chart(grouped_by_game).mark_bar(color='#4db6ac').encode(
            x=alt.X('Players:Q', axis=alt.Axis(title='Total times played')),
            y=alt.Y('Game:O',
                    sort=alt.EncodingSortField(
                        field="Players",  # The field to use for the sort
                        order="descending"  # The order to sort in
                        )
                    )
            )
    else:
        bars = alt.Chart(grouped_by_game).mark_bar(color='#4db6ac').encode(
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
