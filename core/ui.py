import os
import streamlit as st
from core.db import init_db
from core.seed import seed_if_empty
from core.style import inject_css

ROLES = ["Creator", "Reviewer", "Manager"]


def top_nav():
    cols = st.columns(4)
    cols[0].page_link("app.py", label="Home")
    cols[1].page_link("pages/1_Brand_Setup.py", label="Brand Setup")
    cols[2].page_link("pages/2_Review_Draft.py", label="Review Draft")
    cols[3].page_link("pages/3_Review_Queue.py", label="Review Queue")
    st.divider()


def _save_role():
    st.session_state.current_role = st.session_state.role_picker


def setup_page(page_title):
    st.set_page_config(
        page_title=f"{page_title} | ClearBrand",
        page_icon="assets/logo.png",
        layout="wide",
    )
    init_db()
    seed_if_empty()
    inject_css()

    if "current_role" not in st.session_state:
        st.session_state.current_role = ROLES[0]

    if os.path.exists("assets/logo.png"):
        st.logo("assets/logo.png", size="large")

    with st.sidebar:
        st.selectbox(
            "Your role",
            ROLES,
            index=ROLES.index(st.session_state.current_role),
            key="role_picker",
            on_change=_save_role,
        )
        st.caption("Demo role switcher. Each role sees different tools.")

    top_nav()
    return st.session_state.current_role