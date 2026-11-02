import streamlit as st
from core.ui import setup_page, current_user
from core import db, auth

role = setup_page("Users")
me = current_user()["username"]
st.title("Users")
st.write("Each account has one fixed role. Only a Manager can create accounts.")

if role != "Manager":
    st.warning("Only the Manager role can manage accounts.")
    st.stop()

st.subheader("Create an account")
with st.form("new_user", clear_on_submit=True):
    username = st.text_input("Username (lowercase letters, numbers, underscore)")
    display = st.text_input("Display name")
    new_role = st.selectbox("Role", auth.ROLES)
    password = st.text_input("Password (at least 8 characters)", type="password")
    confirm = st.text_input("Repeat the password", type="password")
    submitted = st.form_submit_button("Create account")

if submitted:
    if password != confirm:
        st.error("The two passwords do not match.")
    else:
        ok, message = auth.create_user(username, display, new_role, password)
        if ok:
            db.log_event(me, role, "user_created", username.strip().lower(), f"role: {new_role}")
            st.success(message)
        else:
            st.error(message)

st.subheader("Existing accounts")
st.dataframe(
    [{"Username": u["username"], "Name": u["display_name"], "Role": u["role"], "Created": u["created_at"]}
     for u in db.list_users()],
    hide_index=True,
)
st.caption("Passwords are stored only as salted PBKDF2 hashes. They cannot be read back.")