import re
import streamlit as st
from core.ui import setup_page
from core import db
from core.review import run_checks

role = setup_page("Review Draft")
st.title("Review Draft")

CONTENT_TYPES = ["Social post", "Blog draft", "Press release", "Email copy", "Other"]
SEV_ICON = {"high": "🔴", "medium": "🟠", "low": "🔵"}
CAN_CREATE = role in ("Creator", "Reviewer")

def run_and_save(draft_id, revision_id, text):
    findings, notice = run_checks(text)
    db.save_findings(draft_id, revision_id, findings)
    st.session_state.ai_notice = notice

def highlight(text, findings):
    out = text
    terms = {f["flagged_text"] for f in findings if f["status"] == "open"}
    for term in sorted(terms, key=len, reverse=True):
        pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
        out = re.sub(pattern, lambda m: f":red-background[{m.group(0)}]", out, flags=re.IGNORECASE)
    return out


# ---------- New draft ----------
if CAN_CREATE:
    with st.expander("Submit a new draft", expanded=("draft_id" not in st.session_state)):
        with st.form("new_draft", clear_on_submit=True):
            title = st.text_input("Title")
            ctype = st.selectbox("Content type", CONTENT_TYPES)
            content = st.text_area("Draft text", height=200)
            go = st.form_submit_button("Save and run check")
        if go:
            if not title.strip() or not content.strip():
                st.error("Add a title and some text.")
            else:
                new_id = db.create_draft(title.strip(), ctype, role, content.strip())
                first = db.latest_revision(new_id)
                run_and_save(new_id, first["id"], first["content"])
                st.session_state.draft_id = new_id
                st.rerun()

        else:
            st.info("Only the Creator and Reviewer roles can submit or edit drafts. Managers can view drafts and manage brand material.")

# ---------- Pick a draft ----------
drafts = db.list_drafts()
if not drafts:
    st.info("No drafts yet. A Creator/Reviewer can submit one above.")
    st.stop()

labels = {d["id"]: f"#{d['id']}  {d['title']}  ({d['status']})" for d in drafts}
ids = list(labels.keys())
current = st.session_state.get("draft_id", ids[0])
if current not in ids:
    current = ids[0]
draft_id = st.selectbox("Open a draft", ids, index=ids.index(current), format_func=lambda i: labels[i])
st.session_state.draft_id = draft_id

draft = db.get_draft(draft_id)
rev = db.latest_revision(draft_id)
findings = db.list_findings(draft_id, rev["id"])
open_count = sum(1 for f in findings if f["status"] == "open")
can_edit = CAN_CREATE and draft["status"] in ("Draft", "Changes Requested")

st.caption(f"{draft['content_type']}  |  Version {rev['version']}  |  Status: {draft['status']}")

if st.session_state.get("ai_notice"):
    st.warning(st.session_state.ai_notice)

left, right = st.columns([3, 2])

# ---------- Draft text ----------
with left:
    st.subheader("Draft")
    st.markdown(highlight(rev["content"], findings))

    if can_edit:
        with st.expander("Edit this draft"):
            new_text = st.text_area(
                "Text", value=rev["content"], height=200,
                key=f"edit_{draft_id}_{rev['version']}",
            )
            if st.button("Save as new version and re-check", key=f"save_{draft_id}"):
                if new_text.strip() == rev["content"].strip():
                    st.warning("No changes to save.")
                else:
                    new_rev = db.add_revision(draft_id, new_text.strip(), note="Edited after check")
                    run_and_save(draft_id, new_rev, new_text.strip())
                    st.rerun()

    if can_edit:
        if open_count:
            st.warning(f"{open_count} finding(s) still open. Accept or dismiss each one before submitting.")
        if st.button("Submit for review", disabled=open_count > 0, key=f"submit_{draft_id}"):
            db.update_draft_status(draft_id, "In Review")
            st.rerun()

    comments = db.list_comments(draft_id)
    if comments:
        st.subheader("Comments")
        for c in comments:
            st.markdown(f"**{c['role']}** ({c['created_at']}): {c['body']}")

# ---------- Findings ----------
with right:
    st.subheader(f"Findings ({len(findings)})")
    if not findings:
        st.success("No issues found by the checks.")
    for f in findings:
        with st.container(border=True):
            st.markdown(
                f"{SEV_ICON.get(f['severity'], '⚪')} **{f['category']}** ({f['severity']})  \n`{f['flagged_text']}`"
            )
            st.write(f["reason"])
            st.caption("Checked by: " + ("AI-assisted" if f["origin"] == "ai" else "Rule-based"))
            if f["source_code"]:
                src = db.get_source(f["source_code"])
                if src:
                    st.caption(f"Source {src['code']}: {src['text']}")
            else:
                st.caption("No approved source found, so this is marked unverified.")
            if f["suggestion"]:
                st.caption(f"Suggestion: {f['suggestion']}")

            if f["status"] == "open" and can_edit:
                c1, c2 = st.columns(2)
                if c1.button("Accept", key=f"acc_{f['id']}"):
                    db.update_finding_status(f["id"], "accepted")
                    st.rerun()
                why = st.text_input("Reason to dismiss", key=f"why_{f['id']}")
                if c2.button("Dismiss", key=f"dis_{f['id']}"):
                    if why.strip():
                        db.update_finding_status(f["id"], "dismissed", why.strip())
                        st.rerun()
                    else:
                        st.error("Give a short reason to dismiss.")
            elif f["status"] != "open":
                note = f" ({f['dismiss_reason']})" if f["dismiss_reason"] else ""
                st.caption(f"Status: {f['status']}{note}")