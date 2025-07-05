import os
from dotenv import load_dotenv

# Wajib load .env
load_dotenv()

print("DATABASE_URI from .env:", os.getenv("DATABASE_URI"))


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
