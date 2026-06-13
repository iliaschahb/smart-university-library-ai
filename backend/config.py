import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Base SQLite pour le développement
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///smart_library.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pour les prochaines étapes
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017/smart_library_logs"
    )

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
