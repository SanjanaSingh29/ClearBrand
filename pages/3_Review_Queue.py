import difflib
import streamlit as st
from core.ui import setup_page, current_user
from core import db

role = setup_page("Review Queue")
me = current_user()["username"]
st.title("Review Queue")

CAN_REVIEW = role in ("Reviewer", "Manager")
SEV_ICON = {"high": "🔴", "medium": "🟠", "low": "🔵"}

all_drafts = db.list_drafts()
drafts = all_drafts if role != "Creator" else [d for d in all_drafts if d["creator"] == me]

if not CAN_REVIEW:
    st.warning("Only the Reviewer and Manager roles can approve or request changes. You can view your own drafts here.")

tab_wait, tab_all = st.tabs(["Waiting for review", "All drafts"])

with tab_wait:
    waiting = [d for d in drafts if d["status"] == "In Review"]
    if not waiting:
        st.info("No drafts are waiting for review.")
    for d in waiting:
        st.write(f"**#{d['id']} {d['title']}**  ({d['content_type']}, by {d['creator']})")

with tab_all:
    for d in drafts:
        st.write(f"#{d['id']}  {d['title']}  |  {d['status']}  |  by {d['creator']}  |  updated {d['updated_at']}")

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
comments = db.list_comments(draft_id)
is_own = draft["creator"] == me

st.caption(f"{draft['content_type']}  |  Version {rev['version']}  |  Status: {draft['status']}  |  Created by {draft['creator']}")


def decide(new_status):
    fresh = db.get_draft(draft_id)
    if fresh["creator"] == me:
        db.log_event(me, role, "decision_blocked", f"draft #{draft_id}", "self-approval attempt")
        st.error("You cannot decide on a draft you created.")
        return
    if fresh["status"] != "In Review":
        st.error("This draft is no longer waiting for review.")
        return
    if new_status == "Changes Requested":
        fresh_comments = db.list_comments(draft_id)
        if not any(c["role"] in ("Reviewer", "Manager") for c in fresh_comments):
            st.error("Post a comment explaining the changes first.")
            return
        db.update_draft_status(draft_id, "Changes Requested")
        db.log_event(me, role, "changes_requested", f"draft #{draft_id}", f"version {rev['version']}")
    else:
        db.update_draft_status(draft_id, "Approved")
        db.add_comment(draft_id, me, role, "Approved.")
        db.log_event(me, role, "draft_approved", f"draft #{draft_id}", f"version {rev['version']}")
    st.rerun()


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
    if not comments:
        st.caption("No comments yet.")
    for c in comments:
        st.markdown(f"**{c['author']} ({c['role']})** ({c['created_at']}): {c['body']}")

    with st.form(f"comment_{draft_id}", clear_on_submit=True):
        body = st.text_area("Add a comment")
        posted = st.form_submit_button("Post comment")
        if posted:
            if body.strip():
                db.add_comment(draft_id, me, role, body)
                db.log_event(me, role, "comment_posted", f"draft #{draft_id}", body.strip()[:80])
                st.rerun()
            else:
                st.error("Write a comment first.")

    if draft["status"] == "In Review":
        st.subheader("Decision")
        if not CAN_REVIEW:
            st.info("Only a Reviewer or Manager can decide on this draft.")
        elif is_own:
            st.info("You created this draft, so you cannot approve it or request changes. Another reviewer must decide.")
        else:
            b1, b2 = st.columns(2)
            if b1.button("Approve", type="primary", key=f"approve_{draft_id}"):
                decide("Approved")
            if b2.button("Request changes", key=f"changes_{draft_id}"):
                decide("Changes Requested")
    elif draft["status"] == "Approved":
        st.success("This draft is approved.")
source_map = {s["code"]: s for s in db.list_sources()}
with right:
    st.subheader(f"How findings were handled ({len(findings)})")
    if not findings:
        st.success("No issues were found by the checks.")
    for f in findings:
        with st.container(border=True):
            st.markdown(f"{SEV_ICON.get(f['severity'], '⚪')} **{f['category']}**  \n`{f['flagged_text']}`")
            st.write(f["reason"])
            if f["category"] == "Accessibility":
                st.caption("Built-in accessibility rule.")
            elif f["source_code"]:
                src = source_map.get(f["source_code"])
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