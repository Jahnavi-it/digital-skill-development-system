import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Railway (and other hosts) provide a single DATABASE_URL.
    # Locally, we build the URL from separate DB_* values in .env instead.
    _database_url = os.getenv("DATABASE_URL")

    if _database_url:
        # Railway gives "mysql://...", SQLAlchemy needs "mysql+pymysql://..."
        SQLALCHEMY_DATABASE_URI = _database_url.replace("mysql://", "mysql+pymysql://", 1)
    else:
        DB_USER = os.getenv("DB_USER", "root")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "3306")
        DB_NAME = os.getenv("DB_NAME", "dsds_db")
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  # 24 hours, fine for a student project