from flask import Flask, request, jsonify
from flask_migrate import Migrate
from db import db
from pprint import pprint as pp
from trade_manager import TradeManager


def create_app():
    flask_app = Flask(__name__)
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aurox_signals.db'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(flask_app)
    migrate = Migrate(flask_app, db)

    with flask_app.app_context():
        db.create_all()

    return flask_app


app = create_app()

tm = TradeManager(app)

# NOTE: Need to figure out the trading logic here with orders
#   Following Aurox guides, we should only be taking signals on the Weekly and maybe daily
#   We need to factor in the Futures closing after each month (April, May, June, etc.)
#   We should store each Weekly and Daily signal in the database to help track where we're at
#   While were in a Weekly Long or Short and the Futures closes for that month, we should
#   Re-open a Long or Short based on the signal. We only reverse once the opposing Weekly signal
#   comes into play. So this is a long game.

# NOTE:
#   Perhaps one way we operate is if the Weekly is long, use the Daily Aurox signals for
#   longs only and close out after expiration or a certain percentage to minimize risk (10%?).
#   Then keep opening Daily longs per each indicator while under the Weekly long. perhaps we wait
#   for a duration or percentage from the last signal, or a reverse Daily signal before placing an order

# NOTE: Should we do laddering with orders to caught spikes and other liquidations or quick reversals?


@app.route('/', methods=['GET'])
def index():
    print(":index:")

    # result = cb_api()
    # return jsonify(msg)

    if request.method == 'GET':
        return '<h1>HELLO WORD</h1>'

    # if request.method == 'POST':
    #     data = request.json
    #     print("Received signal:", data)
    #     return jsonify({"status": "success", "message": "Signal received"}), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    print(":webhook:")
    # Parse the incoming JSON data
    data = request.json
    # print("Received signal:", data)

    print("\nReceived signal:")
    pp(data)

    if 'signal' not in data:
        data['signal'] = 'test'

    tm.handle_aurox_signal(data['signal'], data['symbol'])

    # Create a new AuroxSignal object from received data
    # new_signal = AuroxSignal(
    #     timestamp=data['timestamp'],
    #     price=data['price'].replace(',', ''),  # Remove commas for numeric processing if necessary
    #     signal=data['signal'],
    #     symbol=data['symbol'],
    #     time_unit=data['timeUnit'],
    #     message=data.get('message')  # Use .get for optional fields
    # )
    #
    # # Add new_signal to the session and commit it
    # db.session.add(new_signal)
    # db.session.commit()
    #
    # print("New signal stored:", new_signal)

    signal_data = {
        'timestamp':data['timestamp'],
        'price': data['price'].replace(',', ''),  # Remove commas for numeric processing if necessary
        'signal': data['signal'],
        'trading_pair': data['symbol'],
        'timeUnit': data['timeUnit'],
        'message': data.get('message')  # Use .get for optional fields
    }

    tm.write_db_signal(signal_data)

    # Respond back to the webhook sender to acknowledge receipt
    return jsonify({"status": "success", "message": "Signal received"}), 200


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

if __name__ == '__main__':
    print(":", __name__, ":")

    # Note: On PythonAnywhere or other production environments, you might not need to run the app like this.
    app.run(debug=True, port=5000)