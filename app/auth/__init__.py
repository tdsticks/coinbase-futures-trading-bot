# For auth/__init__.py
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes

# Similar structure for auth, admin, scheduler, and logs modules
