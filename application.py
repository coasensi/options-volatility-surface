import streamlit as st
from pages import page1, page2, page3

pages = {
    "Home": page1,
    "IV": page2,
    "Page 3": page3,
}

st.sidebar.title("Choose your fighter")
# sidebar page selection
selection = st.sidebar.radio("Go to", list(pages.keys()))
page = pages[selection]
page.app()
