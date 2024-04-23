# db.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

db = SQLAlchemy()
db_errors = SQLAlchemyError
