# db.py
import pymysql

pymysql.install_as_MySQLdb()

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


db = SQLAlchemy()


def set_db_errors():
    db_errors = SQLAlchemyError
    return db_errors


# def create_session(app):
#     # with app.app_context():  # Push an application context
#     sqlalchemy_database_uri = app.config['SQLALCHEMY_DATABASE_URI']
#     engine = create_engine(sqlalchemy_database_uri)
#     Session = scoped_session(sessionmaker(bind=engine))
#     # Session = scoped_session(sessionmaker(bind=app.db.engine))
#     # Session = sessionmaker(bind=engine)
#     return Session

