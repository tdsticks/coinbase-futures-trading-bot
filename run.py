from app import create_app
from config import DevelopmentConfig


app = create_app(DevelopmentConfig)

if __name__ == '__main__':

    # Note: On PythonAnywhere or other production environments,
    # you might not need to run the app like this.
    app.run(use_reloader=False, debug=app.config['DEBUG'], port=5000)
