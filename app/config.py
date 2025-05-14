import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    ODDS_API_KEY = os.getenv("ODDS_API_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///../instance/data.db"  # Example DB URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking
