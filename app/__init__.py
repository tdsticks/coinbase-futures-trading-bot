from datetime import datetime

from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import threading

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
from app.libraries.trailing_take_profit import TrailingTakeProfit
from app.libraries.list_orders_websocket import ListOrdersWebsocket
from app.scheduler.tasks import setup_scheduler

# TODO: What happens if the Aurox site goes down or has interruptions and we don't receive signals?
#   How do we catch up to the latest signals that came in already? Email?
#   Should create a separate process / app just for signals to to write to the same database
# TODO: Since the market closes on holidays and 5PM on Friday's should we limit trading on those days?
# TODO: Notification Alerts
# TODO: Investigate CCXT integration
# TODO: Need a way to manually trigger bot to open trade when I want
# TODO: Need to build a UI (web interface using Vue or Vite or Streamlite)
#   Dashboard
#       Open Trades / Positions
#       Funds
#       Risk / Liquidation %
#       Signal Status
#   Trading view
#       Open Trades / Positions
#       Manual Trade (add Laddering DCA)
#       Chart with current orders (Avg Entry, Take Profit, DCA orders)
#   Bot Settings
# TODO: Do we also create a trailing take profit feature?
# TODO: Do we need the websocket to watch prices? or to trade Orders faster?
# TODO: Should we start storing Aurox signals historically again?
#   Maybe we could formulate better signals direction or calculation from this
# TODO: Look into adding a timestamp calculation to our calc_all_signals_score_for_direction
#   Could use current and 1 previous Aurox alert to help calculate price difference, plus length of time


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
    app.trailing_take_profit = TrailingTakeProfit(app)
    # app.list_orders_websocket = ListOrdersWebsocket(app)
    setup_scheduler(app)

    # Create all the models (tables) in the db
    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    setup_admin(app)

    # TODO: Need to only enable once we have a trade open

    # Run the Coinbase Websocket for trailing take profit
    # This will start the WebSocket client in a separate thread
    # websocket_thread = threading.Thread(target=app.trailing_take_profit.run_cb_wsclient)
    # websocket_thread = threading.Thread(target=app.list_orders_websocket.run_websocket)

    # websocket_thread = threading.Thread(target=app.trailing_take_profit.run_trailing_take_profit)

    # websocket_thread = threading.Thread(target=app.cb_adv_api.threaded_save_historical_candles)
    websocket_thread = threading.Thread(target=app.cb_adv_api.threaded_save_current_candles)
    websocket_thread.daemon = True  # Daemonize thread to terminate with the main app
    websocket_thread.start()

    # logger.info("create_app Complete")
    app.custom_log.log(True, "D", None,
                       msg1="---------- Flask create_app Complete ----------")

    return app
