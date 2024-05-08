from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_mail import Mail
import configparser
import logging
from logging.handlers import TimedRotatingFileHandler
from db import db
from flask_apscheduler import APScheduler
from datetime import datetime
import pytz
import os
import re

# Custom Libraries
import logs
from coinbase_api import CoinbaseAdvAPI
from trade_manager import TradeManager

# TODO: What happens if the Aurox site goes down or has interruptions and we don't receive signals?
#   How do we catch up to the latest signals that came in already? Email?
# TODO: Email Alerts
# TODO: Notification Alerts
# TODO: Update profit loss method with updated DCA method
# TODO: Since the market closes on holidays and 5PM on Friday's should we limit trading on those days?
# TODO: Need a way to manually trigger bot to open trade when I want
# TODO: Need to build a UI (web interface using Vue or Vite)
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
# TODO: Do we need the websocket to watch prices?
# TODO: Should we start storing Aurox signals historically again?
#   Maybe we could formulate better signals direction or calculation from this
# TODO: Look into adding a timestamp calculation to our calc_all_signals_score_for_direction
#   Could use current and 1 previous Aurox alert to help calculate price difference, plus length of time


config = configparser.ConfigParser()
config.read('bot_config.ini')
config.sections()


# set configuration values
class Config:
    SCHEDULER_API_ENABLED = True

# NOTE: Futures markets are open for trading from Sunday 6 PM to
#  Friday 5 PM ET (excluding observed holidays),
#  with a 1-hour break each day from 5 PM – 6 PM ET


def create_app():
    flask_app = Flask(__name__)

    """
    Database Setup and Configure
    """
    sqlalchemy_database_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    sqlalchemy_track_modifications = os.getenv('SQLALCHEMY_DATABASE_URI')
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_database_uri
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = sqlalchemy_track_modifications
    flask_app.config['DEBUG'] = os.getenv('DEBUG', 'False') == 'True'

    # print("DEBUG:", os.getenv('DEBUG', 'False'))
    print("DEBUG:", flask_app.config['DEBUG'])

    db.init_app(flask_app)
    Migrate(flask_app, db)

    with flask_app.app_context():
        db.create_all()

    """
    Email Setup and Configure
    """
    use_email = config['email.config']['use_email']
    mail_class = None
    if use_email == 'True':
        flask_app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        flask_app.config['MAIL_PORT'] = 587
        flask_app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Use your actual Gmail address
        flask_app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Use your generated App Password
        flask_app.config['MAIL_USE_TLS'] = True
        flask_app.config['MAIL_USE_SSL'] = False
        mail_class = Mail(flask_app)

    """
    Logging Setup and Configure
    """
    # Ensure log directory exists
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_filename = config['logs.config']['log_filename']
    when = config['logs.config']['time_rotation_when']
    interval = int(config['logs.config']['interval'])
    backup_count = int(config['logs.config']['backup_count'])

    # Log file handler with timed rotating files
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_directory, log_filename),
        when=when,
        interval=interval,
        backupCount=backup_count  # currently keeps 30 days of logs (120 rotations * 4 hours)
    )
    file_handler.suffix = "%Y-%m-%d %H.%M.%S"  # Date Time format
    file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}$")  # Ensures on ly files with dates are matched

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s %(message)s'
    )

    # Set the formatter to the file logging
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler()

    # Set the formatter to the console
    console_handler.setFormatter(formatter)

    if flask_app.config['DEBUG']:
        # Set the logger level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        flask_app.logger.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
    else:
        flask_app.logger.setLevel(logging.WARNING)
        file_handler.setLevel(logging.WARNING)
        console_handler.setLevel(logging.WARNING)

    # Remove default Flask logger handlers and add custom handlers
    del flask_app.logger.handlers[:]
    flask_app.logger.addHandler(file_handler)  # Add the file handler
    flask_app.logger.addHandler(console_handler)  # Add the console handler

    # flask_app.logger.debug('----------------- restarting Flask app -----------------')
    flask_app.logger.info('----------------- restarting Flask app -----------------')
    # flask_app.logger.warning('----------------- restarting Flask app -----------------')
    # flask_app.logger.error('----------------- restarting Flask app -----------------')
    # flask_app.logger.critical('----------------- restarting Flask app -----------------')

    if flask_app.config['DEBUG']:
        flask_app.logger.info("Debugging is ON")

    return flask_app, mail_class


app, mail_cls = create_app()

# Add the ApScheduler Config
app.config.from_object(Config())

cbapi = CoinbaseAdvAPI(app, mail_cls)
tm = TradeManager(app, mail_cls)
log = logs.Log(app)  # Send to Log

enable_live_trading = config['trade.conditions']['enable_live_trading']
if enable_live_trading == 'True':
    log.log(True, "W", None, "\n")
    log.log(True, "W", None, "---------------------")
    log.log(True, "W", None, "Live Trading ENABLED!")
    log.log(True, "W", None, "---------------------")
    log.log(True, "W", None, "\n")
else:
    log.log(True, "W", None, "\n")
    log.log(True, "W", None, "---------------------")
    log.log(True, "W", None, "Live Trading DISABLED!")
    log.log(True, "W", None, "---------------------")
    log.log(True, "W", None, "\n")


@app.route('/', methods=['GET'])
def index():
    # print(":index:")
    log.log(True, "I", True, None, ":index:")

    if request.method == 'GET':
        return "Its a bit empty here..."

    # if request.method == 'POST':
    #     data = request.json
    #     print("Received signal:", data)
    #     return jsonify({"status": "success", "message": "Signal received"}), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    log.log(True, "I", None, ":webhook:")

    # Parse the incoming JSON data
    data = request.json

    # If we get data
    if data:
        log.log(True, "I", None, "\nReceived signal:")
        # pp(data)
        log.log(True, "I", None, data)

        if 'signal' not in data:
            data['signal'] = 'test'

        signal_data = {
            'timestamp': data['timestamp'],
            'price': data['price'].replace(',', ''),  # Remove commas for numeric processing if necessary
            'signal': data['signal'],
            'trading_pair': data['symbol'],
            'timeUnit': data['timeUnit'],
            # 'message': data.get('message')  # Use .get for optional fields
        }

        now = datetime.now(pytz.utc)
        # print("Is trading time?", tm.is_trading_time(now))

        # Check if the market is open or not
        if tm.is_trading_time(now):
            try:
                # Get the SignalProcessor through the TradeManager
                signal_stored = tm.signal_processor.write_db_signal(signal_data, tm)
                log.log(True, "I", None, "  >>> Signal Stored", signal_stored)

                # Respond back to the webhook sender to acknowledge receipt
                return jsonify({"Status": "Success", "Message": "Signal received and stored"}), 201

            except Exception as e:
                log.log(True, "E", "Unexpected write_db_signal Error:", msg1=e)
                return jsonify({"Status": "Unsuccessful",
                                "Message": "Signal received, but NOT stored",
                                "Data": data,
                                "Error": e}), 405
    else:
        # Respond back to the webhook sender to acknowledge receipt
        return jsonify({"Status": "Unsuccessful",
                        "Message": "Signal not received",
                        "Sata": data}), 204


#######################
# AP Scheduler
#######################

# If you wish to use anything from your Flask app context inside the job you can use something like this
# def blah():
#     with scheduler.app.app_context():
#         # do stuff

# initialize scheduler
scheduler = APScheduler()

disable_balance_summary = config['scheduler.jobs']['disable_balance_summary']
disable_coinbase_futures_products = config['scheduler.jobs']['disable_coinbase_futures_products']
disable_trading_conditions = config['scheduler.jobs']['disable_trading_conditions']
disable_list_and_store_future_orders = config['scheduler.jobs']['disable_list_and_store_future_orders']

balance_summary_time = int(config['scheduler.jobs']['balance_summary_time'])
coinbase_futures_products_time = int(config['scheduler.jobs']['coinbase_futures_products_time'])
trading_conditions_time = int(config['scheduler.jobs']['trading_conditions_time'])
future_orders_time = int(config['scheduler.jobs']['future_orders_time'])


@scheduler.task('interval', id='balance_summary', seconds=balance_summary_time, misfire_grace_time=900)
def get_balance_summary_job():
    log.log(True, "D", None, ":get_balance_summary_job:")

    now = datetime.now(pytz.utc)
    # print("Is trading time?", tm.is_trading_time(now))

    # Check if the market is open or not
    if tm.is_trading_time(now):
        # Balance Summary get and store
        futures_balance = cbapi.get_balance_summary()
        # pp(futures_balance)

        cbapi.store_futures_balance_summary(futures_balance)


# Runs every 6 hours
@scheduler.task('interval', id='products', seconds=coinbase_futures_products_time, misfire_grace_time=900)
def get_coinbase_futures_products_job():
    log.log(True, "D", None, msg1=":get_coinbase_futures_products_job:")

    now = datetime.now(pytz.utc)
    # print("Is trading time?", tm.is_trading_time(now))

    # Check if the market is open or not
    if tm.is_trading_time(now):
        list_future_products = cbapi.list_products("FUTURE")
        # pp(list_future_products)
        cbapi.store_btc_futures_products(list_future_products)


@scheduler.task('interval', id='trading', seconds=trading_conditions_time, misfire_grace_time=900)
def check_trading_conditions_job():
    log.log(True, "I", None, msg1="------------------------------")
    log.log(True, "I", None, msg1=":check_trading_conditions_job:")

    # NOTE: This is the main trading method with additional methods
    #   to check profit and loss, plus DCA and close out trades

    now = datetime.now(pytz.utc)

    # Check if the market is open or not
    if tm.is_trading_time(now):
        tm.check_trading_conditions()


@scheduler.task('interval', id='orders', seconds=future_orders_time, misfire_grace_time=900)
def list_and_store_future_orders_job():
    log.log(True, "I", None, msg1="------------------------------")
    log.log(True, "D", None, msg1=":list_and_store_future_orders_job:")

    # Check if the market is open or not
    now = datetime.now(pytz.utc)

    # BUG: Was getting an error from this order_status: UNKNOWN_ORDER_STATUS

    all_order_status = ["OPEN", "FILLED", "CANCELLED", "EXPIRED", "FAILED"]

    # all_order_status = ["OPEN"]

    def run_all_list_orders(statuses, month, product_id):
        log.log(True, "D", None, None)
        month_msg = f"Month: {month}"
        product_id_msg = f"Product: {product_id}"
        log.log(True, "D", month_msg, product_id_msg)
        for status in statuses:
            orders = cbapi.list_orders(product_id=product_id, order_status=status)
            status_msg = f" {status}"
            log.log(True, "D", status_msg, "Cnt", len(orders['orders']))

            # if status == "FAILED":
            #     log.log(True, "D", status_msg, "Failed Orders",
            #                        orders['orders'])

            if len(orders['orders']) > 0:
                cbapi.store_or_update_orders_from_api(orders)

    if tm.is_trading_time(now):
        curr_month = cbapi.get_current_short_month_uppercase()
        next_month = cbapi.get_next_short_month_uppercase()
        # log.log(True, "I","next_month", next_month)

        current_future_product = cbapi.get_relevant_future_from_db()
        next_months_future_product = cbapi.get_relevant_future_from_db(month_override=next_month)
        curr_product_id = current_future_product.product_id
        next_product_id = next_months_future_product.product_id

        run_all_list_orders(all_order_status, curr_month, curr_product_id)
        run_all_list_orders(all_order_status, next_month, next_product_id)

        # List Orders
        # ORDER TYPES:
        # [OPEN, FILLED, CANCELLED, EXPIRED, FAILED, UNKNOWN_ORDER_STATUS]
        # all_orders = cbapi.list_orders(product_id=future_product.product_id, order_status=None)
        ## print("all_orders count:", len(all_orders['orders']))
        # log.log(True, msg1="all_orders:", msg2=len(all_orders['orders']))
        #
        # if len(all_orders['orders']) > 0:
        #     cbapi.store_or_update_orders_from_api(all_orders)


# @scheduler.task('interval', id='do_job_6', seconds=15000, misfire_grace_time=900)
# def manual_ladder_orders_job():
#     print('\n:test_ladder_orders_job:')
#
#     next_months_product_id, next_month = tm.check_for_contract_expires()
#     print("next_months_product_id:", next_months_product_id)
#     print("next_month:", next_month)
#
#     # Get this months current product
#     relevant_future_product = cbapi.get_relevant_future_from_db(month_override=next_month)
#     print(" relevant_future_product:", relevant_future_product.product_id)
#
#     # Get Current Bid Ask Prices
#     cur_future_bid_ask_price = cbapi.get_current_bid_ask_prices(
#         relevant_future_product.product_id)
#     cur_future_bid_price = cur_future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
#     cur_future_ask_price = cur_future_bid_ask_price['pricebooks'][0]['asks'][0]['price']
#     print(f" Prd: {relevant_future_product.product_id} - "
#           f"Current Futures: bid: ${cur_future_bid_price} "
#           f"ask: ${cur_future_ask_price}")
#
#     # side = "BUY"
#     side = "SELL"
#     print(" side:", side)
#
#     # How many ladder orders?
#     # ladder_order_qty = 8
#     ladder_order_qty = int(config['dca.ladder.trade_percentages']['ladder_quantity'])
#
#     # Override the starting entry price
#     manual_price = '58945'
#
#     tm.ladder_orders(quantity=ladder_order_qty, side=side,
#                      product_id=relevant_future_product.product_id,
#                      bid_price=cur_future_bid_price,
#                      ask_price=cur_future_ask_price,
#                      manual_price=manual_price)

# @scheduler.task('interval', id='future_positions', seconds=10, misfire_grace_time=900)
# def get_current_position_job():
#     log.log(True, "I", None, msg1="------------------------------")
#     log.log(True, "I", None, msg1=":get_current_position_job:")
#
#     future_contract = cbapi.get_relevant_future_from_db()
#
#     # Get Current Positions
#     future_positions = cbapi.get_future_position(future_contract.product_id)
#     pp(future_positions)


scheduler.init_app(app)
scheduler.start()

# Check if we've disabled any of the schedule jobs from the bot_config.ini file
if disable_balance_summary == 'True':
    log.log(True, "I", " !!! Pausing Schedule Job", msg1="balance_summary")
    scheduler.pause_job('balance_summary')
if disable_coinbase_futures_products == 'True':
    log.log(True, "I", " !!! Pausing Schedule Job", msg1="products")
    scheduler.pause_job('products')
if disable_trading_conditions == 'True':
    log.log(True, "I", " !!! Pausing Schedule Job", msg1="trading")
    scheduler.pause_job('trading')
if disable_list_and_store_future_orders == 'True':
    log.log(True, "I", " !!! Pausing Schedule Job", msg1="orders")
    scheduler.pause_job('orders')

if __name__ == '__main__':
    # Note: On PythonAnywhere or other production environments, you might not need to run the app like this.
    app.run(use_reloader=False, debug=True, port=5000)
