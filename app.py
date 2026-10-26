import streamlit as st
from core.ui import setup_page

role = setup_page("Home")

st.title("ClearBrand")
st.subheader("Check content against approved brand rules before it is published")

st.write(
    "ClearBrand reviews a draft against your approved guidelines, facts and terminology, "
    "explains each issue with its source, and leaves the final decision to people."
)

st.info(f"You are using ClearBrand as: **{role}**")

st.markdown(
    """
**How to use it**
1. **Manager:** open *Brand Setup* and add the guidelines, approved facts and glossary.
2. **Creator:** submit a draft for review and act on the findings.
3. **Reviewer:** comment, then approve or request changes.
"""
)