<img src="https://raw.githubusercontent.com/MaartenGr/boardgame/dev/images/logo_small.jpg">

> A Dashboard for the Board Game Geeks among us

[Link to Application](https://bgexploration.herokuapp.com/)

As many Board Game Geeks like myself track the scores of board game matches
I decided to create an application allowing for the exploration of this data.
Moreover, it felt like a nice opportunity to see how much information can be
extracted from relatively simple data.

As a Data Scientist and self-proclaimed Board Game Nerd I obviously made sure
to write down the results of every board game I played. The data in the application
is currently my own, but will be extended to include those of others.  

<div align="center">
  <br>
  <img src="https://img.shields.io/badge/MADE%20WITH-PYTHON%20-red?style=for-the-badge"
      alt="API stability" height="25"/>
  <img src="https://img.shields.io/badge/SERVED%20WITH-Heroku-blue?style=for-the-badge"
      alt="API stability" height="25"/>
  <img src="https://img.shields.io/badge/DASHBOARDING%20WITH-Streamlit-green?style=for-the-badge"
      alt="API stability" height="25"/>
</div>

![The Application](/images/streamlit_gif_large.gif)


### 🎲 The Application
This application is a Streamlit dashboard hosted on Heroku that can be used
to explore the results from board game matches that I tracked over the last year.

There are currently four pages available in the application:
* **♟ General Statistics ♟**
    * This gives a general overview of the data including
    frequency of games over time, most games played in a day, and longest break
    between games.
* **♟ Player Statistics ♟**
    * As you play with other people it would be interesting to see how they performed.
    This page allows you to see, per player, an overview of their performance across
    games.
    * This also includes a one-sample Wilcoxon signed-rank test to test if a player
    performs significantly better/worse than the average for one board game.
* **♟ Head to Head ♟**
    * I typically play two-player games with my wife and thought it would be nice
    to include a head to head page.
    This page describes who is the better of two players between and within games.
* **♟ Explore Games ♟**
    * This page serves to show statistics per game, like its distribution
    of scores, frequency of matches and best/worst players.  
