import streamlit as st
import plotly.graph_objects as go


def explore_data(df, readme_text):
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
    grouped_by_game = df.groupby("Game").count()
    values = grouped_by_game.sort_values("Date").Date.values
    names = grouped_by_game.sort_values("Date").index
    trace = go.Bar(x=values, y=names, orientation='h', marker_color='#039BE5')
    layout = go.Layout(xaxis={"title": "", "showgrid": False, 'range': [-5, max(values)]},
                       yaxis={"title": "", "showgrid": False},
                       template='plotly_white',
                       height=500,
                       margin=dict(l=0, r=0, t=0, b=0),
                       )
    fig = {"data": [trace], "layout": layout}

    st.plotly_chart(fig, config={'displayModeBar': False})


def show_raw_data(df):
    checkbox = st.sidebar.checkbox("Show raw data")
    if checkbox:
        st.write(df)
