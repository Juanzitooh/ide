import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    MISSIONS_FILE = Path(
        os.getenv("MISSIONS_FILE", BASE_DIR / "instance" / "missions.json")
    )
    FEEDBACK_FILE = Path(
        os.getenv("FEEDBACK_FILE", BASE_DIR / "instance" / "feedback.json")
    )
    APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
    DATA_BACKEND = os.getenv("DATA_BACKEND", "mysql")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_TTL_MISSION = int(os.getenv("REDIS_TTL_MISSION", "600"))
    REDIS_TTL_LIST = int(os.getenv("REDIS_TTL_LIST", "120"))
