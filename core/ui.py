import os
import streamlit as st
from core import db, auth
from core.seed import seed_if_empty
from core.style import inject_css

DEMO_USERNAMES = {u for u, _, _, _ in auth.DEMO_ACCOUNTS}


@st.cache_resource
def _bootstrap():
    """Runs once per server start, not on every page load."""
    db.init_db()
    db.init_auth_tables()
    auth.seed_demo_users()
    seed_if_empty()
    return True


def current_user():
    return st.session_state.get("user")


def top_nav():
    cols = st.columns(7)
    cols[0].page_link("app.py", label="Home")
    cols[1].page_link("pages/1_Brand_Setup.py", label="Brand Setup")
    cols[2].page_link("pages/2_Review_Draft.py", label="Review Draft")
    cols[3].page_link("pages/3_Review_Queue.py", label="Review Queue")
    cols[4].page_link("pages/4_Insights.py", label="Insights")
    cols[5].page_link("pages/5_Audit_Log.py", label="Audit Log")
    cols[6].page_link("pages/6_Users.py", label="Users")
    st.divider()


def _login_view():
    st.title("Sign in to ClearBrand")
    st.write("Each account has one fixed role, set by a Manager. Sign in to continue.")

    if st.session_state.get("failed_logins", 0) >= 5:
        st.error("Too many failed attempts in this session. Reload the page to try again.")
    else:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            go = st.form_submit_button("Sign in")
        if go:
            user = auth.authenticate(username, password)
            if user:
                st.session_state.user = user
                st.session_state.failed_logins = 0
                db.log_event(user["username"], user["role"], "login")
                st.rerun()
            else:
                st.session_state.failed_logins = st.session_state.get("failed_logins", 0) + 1
                db.log_event((username or "-").strip().lower()[:30] or "-", "-", "login_failed")
                st.error("Wrong username or password.")

    with st.expander("Demo accounts for judges (public, demo only)", expanded=True):
        st.table([
            {"Username": u, "Password": p, "Role": r}
            for u, _, r, p in auth.DEMO_ACCOUNTS
        ])
        st.caption(
            "These accounts are public so anyone can try each role. Do not reuse a real password "
            "here, and do not enter confidential material."
        )


def _sign_out(user):
    db.log_event(user["username"], user["role"], "logout")
    st.session_state.pop("user", None)
    st.session_state.pop("draft_id", None)


def _account_section(user):
    if user["username"] in DEMO_USERNAMES:
        st.caption("Demo accounts are shared and cannot be deleted.")
        return
    with st.expander("Delete my account"):
        st.caption(
            "This permanently removes your account so you can no longer sign in. "
            "Drafts, comments and audit entries you created are kept and still show your username."
        )
        password = st.text_input("Confirm with your password", type="password", key="delete_pw")
        if st.button("Delete my account permanently", key="delete_account"):
            if auth.authenticate(user["username"], password):
                db.log_event(user["username"], user["role"], "account_deleted")
                db.delete_user(user["username"])
                st.session_state.pop("user", None)
                st.session_state.pop("draft_id", None)
                st.rerun()
            else:
                st.error("Wrong password. Nothing was deleted.")

def _guest_sidebar():
    with st.sidebar:
        st.markdown("### ClearBrand")
        st.caption("Check content against approved brand rules before it is published.")
        st.markdown("**Try it now**")
        st.caption("Sign in with a demo account in one click:")
        for username, name, role, password in auth.DEMO_ACCOUNTS:
            if st.button(f"{role}: {name}", key=f"quick_{username}"):
                user = auth.authenticate(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.failed_logins = 0
                    db.log_event(user["username"], user["role"], "login", "", "one-click demo sign-in")
                    st.rerun()
        st.caption("Demo accounts are public. Use only non-confidential text.")
def setup_page(page_title, require_login=True):
    st.set_page_config(
        page_title=f"{page_title} | ClearBrand",
        page_icon="assets/logo.png",
        layout="wide",
    )
    _bootstrap()
    inject_css()
    st.markdown(
        "<style>[data-testid='stSidebarNav'] { display: none; }</style>",
        unsafe_allow_html=True,
    )

    if os.path.exists("assets/logo.png"):
        st.logo("assets/logo.png", size="large")

    top_nav()

    user = current_user()
    if user is None:
        if require_login:
            _login_view()
            st.stop()
        return None

    with st.sidebar:
        st.write(f"Signed in as **{user['display_name']}**")
        st.caption(f"Username: {user['username']}  |  Role: {user['role']}")
        if st.button("Sign out", key="sign_out"):
            _sign_out(user)
            st.rerun()
        _account_section(user)
        user = current_user()
        if user is None:
            if require_login:
                _guest_sidebar()
                _login_view()
                st.stop()
            return None

    return user["role"]