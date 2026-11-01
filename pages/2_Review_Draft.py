import re
import streamlit as st
from core.ui import setup_page
from core import db
from core.review import run_checks
from core.importers import extract_text, MAX_CHARS, MAX_FILE_MB

role = setup_page("Review Draft")
st.title("Review Draft")

if not db.list_sources():
    st.warning("No brand material has been added yet, so drafts cannot be checked fully. A Manager needs to add guidelines, approved facts and a glossary on the Brand Setup page first.")

CONTENT_TYPES = ["Social post", "Blog draft", "Press release", "Email copy", "Other"]
SEV_ICON = {"high": "🔴", "medium": "🟠", "low": "🔵"}
CAN_CREATE = role in ("Creator", "Reviewer")


def run_and_save(draft_id, revision_id, text):
    findings, notice = run_checks(text)
    db.save_findings(draft_id, revision_id, findings)
    st.session_state.ai_notice = notice
    st.session_state.check_info = (
        f"Checked against {len(db.list_sources())} approved entries: "
        f"{sum(1 for f in findings if f['origin'] == 'rule')} rule-based and "
        f"{sum(1 for f in findings if f['origin'] == 'ai')} AI-assisted findings."
    )


def highlight(text, findings):
    spans = []
    for f in findings:
        if f["status"] != "open" or not f["flagged_text"]:
            continue
        pattern = r"(?<!\w)" + re.escape(f["flagged_text"]) + r"(?!\w)"
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            spans.append([m.start(), m.end()])
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    out, last = [], 0
    for s, e in merged:
        out.append(text[last:s])
        out.append(f":red-background[{text[s:e]}]")
        last = e
    out.append(text[last:])
    return "".join(out).replace("\n", "  \n")


def compliance_score(findings):
    weights = {"high": 15, "medium": 8, "low": 3}
    penalty = sum(weights.get(f["severity"], 5) for f in findings if f["status"] != "dismissed")
    return max(0, 100 - penalty)


# ---------- New draft ----------
n = st.session_state.get("form_n", 0)
k_title, k_text, k_file, k_img, k_alt, k_type = (
    f"new_title_{n}", f"new_text_{n}", f"new_file_{n}", f"new_img_{n}", f"new_alt_{n}", f"new_type_{n}"
)

if CAN_CREATE:
    with st.expander("Submit a new draft", expanded=("draft_id" not in st.session_state)):
        st.caption(f"Type text, or import a .docx, .pdf or .txt file (up to {MAX_FILE_MB} MB).")
        uploaded = st.file_uploader("Import a file (optional)", type=["docx", "pdf", "txt"], key=k_file)
        if uploaded is not None and st.session_state.get(f"imported_{n}") != (uploaded.name, uploaded.size):
            if uploaded.size > MAX_FILE_MB * 1024 * 1024:
                st.error(f"That file is larger than {MAX_FILE_MB} MB.")
            else:
                try:
                    imported_text, notes = extract_text(uploaded)
                except Exception:
                    st.error("Could not read that file. Check that it is a valid .docx, .pdf or .txt file with selectable text.")
                else:
                    if not imported_text.strip():
                        st.warning("No readable text was found. A scanned PDF has no text layer.")
                    st.session_state[k_text] = imported_text
                    st.session_state[k_title] = uploaded.name.rsplit(".", 1)[0]
                    st.session_state[f"notes_{n}"] = notes
                    st.session_state[f"imported_{n}"] = (uploaded.name, uploaded.size)
        for note in st.session_state.get(f"notes_{n}", []):
            st.info(note)

        title = st.text_input("Title", key=k_title)
        ctype = st.selectbox("Content type", CONTENT_TYPES, key=k_type)
        content = st.text_area("Draft text", height=200, key=k_text)

        image = st.file_uploader("Attach an image (optional)", type=["png", "jpg", "jpeg"], key=k_img)
        alt = ""
        if image is not None:
            st.image(image, width=220)
            alt = st.text_input("Alt text: describe the image for people who cannot see it", key=k_alt)

        if st.button("Save and run check", key=f"save_new_{n}"):
            body = content.strip()
            if image is not None:
                body += ("\n\n" if body else "") + f"Image alt text (image 1): {alt.strip() or 'MISSING'}"
            if not title.strip() or not body:
                st.error("Add a title and some text.")
            elif len(body) > MAX_CHARS:
                st.error(f"The text is longer than {MAX_CHARS:,} characters. Shorten it or split it into two drafts.")
            else:
                new_id = db.create_draft(title.strip(), ctype, role, body)
                first = db.latest_revision(new_id)
                run_and_save(new_id, first["id"], first["content"])
                st.session_state.draft_id = new_id
                st.session_state.form_n = n + 1
                st.rerun()
else:
    st.info("Only the Creator and Reviewer roles can submit or edit drafts. Managers can view drafts and manage brand material.")

# ---------- Pick a draft ----------
drafts = db.list_drafts()
if not drafts:
    st.info("No drafts yet. A Creator can submit one above.")
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
if st.session_state.get("check_info"):
    st.caption(st.session_state.check_info)

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
                elif not new_text.strip():
                    st.error("The draft cannot be empty.")
                elif len(new_text) > MAX_CHARS:
                    st.error(f"The text is longer than {MAX_CHARS:,} characters.")
                else:
                    new_rev = db.add_revision(draft_id, new_text.strip(), note="Edited after check")
                    run_and_save(draft_id, new_rev, new_text.strip())
                    st.rerun()

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
    st.metric("Compliance score", f"{compliance_score(findings)} / 100")
    st.caption("Starts at 100. Each unresolved finding subtracts points: high 15, medium 8, low 3. Dismissed findings do not count.")
    if not findings:
        st.success("No issues found by the checks.")
    for f in findings:
        with st.container(border=True):
            st.markdown(
                f"{SEV_ICON.get(f['severity'], '⚪')} **{f['category']}** ({f['severity']})  \n`{f['flagged_text']}`"
            )
            st.write(f["reason"])
            if f["origin"] == "ai":
                checked_by = "AI-assisted"
            elif f["category"] == "Accessibility":
                checked_by = "Accessibility check"
            else:
                checked_by = "Rule-based"
            st.caption("Checked by: " + checked_by)
            if f["category"] == "Accessibility":
                st.caption("Built-in accessibility rule (not from your brand material).")
            elif f["source_code"]:
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