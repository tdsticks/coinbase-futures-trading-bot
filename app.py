from flask import Flask, request, jsonify
from flask_migrate import Migrate
import logging
from logging.handlers import TimedRotatingFileHandler
from db import db
from pprint import pprint as pp
from trade_manager import LogOrConsole
from trade_manager import CoinbaseAdvAPI
from trade_manager import TradeManager
from flask_apscheduler import APScheduler
from datetime import datetime
import pytz
import os
import re


# set configuration values
class Config:
    SCHEDULER_API_ENABLED = True


# NOTE: Futures markets are open for trading from Sunday 6 PM to
#  Friday 5 PM ET (excluding observed holidays),
#  with a 1-hour break each day from 5 PM – 6 PM ET

# NOTE: Need to figure out the trading logic here with orders
#   Following Aurox guides, we should only be taking signals on the Weekly and maybe daily
#   We need to factor in the Futures closing after each month (April, May, June, etc.)
#   We should store each Weekly and Daily signal in the database to help track where we're at
#   While were in a Weekly Long or Short and the Futures closes for that month, we should
#   Re-open a Long or Short based on the signal. We only reverse once the opposing Weekly signal
#   comes into play. This is a long game.

# NOTE:
#   Perhaps one way we operate is if the Weekly is long, use the Daily Aurox signals for
#   longs only and close out after expiration or a certain percentage to minimize risk (10%?).
#   Then keep opening Daily longs per each indicator while under the Weekly long. perhaps we wait
#   for a duration or percentage from the last signal, or a reverse Daily signal before placing a close order.

# NOTE: Should we do laddering with orders to caught spikes and other liquidations or quick reversals?

# NOTE: Since this whole bot is based on the Aurox Indicator (Ax) signal. We really need to wait
#   and be patient with it. Again, weekly sigals are far and in few throughout the year.
#   Scenario One:
#       The week of Sep 25h, 2023 we see a green long signal. It wasn't until Sep 28th, 2023 using Coinbase
#       BTC/USD chart in Aurox that we see the first Daily signal. Now, technically we could start opening
#       a long trade after the Weekly comes in and that might be ok, but we're aiming for safety, especially
#       dealing with future contracts. BTC had been going sideways even prior to that weekly, so you really
#       need to watch the charts, turn off the trading (but keep the bot running to track the signals)
#       if you feel it's too risky or not worth trading.
#       Around the beginning of Oct (5th, 7th and 9th) we see more Daily signals (Short, Long, Short),
#       then a dip in the market until another green long on Oct 15th, then a nice surge in the market upwards.
#       Technically speaking, if we had waited to place the first trade around the first Daily (into Oct),
#       then we'd be in a new contract month and riding out the dip, it would have been a great place
#       to be. We could then close out at that Daily short signal right before end the of Oct on the 27th.
#       That would have been roughly 25% on that trade (or multiple trades if you DCA on the dip).
#       Note: We need to track and trade within the monthly contracts to avoid forceful closing them on Coinbase Futures.
#   Scenario Two:
#


def create_app():
    flask_app = Flask(__name__)
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aurox_signals.db'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['DEBUG'] = os.getenv('DEBUG', 'False') == 'True'

    # print("DEBUG:", os.getenv('DEBUG', 'False'))
    print("DEBUG:", flask_app.config['DEBUG'])

    db.init_app(flask_app)
    migrate = Migrate(flask_app, db)
    # print("migrate:", migrate)

    with flask_app.app_context():
        db.create_all()

    # Ensure log directory exists
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    handler = TimedRotatingFileHandler(
        filename=os.path.join(log_directory, 'flask_app.log'),
        when='H',
        interval=4,
        backupCount=120  # currently keeps 30 days of logs (120 rotations * 6 hours)
    )
    handler.suffix = "%Y-%m-%d %H:%M:%S"  # Date Time format
    handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}$")  # Ensures only files with dates are matched

    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    if flask_app.config['DEBUG']:
        # Set the logger level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        handler.setLevel(logging.DEBUG)
        flask_app.logger.addHandler(handler)
        flask_app.logger.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.WARNING)
        flask_app.logger.addHandler(handler)
        flask_app.logger.setLevel(logging.WARNING)

    # flask_app.logger.debug('----------------- restarting Flask app -----------------')
    flask_app.logger.info('----------------- restarting Flask app -----------------')
    # flask_app.logger.warning('----------------- restarting Flask app -----------------')
    # flask_app.logger.error('----------------- restarting Flask app -----------------')
    # flask_app.logger.critical('----------------- restarting Flask app -----------------')

    if flask_app.config['DEBUG']:
        flask_app.logger.info("Debugging is ON")

    return flask_app


app = create_app()

# Add the ApScheduler Config
app.config.from_object(Config())

cbapi = CoinbaseAdvAPI(app)
tm = TradeManager(app)
loc = LogOrConsole(app)  # Send to Log or Console or both

@app.route('/', methods=['GET'])
def index():
    # print(":index:")
    loc.log_or_console(True, "I", True, None, ":index:")

    if request.method == 'GET':
        return "Its a bit empty here..."

    # if request.method == 'POST':
    #     data = request.json
    #     print("Received signal:", data)
    #     return jsonify({"status": "success", "message": "Signal received"}), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    # print(":webhook:")
    loc.log_or_console(True, "I", None, ":webhook:")

    # Parse the incoming JSON data
    data = request.json

    # print("\nReceived signal:")
    loc.log_or_console(True, "I", None, "\nReceived signal:")
    # pp(data)
    loc.log_or_console(True, "I", None, data)

    if 'signal' not in data:
        data['signal'] = 'test'

    # NOTE: Not using this currently
    # tm.handle_aurox_signal(data['signal'], data['symbol'])

    signal_data = {
        'timestamp': data['timestamp'],
        'price': data['price'].replace(',', ''),  # Remove commas for numeric processing if necessary
        'signal': data['signal'],
        'trading_pair': data['symbol'],
        'timeUnit': data['timeUnit'],
        # 'message': data.get('message')  # Use .get for optional fields
    }

    tm.write_db_signal(signal_data)

    # Respond back to the webhook sender to acknowledge receipt
    return jsonify({"status": "success", "message": "Signal received"}), 200


#######################
# TODO: Now we know if we're within range of the last Daily
#   and should have placed an order (market?)
#   Do we then place some limit orders for spikes or bounces?

# TODO: Should we do the DCA limit orders, then track the DCA with
#   placing a moving limit order for the opposing side to take profit?
#######################

#######################
# Get Porfolios
# porfolio_uuid = cbapi.get_portfolios()
# print("porfolio_uuid:", porfolio_uuid)

# porfolio_breakdown = cbapi.get_portfolio_breakdown(portfolio_uuid=porfolio_uuid)
# print("porfolio_breakdown:", porfolio_breakdown)
#######################

# compare_daily = tm.compare_last_daily_to_todays_date()
# print("compare_daily:", compare_daily)

#######################
# List Orders
# future_product = cbapi.get_this_months_future()
# open_orders = cbapi.list_orders(product_id=future_product.product_id, order_status="OPEN")
# pp(open_orders)

# filled_orders = cbapi.list_orders(product_id=future_product.product_id, order_status="FILLED")
# pp(filled_orders)

# cbapi.store_orders(open_orders)
# cbapi.store_orders(filled_orders)
#######################

#######################
# Get Current Positions
# future_positions = cbapi.get_future_position('BIT-26APR24-CDE')
# pp(future_positions)
#######################

#######################
# Get Current Bid Ask Prices
# current_future_product = cbapi.get_this_months_future()
# print("current_future_product:", current_future_product)
#
# future_bid_ask_price = cbapi.get_current_bid_ask_prices(current_future_product.product_id)
# future_bid_price = future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
# future_ask_price = future_bid_ask_price['pricebooks'][0]['asks'][0]['price']
# print("bid:", future_bid_price, "ask:", future_ask_price)
#######################

#######################
# List Products
# list_products = cbapi.list_products()
# pp(list_products)
#######################

#######################
# Get Product
# get_product = cbapi.get_product("BIT-26APR24-CDE")
# pp(get_product)
#######################


#######################
# AP Scheduler
#######################

# If you wish to use anything from your Flask app context inside the job you can use something like this
# def blah():
#     with scheduler.app.app_context():
#         # do stuff

# initialize scheduler
scheduler = APScheduler()


@scheduler.task('interval', id='do_job_1', seconds=125, misfire_grace_time=900)
def get_balance_summary_job():
    loc.log_or_console(True, "D", None, ":get_balance_summary_job:")

    now = datetime.now(pytz.utc)
    # print("Is trading time?", tm.is_trading_time(now))

    # Check if the market is open or not
    if tm.is_trading_time(now):

        # Balance Summary get and store
        futures_balance = cbapi.get_balance_summary()
        # pp(futures_balance)

        cbapi.store_futures_balance_summary(futures_balance)


# Runs every 6 hours
@scheduler.task('interval', id='do_job_2', seconds=600, misfire_grace_time=900)
def check_coinbase_futures_products_job():
    # print('\n:check_coinbase_futures_products_job:')
    loc.log_or_console(True, "D", None, msg1=":check_coinbase_futures_products_job:")

    now = datetime.now(pytz.utc)
    # print("Is trading time?", tm.is_trading_time(now))

    # Check if the market is open or not
    if tm.is_trading_time(now):
        list_future_products = cbapi.list_products("FUTURE")
        # pp(list_future_products)
        cbapi.store_btc_futures_products(list_future_products)


@scheduler.task('interval', id='do_job_3', seconds=30, misfire_grace_time=900)
def check_trading_conditions_job():
    # print('\n:check_trading_conditions_job:')
    loc.log_or_console(True, "D", None, msg1=":check_trading_conditions_job:")

    # NOTE: This is the main trading method with additional methods
    #   to check profit and loss, plus DCA and close out trades

    now = datetime.now(pytz.utc)
    # print("Is trading time?", tm.is_trading_time(now))

    # Check if the market is open or not
    if tm.is_trading_time(now):
        tm.check_trading_conditions()


@scheduler.task('interval', id='do_job_4', seconds=120, misfire_grace_time=900)
def list_and_store_future_orders_job():
    # print('\n:list_and_store_future_orders_job:')
    loc.log_or_console(True, "D", None, msg1=":list_and_store_future_orders_job:")

    #
    # Check if the market is open or not
    now = datetime.now(pytz.utc)
    # print("Is trading time?", tm.is_trading_time(now))

    if tm.is_trading_time(now):

        future_product = cbapi.get_this_months_future()
        # print("future_product:", future_product)
        loc.log_or_console(True, "I", "future_product", msg1=future_product.product_id)

        # ORDER TYPES:
        # [OPEN, FILLED, CANCELLED, EXPIRED, FAILED, UNKNOWN_ORDER_STATUS]

        # List Orders
        # all_orders = cbapi.list_orders(product_id=future_product.product_id, order_status=None)
        ## print("all_orders count:", len(all_orders['orders']))
        # loc.log_or_console(True, msg1="all_orders:", msg2=len(all_orders['orders']))
        #
        # if len(all_orders['orders']) > 0:
        #     cbapi.store_or_update_orders(all_orders)

        # REVIEW: Was getting an error from this order_status: UNKNOWN_ORDER_STATUS

        all_order_status = ["OPEN", "FILLED", "CANCELLED", "EXPIRED", "FAILED"]
        # all_order_status = ["OPEN"]
        for status in all_order_status:
            orders = cbapi.list_orders(product_id=future_product.product_id, order_status=status)
            # print(status, " orders count:", len(orders['orders']))
            loc.log_or_console(True, "D", status, "orders cnt:", len(orders['orders']))

            if len(orders['orders']) > 0:
                cbapi.store_or_update_orders(orders)

# TODO: Need to adjust check for contract expires and switch a few days prior
#  to the closing of the contract or we just let it
#  go and reopen in the next contract trading session


# @scheduler.task('interval', id='do_job_5', seconds=10, misfire_grace_time=900)
# def check_for_contract_expires_job():
#     # print('\n:check_for_contract_expires_job:')
#     loc.log_or_console(True, "D", None, msg1=":check_for_contract_expires_job:")
#
#     tm.check_for_contract_expires()

# @scheduler.task('interval', id='do_job_5', seconds=30, misfire_grace_time=900)
# def list_future_positions_job():
#     print('\n:list_future_positions_job:')
#     # Get Current Positions
#     future_positions = cbapi.list_future_positions()
#     # pp(future_positions)
#     cbapi.store_future_positions(future_positions)

# @scheduler.task('interval', id='do_job_6', seconds=150000, misfire_grace_time=900)
# def test_ladder_orders_job():
#     print('\n:test_ladder_orders_job:')
#
#     # Get this months current product
#     current_future_product = cbapi.get_this_months_future()
#     print(" current_future_product:", current_future_product.product_id)
#
#     # Get Current Bid Ask Prices
#     cur_future_bid_ask_price = cbapi.get_current_bid_ask_prices(
#         current_future_product.product_id)
#     cur_future_bid_price = cur_future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
#     cur_future_ask_price = cur_future_bid_ask_price['pricebooks'][0]['asks'][0]['price']
#     print(f" Prd: {current_future_product.product_id} - "
#           f"Current Futures: bid: ${cur_future_bid_price} "
#           f"ask: ${cur_future_ask_price}")
#
#     # side = "BUY"
#     side = "SELL"
#
#     tm.ladder_orders(side=side,
#                      product_id=current_future_product.product_id,
#                      bid_price=cur_future_bid_price,
#                      ask_price=cur_future_ask_price)

# @scheduler.task('interval', id='do_job_6', seconds=150000, misfire_grace_time=900)
# def test_create_order_job():
#     print('\n:test_create_order_job:')
#
#     # Get this months current product
#     current_future_product = cbapi.get_this_months_future()
#     print(" current_future_product:", current_future_product.product_id)
#
#     # Get Current Bid Ask Prices
#     cur_future_bid_ask_price = cbapi.get_current_bid_ask_prices(
#         current_future_product.product_id)
#     cur_future_bid_price = cur_future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
#     cur_future_ask_price = cur_future_bid_ask_price['pricebooks'][0]['asks'][0]['price']
#     print(f" Prd: {current_future_product.product_id} - "
#           f"Current Futures: bid: ${cur_future_bid_price} "
#           f"ask: ${cur_future_ask_price}")
#
#
#     two_percent_offset = int(float(cur_future_bid_price) * 0.02)
#     print(" two_percent_offset:", two_percent_offset)
#
#     # side = "BUY"
#     side = "SELL"
#
#     if side == "BUY":
#         # BUY / LONG
#         limit_price = cbapi.adjust_price_to_nearest_increment(
#             int(cur_future_bid_price) - two_percent_offset)
#         print(" Buy Long limit_price: $", limit_price)

#     elif side == "SELL":
#         # SELL / SHORT
#         limit_price = cbapi.adjust_price_to_nearest_increment(
#             int(cur_future_ask_price) + two_percent_offset)
#         print(" Sell Short limit_price: $", limit_price)
#
#     size = "1"
#     leverage = "3"
#
#     order_type = "market_market_ioc"
#     # order_type = "limit_limit_gtc"
#
#     # cbapi.create_order(side=side,
#     #                    product_id=current_future_product.product_id,
#     #                    size=size,
#     #                    limit_price=limit_price,
#     #                    leverage=leverage,
#     #                    order_type=order_type)


# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True

# @scheduler.task('interval', id='do_job_10', seconds=30, misfire_grace_time=900)
# def testing():
#     print('\n:testing:')


scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    # print(":", __name__, ":")
    # Note: On PythonAnywhere or other production environments, you might not need to run the app like this.
    app.run(use_reloader=False, debug=True, port=5000)
