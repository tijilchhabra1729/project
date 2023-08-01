from dotenv import load_dotenv
import os
from datetime import timedelta


load_dotenv()

class ApplicationConfig:
    SECRET_KEY = os.environ["SECRET_KEY"]

    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = r"sqlite:///./db.sqlite"

    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USER_SIGNER = True

    SESSION_COOKIE_SAMESITE = "Strict"

    JWT_SECRET_KEY = 'cdd869ed49591a0377cf7605f9b8005a'

    JWT_TOKEN_LOCATION = ['headers', 'query_string']

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
