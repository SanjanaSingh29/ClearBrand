import hashlib
import hmac
import os
import re

from core import db

ITERATIONS = 200_000
USERNAME_RE = re.compile(r"^[a-z0-9_]{3,30}$")
ROLES = ["Creator", "Reviewer", "Manager"]

# Public demo accounts so judges can try every role. Demo only.
DEMO_ACCOUNTS = [
    ("creator_demo", "Demo Creator", "Creator", "Creator#2026"),
    ("reviewer_demo", "Demo Reviewer", "Reviewer", "Reviewer#2026"),
    ("reviewer2_demo", "Second Reviewer", "Reviewer", "Reviewer2#2026"),
    ("manager_demo", "Demo Manager", "Manager", "Manager#2026"),
]


def hash_password(password, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return salt.hex(), digest.hex()


def verify_password(password, salt_hex, hash_hex):
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), ITERATIONS)
    return hmac.compare_digest(digest.hex(), hash_hex)


def create_user(username, display_name, role, password):
    username = (username or "").strip().lower()
    display_name = (display_name or "").strip()
    if not USERNAME_RE.match(username):
        return False, "Username must be 3 to 30 characters: lowercase letters, numbers or underscore."
    if not display_name:
        return False, "Enter a display name."
    if role not in ROLES:
        return False, "Choose a valid role."
    if len(password or "") < 8:
        return False, "The password must be at least 8 characters."
    if db.get_user(username):
        return False, "That username is already taken."
    salt, digest = hash_password(password)
    db.add_user(username, display_name, role, salt, digest)
    return True, "Account created."


def authenticate(username, password):
    user = db.get_user((username or "").strip().lower())
    if not user:
        hash_password(password or "")  # similar timing whether or not the user exists
        return None
    if verify_password(password or "", user["salt"], user["password_hash"]):
        return {"username": user["username"], "display_name": user["display_name"], "role": user["role"]}
    return None


def seed_demo_users():
    if db.list_users():
        return
    for username, name, role, password in DEMO_ACCOUNTS:
        create_user(username, name, role, password)