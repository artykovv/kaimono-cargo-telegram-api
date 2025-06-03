import os
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

class Base(DeclarativeBase):
    pass



DB_HOST = os.environ.get("POSTGRESQL_HOST")
DB_PORT = os.environ.get("POSTGRESQL_PORT")
DB_NAME = os.environ.get("POSTGRESQL_DBNAME")
DB_USER = os.environ.get("POSTGRESQL_USER")
DB_PASS = os.environ.get("POSTGRESQL_PASSWORD")

API_KEYS = {
    os.getenv("API_KEY_1"): "Key1",
    os.getenv("API_KEY_2"): "Key2",
}