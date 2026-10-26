import streamlit as st
from core.db import init_db

init_db()

st.set_page_config(page_title="ClearBrand", page_icon="assets/logo.png", layout="wide")
ROLES = ["Creator", "Reviewer", "Manager"]

with st.sidebar:
    st.title("ClearBrand")
    st.selectbox("Your role", ROLES, key="role")
    st.caption("Demo role switcher. Each role sees different tools.")

st.title("ClearBrand")
st.subheader("Check content against approved brand rules before it is published")

st.write(
    "ClearBrand reviews a draft against your approved guidelines, facts and terminology, "
    "explains each issue with its source, and leaves the final decision to people."
)

st.info(f"You are using ClearBrand as: **{st.session_state.role}**")