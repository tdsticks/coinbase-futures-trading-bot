from flask import Flask, request, jsonify
from flask_migrate import Migrate
from db import db
from pprint import pprint as pp
from trade_manager import CoinbaseAdvAPI
from trade_manager import TradeManager
from flask_apscheduler import APScheduler


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

    db.init_app(flask_app)
    migrate = Migrate(flask_app, db)
    print("migrate:", migrate)

    with flask_app.app_context():
        db.create_all()

    return flask_app


app = create_app()

# Add the ApScheduler Config
app.config.from_object(Config())

cbapi = CoinbaseAdvAPI(app)
tm = TradeManager(app)


@app.route('/', methods=['GET'])
def index():
    print(":index:")

    if request.method == 'GET':
        return "Its a bit empty here..."

    # if request.method == 'POST':
    #     data = request.json
    #     print("Received signal:", data)
    #     return jsonify({"status": "success", "message": "Signal received"}), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    print(":webhook:")

    # Parse the incoming JSON data
    data = request.json

    print("\nReceived signal:")
    pp(data)

    if 'signal' not in data:
        data['signal'] = 'test'

    tm.handle_aurox_signal(data['signal'], data['symbol'])

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
# Get the the future products for BTC and store in DB
# Then using this months future product, get the bid and ask prices
# TODO: This should run once a day in the morning.
# list_future_products = cbapi.list_products("FUTURE")
# pp(list_future_products)
# cbapi.store_btc_futures_products(list_future_products)
#######################

#######################
# check_contract_expiration = tm.check_for_contract_expires()
# print(check_contract_expiration)
#######################

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


# Runs every 6 hours
@scheduler.task('interval', id='do_job_0', seconds=21600, misfire_grace_time=900)
def check_coinbase_futures_products_job():
    print('\n:check_coinbase_futures_products_job:')

    list_future_products = cbapi.list_products("FUTURE")
    # pp(list_future_products)
    cbapi.store_btc_futures_products(list_future_products)


@scheduler.task('interval', id='do_job_1', seconds=60, misfire_grace_time=900)
def check_trading_conditions_job():
    print('\n:check_trading_conditions_job:')

    tm.check_trading_conditions()


# @scheduler.task('interval', id='do_job_2', seconds=30, misfire_grace_time=900)
# def check_profit_or_loss_job():
#     print('\n:check_profit_or_loss_job:')
#     # Get Current Positions
#     tm.tracking_current_position_profit_loss()


# @scheduler.task('interval', id='do_job_3', seconds=30, misfire_grace_time=900)
# def list_future_positions_job():
#     print('\n:list_future_positions_job:')
#     # Get Current Positions
#     future_positions = cbapi.list_future_positions()
#     # pp(future_positions)
#
#     cbapi.store_future_positions(future_positions)


@scheduler.task('interval', id='do_job_4', seconds=60, misfire_grace_time=900)
def get_balance_summary_job():
    print('\n:get_balance_summary_job:')
    # Balance Summary get and store
    futures_balance = cbapi.get_balance_summary()
    # pp(futures_balance)

    cbapi.store_futures_balance_summary(futures_balance)


@scheduler.task('interval', id='do_job_5', seconds=150000, misfire_grace_time=900)
def test_create_order_job():
    print('\n:test_create_order_job:')

    # Get this months current product
    current_future_product = cbapi.get_this_months_future()
    print(" current_future_product:", current_future_product.product_id)

    # Get Current Bid Ask Prices
    cur_future_bid_ask_price = cbapi.get_current_bid_ask_prices(
        current_future_product.product_id)
    cur_future_bid_price = cur_future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
    cur_future_ask_price = cur_future_bid_ask_price['pricebooks'][0]['asks'][0]['price']
    print(f" Prd: {current_future_product.product_id} - "
          f"Current Futures: bid: ${cur_future_bid_price} "
          f"ask: ${cur_future_ask_price}")

    two_percent_offset = int(float(cur_future_bid_price) * 0.01)
    print(" two_percent_offset:", two_percent_offset)

    # side = "BUY"
    side = "SELL"

    if side == "BUY":
        # BUY / LONG
        limit_price = cbapi.adjust_price_to_nearest_increment(
            int(cur_future_bid_price) - two_percent_offset)
        print(" Buy Long limit_price: $", limit_price)
    elif side == "SELL":
        # SELL / SHORT
        limit_price = cbapi.adjust_price_to_nearest_increment(
            int(cur_future_bid_price) + two_percent_offset)
        print(" Sell Short limit_price: $", limit_price)

    size = "1"
    leverage = "3"

    order_type = "market_market_ioc"
    # order_type = "limit_limit_gtc"

    # cbapi.create_order(side=side,
    #                    product_id=current_future_product.product_id,
    #                    size=size,
    #                    limit_price=limit_price,
    #                    leverage=leverage,
    #                    order_type=order_type)


# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    print(":", __name__, ":")

    # Note: On PythonAnywhere or other production environments, you might not need to run the app like this.
    app.run(use_reloader=False, debug=True, port=5000)
