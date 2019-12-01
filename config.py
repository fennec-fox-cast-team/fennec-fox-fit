import os

POSTGRES_URL = os.environ.get("POSTGRES_URL")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PW = os.environ.get("POSTGRES_PW")
POSTGRES_DB = os.environ.get("POSTGRES_DB")

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fennec-fox-fit'
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

