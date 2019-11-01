import streamlit as st
import pandas as pd

# Custom packages
import statsperplayer
import general
import compare
import games
import preprocessing


def main():
    link_to_data, is_loaded_header = load_data_option()
    df, player_list, exception = load_external_data(link_to_data)

    if not exception:
        is_loaded_header.subheader("✔️Data is loaded")
        create_layout(df, player_list)
    else:
        st.sidebar.text(str(exception))
        st.title("⭕️The data was not correctly loaded")
        preprocessing_tips()



def load_data_option():
    """ Prepare options for loading data"""
    is_loaded_header = st.sidebar.subheader("⭕️ Data not loaded")
    link_to_data = st.sidebar.text_input('Link to data',
                                         "https://github.com/MaartenGr/boardgame/blob/dev/files/matches.xlsx?raw=true")

    return link_to_data, is_loaded_header


@st.cache
def load_external_data(link):
    """ Load data from a link and preprocess it"""
    exception = False
    try:
        df, player_list = preprocessing.prepare_data(link)
        return df, player_list, exception
    except Exception as exception:
        return False, False, exception


def load_homepage():
    st.image("https://raw.githubusercontent.com/MaartenGr/boardgame/dev/images/logo_small.jpg",
             use_column_width=True)
    st.markdown("> A Dashboard for the Board Game Geeks among us")
    st.write("As many Board Game Geeks like myself track the scores of board game matches "
             "I decided to create an application allowing for the exploration of this data. "
             "Moreover, it felt like a nice opportunity to see how much information can be "
             "extracted from relatively simple data.")
    st.write("As a Data Scientist and self-proclaimed Board Game Nerd I obviously made sure to "
             "write down the results of every board game I played. The data in the application "
             "is currently my own, but will be extended to include those of others.")
    st.markdown("<div align='center'><br>"
                "<img src='https://img.shields.io/badge/MADE%20WITH-PYTHON%20-red?style=for-the-badge'"
                "alt='API stability' height='25'/>"
                "<img src='https://img.shields.io/badge/SERVED%20WITH-Heroku-blue?style=for-the-badge'"
                "alt='API stability' height='25'/>"
                "<img src='https://img.shields.io/badge/DASHBOARDING%20WITH-Streamlit-green?style=for-the-badge'"
                "alt='API stability' height='25'/></div>", unsafe_allow_html=True)

    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.header("🎲 The Application")
    st.write("This application is a Streamlit dashboard hosted on Heroku that can be used to explore "
             "the results from board game matches that I tracked over the last year.")
    st.write("There are currently four pages available in the application:")
    st.subheader("♟ General Statistics ♟")
    st.markdown("* This gives a general overview of the data including frequency of games over time, "
                "most games played in a day, and longest break between games.")
    st.subheader("♟ Player Statistics ♟")
    st.markdown("* As you play with other people it would be interesting to see how they performed. "
                "This page allows you to see, per player, an overview of their performance across games.")
    st.markdown("* This also includes a one-sample Wilcoxon signed-rank test to test if a player performs "
                "significantly better/worse than the average for one board game.")
    st.subheader("♟ Head to Head ♟")
    st.markdown("* I typically play two-player games with my wife and thought it would be nice to include a "
                "head to head page. This page describes who is the better of two players between and within games.")
    st.subheader("♟ Explore Games ♟")
    st.markdown("* This page serves to show statistics per game, like its distribution of scores, frequency of "
                "matches and best/worst players.")


def create_layout(df, player_list):
    """ Create the layout after the data has succesfully loaded """
    st.sidebar.title("Menu")
    app_mode = st.sidebar.selectbox("Please select a page", ["Homepage",
                                                             "General Statistics",
                                                             "Player Statistics",
                                                             "Head to Head",
                                                             "Explore Games"])

    if app_mode == 'Homepage':
        load_homepage()
        preprocessing_tips()
    elif app_mode == "Instruction":
        body = " ".join(open("files/instructions.md", 'r').readlines())
        st.markdown(body, unsafe_allow_html=True)
    elif app_mode == "General Statistics":
        general.explore_data(df)
    elif app_mode == "Player Statistics":
        statsperplayer.stats_per_player(df, player_list)
    elif app_mode == "Head to Head":
        compare.compare_players(df, player_list)
    elif app_mode == "Explore Games":
        games.explore(df, player_list)


def preprocessing_tips():
    st.header("🎲 Tips for preparing your data")
    st.write("Make sure your dataset is in a xlsx (excel) format.")
    st.write("Make sure it has the structure as seen below with the exact same column names"
             ", same structure for scoring points, same structure for players that participated, and "
             "make sure to use the same date format. Any changes to this structure will break the "
             "application. ")
    example_df = pd.DataFrame([
        ['2018-11-18', 'Peter+Mike', 'Qwixx', 'Peter77+Mike77', 'Peter+Mike', 'Normal'],
        ['2018-11-18', 'Chris+Mike', 'Qwixx', 'Chris42+Mike99', 'Mike', 'Big Points'],
        ['2018-11-22', 'Mike+Chris', 'Jaipur', 'Mike84+Chris91', 'Chris', 'Normal'],
        ['2018-11-30', 'Peter+Chris+Mike', 'Kingdomino', 'Chris43+Mike37+Peter35', 'Chris', '5x5'],
    ], columns=['Date', 'Players', 'Game', 'Scores', 'Winner', 'Version'])

    st.write(example_df)

    st.write("An example of the data can be found here:")
    st.write("https://github.com/MaartenGr/boardgame/blob/dev/files/matches.xlsx")


if __name__ == "__main__":
    main()
