"""Authentication helpers — MongoDB + bcrypt.

Provides:
    create_user(name, email, password) -> dict
    authenticate_user(email, password) -> dict | None
"""

import bcrypt
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from config import settings

# ── MongoDB connection ────────────────────────────────────
_client = MongoClient(settings.mongo_uri)
_db = _client["planit"]
_users = _db["users"]

# Ensure unique index on email (idempotent — safe to call every startup)
_users.create_index("email", unique=True)


def create_user(name: str, email: str, password: str) -> dict:
    """Hash the password, insert into MongoDB, and return the user dict.

    Raises ValueError if the email already exists.
    """
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        _users.insert_one({
            "name": name,
            "email": email,
            "password": hashed,
        })
    except DuplicateKeyError:
        raise ValueError("An account with this email already exists.")

    return {"name": name, "email": email}


def authenticate_user(email: str, password: str) -> dict | None:
    """Return the user dict if credentials are valid, else None."""
    user = _users.find_one({"email": email})
    if not user:
        return None

    if bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return {"name": user["name"], "email": user["email"]}

    return None
