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
