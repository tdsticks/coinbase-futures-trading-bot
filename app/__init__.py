from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

from config import Config

login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

from .main import main as main_blueprint
from .auth import auth as auth_blueprint
from .admin import setup_admin
from .models import db

# Custom Libraries
from app.logs.custom_logger import Log
from app.libraries.email_manager import EmailManager
from app.libraries.coinbase_api import CoinbaseAdvAPI
from app.libraries.signals_processor import SignalProcessor
from app.libraries.trade_manager import TradeManager
from app.scheduler.tasks import setup_scheduler


def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static')

    app.config.from_object(config_class)
    print("DEBUG MODE:", app.config['DEBUG'])

    app.db = db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    app.mail = mail.init_app(app)

    # Load Custom Libraries, assign to the Flask app
    app.custom_log = Log(app)  # Initialize and attach custom logger
    app.email_manager = EmailManager(app)
    app.cb_adv_api = CoinbaseAdvAPI(app)
    app.signal_processor = SignalProcessor(app)
    app.trade_manager = TradeManager(app)
    setup_scheduler(app)

    # Create all the models (tables) in the db
    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    setup_admin(app)

    # logger.info("create_app Complete")
    app.custom_log.log(True, "I", None,
                       msg1="---------- Flask create_app Complete ----------")

    return app
