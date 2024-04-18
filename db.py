# db.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

db = SQLAlchemy()
db_errors = SQLAlchemyError
