import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import statsperplayer as spp
import general as gn


def main():
    df, player_list = load_data()

    body = " ".join(open("homepage.md", 'r').readlines())
    readme_text = st.markdown(body, unsafe_allow_html=True)

    st.sidebar.title("Menu")
    app_mode = st.sidebar.selectbox("Selecteer de modus", ["Homepage", "General",
                                                           "Stats per player", "Compare players"])
    if app_mode == "Instruction":
        readme_text.empty()
        body = " ".join(open("instructions.md", 'r').readlines())
        st.markdown(body, unsafe_allow_html=True)
    elif app_mode == "General":
        gn.explore_data(df, readme_text)
    elif app_mode == "Stats per player":
        spp.stats_per_player(df, player_list, readme_text)
    elif app_mode == "Compare players":
        readme_text.empty()
        st.title("Compare players")


@st.cache
def load_data():
    df = pd.read_csv("boardgame.csv")
    player_list = df.Players.unique()
    player_list = [players.split('+') for players in player_list]
    player_list = list(set([player for sublist in player_list for player in sublist]))

    return df, player_list


if __name__ == "__main__":
    main()
