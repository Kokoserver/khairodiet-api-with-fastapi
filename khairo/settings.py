import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path="./env")
DEBUG = os.getenv("DEBUG")
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_KEY = os.getenv("REFRESH_KEY")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
DATABASE_URI = os.getenv("DATABASE_URL")
ACCESS_TOKEN_EXPIRE_TIME = os.getenv("ACCESS_TOKEN_EXPIRE_TIME")
REFRESH_TOKEN_EXPIRE_TIME = os.getenv("REFRESH_TOKEN_EXPIRE_TIME")
# url in localhost        url in production
WEBSITE_URL = "http://127.0.0.1:8000"  # "https://khairodiet.herokuapp.com"
WEBSITE_NAME = "khairo"
API_BASE_URI = "/api/v1"
BASE_DIR = Path.cwd()
STATIC_DIR = Path.cwd() / "khairo/backend/static"
STATIC_FILE_NAME = "static"
