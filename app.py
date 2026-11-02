import streamlit as st
from core.ui import setup_page, current_user

role = setup_page("Home")
user = current_user()

st.title("ClearBrand")
st.subheader("Check content against approved brand rules before it is published")

st.write(
    "ClearBrand reviews a draft against your approved guidelines, facts and terminology, "
    "explains each issue with its source, and leaves the final decision to people."
)

st.info(f"Signed in as **{user['display_name']}** ({user['username']}). Role: **{role}**")

GUIDE = {
    "Manager": "Open **Brand Setup** to manage guidelines, approved facts and the glossary. Use **Users** to create accounts, **Insights** for patterns, and **Audit Log** for the record of activity.",
    "Creator": "Open **Review Draft**, submit text or import a file, then accept or dismiss each finding, edit, and submit for review. You see only your own drafts.",
    "Reviewer": "Open **Review Queue** to read findings and revision history, comment, then approve or request changes. You cannot approve a draft you created yourself.",
}
st.markdown(GUIDE[role])