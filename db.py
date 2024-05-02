# db.py
import pymysql
pymysql.install_as_MySQLdb()

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

db = SQLAlchemy()
db_errors = SQLAlchemyError

sqlalchemy_database_uri = os.getenv('SQLALCHEMY_DATABASE_URI')

engine = create_engine(sqlalchemy_database_uri)
Session = sessionmaker(bind=engine)
session = Session()
