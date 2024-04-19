from flask import Flask, request, jsonify
from flask_migrate import Migrate
from db import db
from pprint import pprint as pp
from trade_manager import CoinbaseAdvAPI
from trade_manager import TradeManager


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

cbapi = CoinbaseAdvAPI(app)
tm = TradeManager(app)


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
# Get the latest Weekly and Daily signals, then
# compare the Daily to today's date. Do we need to know this?

# TODO: Now we know if we're within range of the last Daily
#   and should have placed an order (market?)
#   Do we then place some limit orders for spikes or bounces?

# TODO: Should we do the DCA limit orders, then track the DCA with
#   placing a moving limit order for the opposing side to take profit?
#######################

#######################
# porfolios = cbapi.list_and_get_portfolios()
# print("porfolios:", porfolios)
#######################

# weekly_signals = tm.get_latest_weekly_signal()
# daily_signals = tm.get_latest_daily_signal()

# print("weekly_signals:", weekly_signals)
# print("\nweekly_signals: signal", weekly_signals.time_unit)
# print("weekly_signals: signal", weekly_signals.timestamp)
# print("weekly_signals: signal", weekly_signals.price)
# print("weekly_signals: signal", weekly_signals.signal)

# print("daily_signals:", daily_signals)
# print("\ndaily_signals: signal", daily_signals.time_unit)
# print("daily_signals: signal", daily_signals.timestamp)
# print("daily_signals: signal", daily_signals.price)
# print("daily_signals: signal", daily_signals.signal)

# compare_daily = tm.compare_last_daily_to_todays_date()
# print("compare_daily:", compare_daily)

#######################
# Get the the future products for BTC and store in DB
# Then using this months future product, get the bid and ask prices
# TODO: This should run once a day in the morning.
#  Setup as a Pythonanywhere cron task within a Flask route
# list_future_products = cbapi.list_products("FUTURE")
# pp(list_future_products)
# cbapi.store_btc_futures_products(list_future_products)
#######################

#######################
# check_contract_expiration = tm.check_for_contract_expires()
# print(check_contract_expiration)
#######################

#######################
# Balance Summary get and store
futures_balance = cbapi.get_balance_summary()
# pp(futures_balance)
cbapi.store_futures_balance_summary(futures_balance)
#######################

#######################
# List Orders
future_product = cbapi.get_this_months_future()
# open_orders = cbapi.list_orders(product_id=future_product.product_id, order_status="OPEN")
# pp(open_orders)
filled_orders = cbapi.list_orders(product_id=future_product.product_id, order_status="FILLED")
# pp(filled_orders)
#######################

#######################
# Get Current Positions
future_positions = cbapi.list_future_positions()
# pp(future_positions)
cbapi.store_future_positions(future_positions)
#######################

#######################
# Get Current Positions
# future_positions = cbapi.get_future_position('BIT-26APR24-CDE')
# pp(future_positions)
#######################

#######################
# Get Current Positions
curret_profit_or_loss = tm.tracking_current_position_profit_loss()
# pp(curret_profit_or_loss)
#######################



if __name__ == '__main__':
    print(":", __name__, ":")

    # Note: On PythonAnywhere or other production environments, you might not need to run the app like this.
    app.run(debug=True, port=5000)
