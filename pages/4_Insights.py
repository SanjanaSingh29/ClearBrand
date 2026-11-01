import pandas as pd
import streamlit as st
from core.ui import setup_page
from core import db

role = setup_page("Insights")
st.title("Governance Insights")
st.write(
    "Patterns across reviewed drafts: which mistakes repeat, and which rules creators "
    "often dismiss. Rules that are dismissed a lot may be unclear or too strict."
)

if role not in ("Manager", "Reviewer"):
    st.warning("Insights are available to the Manager and Reviewer roles.")
    st.stop()

rows = db.list_all_findings()
if not rows:
    st.info("No findings yet. Submit and review some drafts, then come back.")
    st.stop()

df = pd.DataFrame(rows)
drafts = db.list_drafts()
sources = {s["code"]: s["text"] for s in db.list_sources()}

handled = df[df["status"].isin(["accepted", "dismissed"])]
dismissed = df[df["status"] == "dismissed"]
first = df[df["version"] == 1]

# ---------- Headline numbers ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Drafts", len(drafts))
c2.metric("Findings", len(df))
c3.metric(
    "Dismissal rate",
    f"{len(dismissed) / len(handled) * 100:.0f}%" if len(handled) else "n/a",
)
c4.metric("Unverified claims", int((df["category"] == "Unverified claim").sum()))

st.caption(
    "Mistakes below are counted from each draft's first version, so re-checking a draft "
    "does not count the same mistake twice."
)

# ---------- Repeated mistakes ----------
left, right = st.columns(2)
with left:
    st.subheader("Findings by category")
    st.bar_chart(first["category"].value_counts())
with right:
    st.subheader("Rule-based vs AI-assisted")
    st.bar_chart(first["origin"].map({"rule": "Rule-based", "ai": "AI-assisted"}).value_counts())

left, right = st.columns(2)
with left:
    st.subheader("Most repeated flagged phrases")
    phrases = first["flagged_text"].str.lower().value_counts().head(10)
    st.dataframe(phrases.rename("times flagged"))
with right:
    st.subheader("Most cited sources")
    cited = first["source_code"].fillna("No source (unverified)").value_counts().head(10)
    st.dataframe(cited.rename("times cited"))

# ---------- Unclear rules ----------
st.subheader("Rules creators dismiss most")
if handled.empty:
    st.info("No findings have been accepted or dismissed yet.")
else:
    h = handled.copy()
    h["code"] = h["source_code"].fillna("No source")
    g = (
        h.groupby("code")
        .agg(handled=("id", "count"), dismissed=("status", lambda s: int((s == "dismissed").sum())))
        .reset_index()
    )
    g["dismissal_rate_%"] = (g["dismissed"] / g["handled"] * 100).round(0)
    g["rule_text"] = g["code"].map(lambda c: sources.get(c, "-"))
    g["signal"] = g.apply(
        lambda r: "May be unclear or too strict" if r["handled"] >= 2 and r["dismissal_rate_%"] >= 50 else "",
        axis=1,
    )
    g = g.sort_values(["dismissal_rate_%", "handled"], ascending=False)
    st.dataframe(
        g[["code", "rule_text", "handled", "dismissed", "dismissal_rate_%", "signal"]],
        hide_index=True,
    )
    st.caption("A signal needs at least 2 handled findings and a dismissal rate of 50% or more.")

# ---------- Dismissal reasons ----------
st.subheader("Why creators dismissed findings")
reasons = dismissed["dismiss_reason"].dropna()
if reasons.empty:
    st.info("No dismissal reasons recorded yet.")
else:
    st.dataframe(reasons.value_counts().head(10).rename("times given"))

# ---------- Draft status ----------
st.subheader("Drafts by status")
st.bar_chart(pd.Series([d["status"] for d in drafts]).value_counts())