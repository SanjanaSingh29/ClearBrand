import streamlit as st

CSS = """
<style>
@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.stApp {
  background: linear-gradient(135deg, #0b1020, #101a3a, #0b2a3a, #1a1040);
  background-size: 300% 300%;
  animation: gradientShift 24s ease infinite;
}

.block-container { animation: fadeUp .6s ease both; }

h1 {
  background: linear-gradient(90deg, #22d3ee, #6366f1, #a855f7);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
h2, h3 { color: #e8eefc; }

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0f172a 0%, #12204a 100%);
  border-right: 1px solid rgba(34, 211, 238, .25);
}

a[data-testid="stPageLink-NavLink"] {
  border-radius: 999px;
  padding: .35rem .9rem;
  background: rgba(99, 102, 241, .12);
  border: 1px solid rgba(99, 102, 241, .35);
  transition: background .3s ease, transform .2s ease, box-shadow .3s ease;
}
a[data-testid="stPageLink-NavLink"]:hover {
  background: linear-gradient(90deg, rgba(34,211,238,.35), rgba(168,85,247,.35));
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(34, 211, 238, .25);
}

.stButton > button, .stFormSubmitButton > button {
  border-radius: 10px;
  border: 1px solid rgba(34, 211, 238, .5);
  background: rgba(34, 211, 238, .08);
  transition: transform .2s ease, box-shadow .3s ease, background .3s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
  background: linear-gradient(90deg, #22d3ee, #6366f1);
  color: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, .4);
}
button[kind="primary"] {
  background: linear-gradient(90deg, #22d3ee, #6366f1, #a855f7);
  background-size: 200% 200%;
  border: none;
  color: #ffffff;
  transition: background-position .6s ease, transform .2s ease, box-shadow .3s ease;
}
button[kind="primary"]:hover {
  background-position: 100% 0;
  transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(168, 85, 247, .45);
}

[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: 14px;
  background: rgba(255, 255, 255, .03);
  transition: transform .25s ease, box-shadow .3s ease, border-color .3s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  transform: translateY(-3px);
  border-color: rgba(34, 211, 238, .6);
  box-shadow: 0 10px 26px rgba(0, 0, 0, .35);
}

button[data-baseweb="tab"] { transition: color .3s ease, background .3s ease; }
button[data-baseweb="tab"][aria-selected="true"] { color: #22d3ee; }

textarea, input { transition: box-shadow .3s ease, border-color .3s ease; }
textarea:focus, input:focus { box-shadow: 0 0 0 2px rgba(34, 211, 238, .45) !important; }

[data-testid="stAlert"] { border-radius: 12px; }
[data-testid="stExpander"] { border-radius: 12px; }

@media (prefers-reduced-motion: reduce) {
  .stApp, .block-container, * { animation: none !important; transition: none !important; }
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)