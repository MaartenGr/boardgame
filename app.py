from typing import List, Tuple
import streamlit as st
import pandas as pd

# Custom packages
import playerstats
import generalstats
import headtohead
import exploregames
import preprocessing


def main():
    link_to_data, is_loaded_header = load_data_option()
    df, player_list, exception = load_external_data(link_to_data)

    if not exception:
        create_layout(df, player_list, is_loaded_header)
    else:
        st.sidebar.text(str(exception))
        st.title("⭕️The data was not correctly loaded")
        preprocessing_tips()


def load_data_option() -> Tuple[str, st.DeltaGenerator.DeltaGenerator]:
    """ Prepare options for loading data"""
    is_loaded_header = st.sidebar.subheader("⭕️ Data not loaded")
    link_to_data = st.sidebar.text_input('Link to data',
                                         "https://github.com/MaartenGr/boardgame/blob/master/files/matches.xlsx?raw=true")

    return link_to_data, is_loaded_header


@st.cache
def load_external_data(link: str) -> Tuple[pd.DataFrame, List[str], Exception]:
    """ Load data from a link and preprocess it

    Parameters:
    -----------

    link : str
        Link to the data (should be hosted online)

    Returns:
    --------

    df : pandas.core.frame.DataFrame | False
        The data loaded and preprocessed.
        If there is an issue loading/preprocessing then it
        returns False instead.

    player_list : list | False
        List of players that have been in any board game match.
        If there is an issue with loading/preprocessing the data
        then it returns False instead.

    exception : False | Exception
        If there is something wrong with preprocessing,
        return Exception, otherwise return False
    """

    exception = False
    try:
        df, player_list = preprocessing.prepare_data(link)
        return df, player_list, exception
    except Exception as exception:
        return False, False, exception


def load_homepage() -> None:
    """ The homepage is loaded using a combination of .write and .markdown.
    Due to some issues with emojis incorrectly loading in markdown st.write was
    used in some cases.

    When this issue is resolved, markdown will be used instead.

    """
    st.image("https://raw.githubusercontent.com/MaartenGr/boardgame/master/images/logo_small.jpg",
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
    for i in range(3):
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


def create_layout(df: pd.DataFrame,
                  player_list: List[str],
                  is_loaded_header: st.DeltaGenerator.DeltaGenerator) -> None:
    """ Create the layout after the data has succesfully loaded

    Parameters:
    -----------

    df : pandas.core.frame.DataFrame
        The data to be used for the analyses of played board game matches.

        Make sure the data has the following structure:
        |  Date        |  Players          |  Game        |  Scores                  |  Winner     | Version    |
        |  2018-11-18  |  Peter+Mike       |  Qwixx       |  Peter77+Mike77          |  Peter+Mike | Normal     |
        |  2018-11-18  |  Chris+Mike       |  Qwixx       |  Chris42+Mike99          |  Mike       | Big Points |
        |  2018-11-22  |  Mike+Chris       |  Jaipur      |  Mike84+Chris91          |  Chris      | Normal     |
        |  2018-11-30  |  Peter+Chris+Mike |  Kingdomino  |  Chris43+Mike37+Peter35  |  Chris      | 5x5        |

    player_list : list of str
        List of players that participated in the board games

    is_loaded_header : streamlit.DeltaGenerator.DeltaGenerator
        Sidebar subheader to be changed if Data is (not) loaded

    """

    is_loaded_header.subheader("✔️Data is loaded")
    st.sidebar.title("Menu")
    app_mode = st.sidebar.selectbox("Please select a page", ["Homepage",
                                                             "Data Exploration",
                                                             "Player Statistics",
                                                             "Game Statistics",
                                                             "Head to Head"])
    if app_mode == 'Homepage':
        load_homepage()
        preprocessing_tips()
    elif app_mode == "Instruction":
        body = " ".join(open("files/instructions.md", 'r').readlines())
        st.markdown(body, unsafe_allow_html=True)
    elif app_mode == "Data Exploration":
        generalstats.load_page(df)
    elif app_mode == "Player Statistics":
        playerstats.load_page(df, player_list)
    elif app_mode == "Game Statistics":
        exploregames.load_page(df, player_list)
    elif app_mode == "Head to Head":
        headtohead.load_page(df, player_list)


def preprocessing_tips() -> None:
    """ Description of how to process the data and in which format. """
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
