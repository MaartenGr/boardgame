import streamlit as st


def main():
    body = " ".join(open("homepage.md", 'r').readlines())
    readme_text = st.markdown(body, unsafe_allow_html=True)

    st.sidebar.title("Menu")
    app_mode = st.sidebar.selectbox("Selecteer de modus", ["Homepage", "Instruction", "Turnover Prediction"])
    if app_mode == "Instruction":
        readme_text.empty()
        body = " ".join(open("instructions.md", 'r').readlines())
        readme_text = st.markdown(body, unsafe_allow_html=True)
    elif app_mode == "Turnover Prediction":
        readme_text.empty()


if __name__ == "__main__":
    main()
