from . import main
from flask import current_app, request, jsonify
from datetime import datetime
import pytz


@main.route('/', methods=['GET'])
def index():
    # print(":index:")
    current_app.custom_log.log(True, "I", True, None, ":index:")

    if request.method == 'GET':
        return "Its a bit empty here..."

    # if request.method == 'POST':
    #     data = request.json
    #     print("Received signal:", data)
    #     return jsonify({"status": "success", "message": "Signal received"}), 200


@main.route('/webhook', methods=['POST'])
def webhook():
    current_app.custom_log.log(True, "I", None, ":webhook:")

    # Parse the incoming JSON data
    data = request.json

    # If we get data
    if 'price' in data:
        current_app.custom_log.log(True, "I", None, "\nReceived signal:")
        # pp(data)
        current_app.custom_log.log(True, "I", None, data)

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

        # Check if the market is open or not
        # if current_app.trade_manager.is_trading_time(now):
        try:
            # Get the SignalProcessor through the TradeManager
            signal_stored = current_app.trade_manager.signal_processor.write_db_signal(signal_data)
            current_app.custom_log.log(True, "I", None, "  >>> Signal Stored", signal_stored)

            # Respond back to the webhook sender to acknowledge receipt
            return jsonify({"Status": "Success", "Message": "Signal received and stored"}), 201

        except Exception as e:
            current_app.custom_log.log(True, "E", "Unexpected write_db_signal Error:", msg1=e)
            return jsonify({"Status": "Unsuccessful",
                            "Message": "Signal received, but NOT stored",
                            "Data": data,
                            "Error": e}), 405
        # else:
        #     return jsonify({"Status": "Unsuccessful",
        #                     "Message": "Market is closed",
        #                     "Sata": data}), 204
    else:
        # Respond back to the webhook sender to acknowledge receipt
        return jsonify({"Status": "Unsuccessful",
                        "Message": "Signal not received",
                        "Sata": data}), 204
