import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker



def main():
    df = load_data()

    body = " ".join(open("homepage.md", 'r').readlines())
    readme_text = st.markdown(body, unsafe_allow_html=True)

    st.sidebar.title("Menu")
    app_mode = st.sidebar.selectbox("Selecteer de modus", ["Homepage", "Explore Data", "Stats per Player"])
    if app_mode == "Instruction":
        readme_text.empty()
        body = " ".join(open("instructions.md", 'r').readlines())
        readme_text = st.markdown(body, unsafe_allow_html=True)
    elif app_mode == "Explore Data":
        readme_text.empty()
        explore_data(df)
    elif app_mode == "Stats per Player":
        readme_text.empty()
        st.write("Stats per Player")

        df, colors, group_lk = load_data_test()

        for i in range(50):
            draw_barchart(1900+i, df, colors, group_lk)

@st.cache
def load_data_test():
    df = pd.read_csv('https://gist.githubusercontent.com/johnburnmurdoch/4199dbe55095c3e13de8d5b2e5e5307a/raw/fa018b25c24b7b5f47fd0568937ff6c04e384786/city_populations',
                 usecols=['name', 'group', 'year', 'value'])
    colors = dict(zip(
        ['India', 'Europe', 'Asia', 'Latin America',
         'Middle East', 'North America', 'Africa'],
        ['#adb0ff', '#ffb3ff', '#90d595', '#e48381',
         '#aafbff', '#f7bb5f', '#eafb50']
    ))
    group_lk = df.set_index('name')['group'].to_dict()
    return df, colors, group_lk


@st.cache
def load_data():
    df = pd.read_excel("matches.xlsx")
    return df


fig, ax = plt.subplots(figsize=(15, 8))


def draw_barchart(year, df, colors, group_lk):
    dff = df[df['year'].eq(year)].sort_values(by='value', ascending=True).tail(10)
    ax.clear()
    ax.barh(dff['name'], dff['value'], color=[colors[group_lk[x]] for x in dff['name']])
    dx = dff['value'].max() / 200
    for i, (value, name) in enumerate(zip(dff['value'], dff['name'])):
        ax.text(value - dx, i, name, size=14, weight=600, ha='right', va='bottom')
        ax.text(value - dx, i - .25, group_lk[name], size=10, color='#444444', ha='right', va='baseline')
        ax.text(value + dx, i, f'{value:,.0f}', size=14, ha='left', va='center')
    # ... polished styles
    ax.text(1, 0.4, year, transform=ax.transAxes, color='#777777', size=46, ha='right', weight=800)
    ax.text(0, 1.06, 'Population (thousands)', transform=ax.transAxes, size=12, color='#777777')
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_ticks_position('top')
    ax.tick_params(axis='x', colors='#777777', labelsize=12)
    ax.set_yticks([])
    ax.margins(0, 0.01)
    ax.grid(which='major', axis='x', linestyle='-')
    ax.set_axisbelow(True)
    ax.text(0, 1.12, 'The most populous cities in the world from 1500 to 2018',
            transform=ax.transAxes, size=24, weight=600, ha='left')
    ax.text(1, 0, 'by @pratapvardhan; credit @jburnmurdoch', transform=ax.transAxes, ha='right',
            color='#777777', bbox=dict(facecolor='white', alpha=0.8, edgecolor='white'))
    plt.box(False)
    st.pyplot(plt)


def explore_data(df):
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


if __name__ == "__main__":
    main()
