from . import main
from flask import render_template, request, jsonify

@main.route('/')
def index():
    return "Welcome to the Home Page!"

# More routes as per the original app.py
