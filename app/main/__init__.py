# For main/__init__.py
from flask import Blueprint

main = Blueprint('main', __name__)

from . import routes

# Similar structure for auth, admin, scheduler, and logs modules
