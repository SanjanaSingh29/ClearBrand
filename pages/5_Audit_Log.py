import pandas as pd
import streamlit as st
from core.ui import setup_page
from core import db

role = setup_page("Audit Log")
st.title("Audit Log")
st.write(
    "A record of who did what and when: sign-ins, drafts, revisions, review decisions, "
    "approvals, brand material changes and account changes."
)

if role not in ("Manager", "Reviewer"):
    st.warning("The audit log is available to the Manager and Reviewer roles.")
    st.stop()

rows = db.list_audit()
if not rows:
    st.info("No activity has been recorded yet.")
    st.stop()

df = pd.DataFrame(rows)
c1, c2 = st.columns(2)
pick_action = c1.selectbox("Action", ["All"] + sorted(df["action"].unique()))
pick_user = c2.selectbox("User", ["All"] + sorted(df["username"].unique()))

view = df
if pick_action != "All":
    view = view[view["action"] == pick_action]
if pick_user != "All":
    view = view[view["username"] == pick_user]

st.caption(f"Showing {len(view)} of {len(df)} events, newest first.")
st.dataframe(view[["at", "username", "role", "action", "target", "detail"]], hide_index=True)
st.download_button(
    "Download as CSV",
    view.to_csv(index=False).encode("utf-8"),
    "clearbrand_audit_log.csv",
    "text/csv",
)