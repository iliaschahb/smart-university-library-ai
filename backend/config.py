import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-key")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'library.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sessions / Cookies
    PERMANENT_SESSION_LIFETIME_HOURS = int(
        os.environ.get("PERMANENT_SESSION_LIFETIME_HOURS", "8")
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "None")
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "true").lower() == "true"

    # Demo accounts
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-me")

    LIBRARIAN_USERNAME = os.environ.get("LIBRARIAN_USERNAME", "biblio")
    LIBRARIAN_PASSWORD = os.environ.get("LIBRARIAN_PASSWORD", "change-me")
