# db.py
import pymysql

pymysql.install_as_MySQLdb()

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy import and_
# from sqlalchemy.orm import joinedload

db = SQLAlchemy()


def set_db_errors():
    db_errors = SQLAlchemyError
    return db_errors


def set_session(app):
    sqlalchemy_database_uri = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(sqlalchemy_database_uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
