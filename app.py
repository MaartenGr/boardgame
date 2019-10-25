import streamlit as st
import pandas as pd

# Custom packages
import statsperplayer
import general
import compare
import games


def main():
    df, player_list = load_data()

    body = " ".join(open("files/homepage.md", 'r').readlines())
    readme_text = st.markdown(body, unsafe_allow_html=True)

    st.sidebar.title("Menu")
    app_mode = st.sidebar.selectbox("Selecteer de modus", ["Homepage",
                                                           "General",
                                                           "Stats per player",
                                                           "Compare players",
                                                           "Explore games"])
    if app_mode == "Instruction":
        readme_text.empty()
        body = " ".join(open("files/instructions.md", 'r').readlines())
        st.markdown(body, unsafe_allow_html=True)
    elif app_mode == "General":
        general.explore_data(df, readme_text)
    elif app_mode == "Stats per player":
        statsperplayer.stats_per_player(df, player_list, readme_text)
    elif app_mode == "Compare players":
        readme_text.empty()
        st.title("Compare players")
        compare.compare_players(df, player_list)
    elif app_mode == "Explore games":
        readme_text.empty()
        games.explore(df)


# @st.cache
def load_data():
    df = pd.read_csv("https://github.com/MaartenGr/boardgame/raw/master/files/boardgame.csv")
    df.Date = pd.to_datetime(df.Date)
    player_list = df.Players.unique()
    player_list = [players.split('+') for players in player_list]
    player_list = list(set([player for sublist in player_list for player in sublist]))
    return df, player_list


if __name__ == "__main__":
    main()
