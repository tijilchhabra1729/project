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

    JWT_SECRET_KEY = 'mysecret'

    JWT_TOKEN_LOCATION = ['headers', 'query_string']

    ACCESS_EXPIRES = timedelta(hours=12)
