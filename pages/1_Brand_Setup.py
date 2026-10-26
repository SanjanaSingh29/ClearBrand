import streamlit as st
from core.ui import setup_page
from core import db

role = setup_page("Brand Setup")
is_manager = role == "Manager"

st.title("Brand Setup")
st.write(
    "This is the approved material every draft is checked against. "
    "Each entry gets a code (R = guideline, F = approved fact, G = glossary) "
    "that findings cite as their source."
)
if not is_manager:
    st.warning("Only the Manager role can change brand material. You can view it here.")

SECTIONS = [
    ("guideline", "Guidelines", "Tone, voice and do/don't rules."),
    ("fact", "Approved facts", "Statements the organisation can prove, such as figures, dates and policies."),
    ("glossary", "Glossary", "Terms to avoid and the preferred term to use instead."),
]

tabs = st.tabs([label for _, label, _ in SECTIONS])

for tab, (kind, label, hint) in zip(tabs, SECTIONS):
    with tab:
        st.caption(hint)
        items = db.list_sources(kind)
        if not items:
            st.info(f"No {label.lower()} added yet.")
        for item in items:
            col_code, col_text, col_btn = st.columns([1, 8, 1])
            col_code.markdown(f"**{item['code']}**")
            if kind == "glossary" and "=>" in item["text"]:
                avoid, preferred = [p.strip() for p in item["text"].split("=>", 1)]
                col_text.write(f'Avoid "{avoid}", use "{preferred}"')
            else:
                col_text.write(item["text"])
            if is_manager and col_btn.button("Delete", key=f"del_{item['code']}"):
                db.delete_source(item["code"])
                st.rerun()

        if is_manager:
            st.divider()
            with st.form(f"add_{kind}", clear_on_submit=True):
                if kind == "glossary":
                    avoid = st.text_input("Term to avoid")
                    preferred = st.text_input("Preferred term")
                    submitted = st.form_submit_button("Add glossary entry")
                    if submitted:
                        if avoid.strip() and preferred.strip():
                            db.add_source(kind, f"{avoid.strip()} => {preferred.strip()}")
                            st.rerun()
                        else:
                            st.error("Fill in both fields.")
                else:
                    text = st.text_area(f"New {label.lower()[:-1] if label.endswith('s') else label.lower()}")
                    submitted = st.form_submit_button("Add")
                    if submitted:
                        if text.strip():
                            db.add_source(kind, text)
                            st.rerun()
                        else:
                            st.error("Write something first.")

            if kind != "glossary":
                uploaded = st.file_uploader(
                    f"Or import {label.lower()} from a .txt file (one per line)",
                    type=["txt"],
                    key=f"upload_{kind}",
                )
                if uploaded is not None and st.button("Import file", key=f"import_{kind}"):
                    lines = uploaded.getvalue().decode("utf-8").splitlines()
                    count = 0
                    for line in lines:
                        if line.strip():
                            db.add_source(kind, line)
                            count += 1
                    st.success(f"Imported {count} entries.")
                    st.rerun()