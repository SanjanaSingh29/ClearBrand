import difflib
import streamlit as st
from core.ui import setup_page
from core import db

role = setup_page("Review Queue")
st.title("Review Queue")

CAN_REVIEW = role in ("Reviewer", "Manager")
SEV_ICON = {"high": "🔴", "medium": "🟠", "low": "🔵"}

if not CAN_REVIEW:
    st.warning("Only the Reviewer and Manager roles can approve or request changes. You can view drafts here.")

tab_wait, tab_all = st.tabs(["Waiting for review", "All drafts"])

with tab_wait:
    waiting = db.list_drafts("In Review")
    if not waiting:
        st.info("No drafts are waiting for review.")
    for d in waiting:
        st.write(f"**#{d['id']} {d['title']}**  ({d['content_type']}, by {d['creator']})")

with tab_all:
    for d in db.list_drafts():
        st.write(f"#{d['id']}  {d['title']}  |  {d['status']}  |  updated {d['updated_at']}")

drafts = db.list_drafts()
if not drafts:
    st.stop()

st.divider()
labels = {d["id"]: f"#{d['id']}  {d['title']}  ({d['status']})" for d in drafts}
default = [d["id"] for d in drafts if d["status"] == "In Review"]
ids = list(labels.keys())
start = ids.index(default[0]) if default else 0
draft_id = st.selectbox("Open a draft", ids, index=start, format_func=lambda i: labels[i])

draft = db.get_draft(draft_id)
revisions = db.list_revisions(draft_id)
rev = revisions[-1]
findings = db.list_findings(draft_id, rev["id"])

st.caption(f"{draft['content_type']}  |  Version {rev['version']}  |  Status: {draft['status']}")

left, right = st.columns([3, 2])

with left:
    st.subheader("Draft text")
    st.write(rev["content"])

    if len(revisions) > 1:
        with st.expander("Revision history"):
            for i in range(1, len(revisions)):
                old, new = revisions[i - 1], revisions[i]
                st.markdown(f"**Version {old['version']} to {new['version']}**  ({new['created_at']})")
                diff = difflib.unified_diff(
                    old["content"].splitlines(), new["content"].splitlines(),
                    lineterm="", n=0,
                )
                lines = [l for l in diff if not l.startswith(("---", "+++", "@@"))]
                st.code("\n".join(lines) or "No line changes", language="diff")

    st.subheader("Comments")
    comments = db.list_comments(draft_id)
    if not comments:
        st.caption("No comments yet.")
    for c in comments:
        st.markdown(f"**{c['role']}** ({c['created_at']}): {c['body']}")

    with st.form(f"comment_{draft_id}", clear_on_submit=True):
        body = st.text_area("Add a comment")
        posted = st.form_submit_button("Post comment")
        if posted:
            if body.strip():
                db.add_comment(draft_id, role, role, body)
                st.rerun()
            else:
                st.error("Write a comment first.")

    if CAN_REVIEW and draft["status"] == "In Review":
        st.subheader("Decision")
        b1, b2 = st.columns(2)
        if b1.button("Approve", type="primary", key=f"approve_{draft_id}"):
            db.update_draft_status(draft_id, "Approved")
            db.add_comment(draft_id, role, role, "Approved.")
            st.rerun()
        if b2.button("Request changes", key=f"changes_{draft_id}"):
            has_comment = any(c["role"] in ("Reviewer", "Manager") for c in comments)
            if has_comment:
                db.update_draft_status(draft_id, "Changes Requested")
                st.rerun()
            else:
                st.error("Post a comment explaining the changes first.")
    elif draft["status"] == "Approved":
        st.success("This draft is approved.")

with right:
    st.subheader(f"How findings were handled ({len(findings)})")
    if not findings:
        st.success("No issues were found by the checks.")
    for f in findings:
        with st.container(border=True):
            st.markdown(f"{SEV_ICON.get(f['severity'], '⚪')} **{f['category']}**  \n`{f['flagged_text']}`")
            st.write(f["reason"])
            if f["source_code"]:
                src = db.get_source(f["source_code"])
                if src:
                    st.caption(f"Source {src['code']}: {src['text']}")
            else:
                st.caption("No approved source found: unverified.")
            status = f["status"]
            if status == "dismissed":
                st.warning(f"Dismissed by the creator. Reason: {f['dismiss_reason']}")
            elif status == "accepted":
                st.success("Accepted by the creator.")
            else:
                st.info("Still open.")