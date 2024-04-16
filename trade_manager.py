from coinbase import jwt_generator
# from app import create_app
from models.signals import AuroxSignal
from db import db, db_errors
from dotenv import load_dotenv
from pprint import pprint as pp
import os
import http.client
import json
import uuid

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
UUID = os.getenv('UUID')
# print("UUID:", UUID)
# print("API_KEY:", API_KEY)

# NOTE: Aurox Ax Signal Guide
#   https://docs.getaurox.com/product-docs/aurox-terminal-guides/indicator-guides/
#       aurox-indicator/how-the-aurox-indicator-functions-part-1

# NOTE: Futures markets are open for trading from Sunday 6 PM to
#  Friday 5 PM ET (excluding observed holidays),
#  with a 1-hour break each day from 5 PM – 6 PM ET


# TODO: Make coinbase into class library for importing into Flask
# TODO: Setup trading logic
# TODO: Create Buy order for long or short
# TODO: Create Close order for long or short
# TODO: Parse Aurox signal Daily and Weekly
# TODO: Monthly contract expiration
# TODO: Need to factor in trading hours


class CoinbaseAdvAPI:

    def __init__(self):
        print(":Initializing CoinbaseAdvAPI:")

        # Assign the initial http connection
        self.conn = http.client.HTTPSConnection("api.coinbase.com")

    @staticmethod
    def jwt_authorization_header(method, path):
        """
        Be sure to path the same request method and API url (path) to both the JWT and the API call
        """
        # print(":jwt_authorization_header:")

        jwt_uri = jwt_generator.format_jwt_uri(method, path)
        jwt_token = jwt_generator.build_rest_jwt(jwt_uri, API_KEY, API_SECRET)

        create_headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0)"
        }
        return create_headers

    def cb_api_call(self, p_headers, method, path, payload_param=None):
        """
        Be sure to path the same request method and API url (path) to both the JWT and the API call
        """
        print(":cb_api_call:")

        # Check to see if we have a payload, otherwise assign it empty
        if payload_param is not None:
            payload = payload_param
        else:
            payload = ''
        print("payload:", payload)

        # Make the API request
        self.conn.request(method, path, payload, p_headers)

        # Assign the response from the API request
        res = self.conn.getresponse()
        # print("response:", res)

        # Read the data response
        data = res.read()
        # print("data:", data)

        # print(data.decode("utf-8"), type(data.decode("utf-8")))
        # pp(data.decode("utf-8"))

        # Return the data response in JSON
        return json.loads(data.decode("utf-8"))

    # def get_accounts(self):
    #     print(":get_accounts:")
    #
    #     # Get Accounts
    #     request_path = "/api/v3/brokerage/accounts"

    # def get_products(self):
    #     print(":get_products:")
    #
    #     # Get Products
    #     request_path = "/api/v3/brokerage/products"

    def list_and_get_portfolios(self):
        print(":list_and_get_portfolios:")

        request_method = "GET"

        # List Portfolios
        request_path = "/api/v3/brokerage/portfolios"

        headers = self.jwt_authorization_header(request_method, request_path)
        # print("headers:", headers)

        list_portfolios = self.cb_api_call(headers, request_method, request_path)
        print("list_portfolios", list_portfolios['portfolios'])
        # list_portfolios {'portfolios': [{'name': 'Default', 'uuid': '7456a543-d356-fioe-w343-4trjoas345is', 'type': 'DEFAULT', 'deleted': False}]}

        portfolio_uuid = list_portfolios['portfolios'][0]['uuid']
        print("portfolio_uuid", portfolio_uuid)

        # List Portfolios
        request_path = f"/api/v3/brokerage/portfolios/{portfolio_uuid}"

        headers = self.jwt_authorization_header(request_method, request_path)
        # print("headers:", headers)

        get_portfolio_breakdown = self.cb_api_call(headers, request_method, request_path)
        # print("get_portfolio_breakdown", get_portfolio_breakdown)

        for breakdown in get_portfolio_breakdown['breakdown']:
            # print("breakdown:", breakdown, get_portfolio_breakdown['breakdown'][breakdown])
            """
            breakdown: portfolio
            breakdown: portfolio_balances
            breakdown: spot_positions
            breakdown: perp_positions
            breakdown: futures_positions
            """
        # for portfolio in get_portfolio_breakdown['breakdown']['portfolio']:
        #     print("portfolio:", portfolio, get_portfolio_breakdown['breakdown']['portfolio'][portfolio])

        # for portfolio_balances in get_portfolio_breakdown['breakdown']['portfolio_balances']:
        #     # print(portfolio_balances, get_portfolio_breakdown['breakdown']['portfolio_balances'])
        #
        #     for balance in get_portfolio_breakdown['breakdown']['portfolio_balances'][portfolio_balances]:
        #         print(" ", portfolio_balances, balance, get_portfolio_breakdown['breakdown']['portfolio_balances'][portfolio_balances][balance])

        # for futures_positions in get_portfolio_breakdown['breakdown']['futures_positions']:
        #     # print(futures_positions)
        #     for position in futures_positions:
        #         print(" position:", position, futures_positions[position])

    def list_future_positions(self):
        print(":list_future_positions:")

        request_method = "GET"

        # List Futures Positions
        list_futures_pos_path = "/api/v3/brokerage/cfm/positions"

        headers = self.jwt_authorization_header(request_method, list_futures_pos_path)
        # print("headers:", headers)

        list_futures_positions = self.cb_api_call(headers, request_method, list_futures_pos_path)
        # print("list_futures_positions", list_futures_positions)

        # for future in list_futures_positions['positions']:
        #     # print("list future:", future)
        #     # print("list future product_id:", future['product_id'])
        #     print("list future expiration_time:", future['expiration_time'])
        #     print("list future number_of_contracts:", future['number_of_contracts'])
        #     print("list future side:", future['side'])
        #     print("list future current_price:", future['current_price'])
        #     print("list future avg_entry_price:", future['avg_entry_price'])
        #     print("list future unrealized_pnl:", future['unrealized_pnl'])
        #     print("list future number_of_contracts:", future['number_of_contracts'])
        #
        #     product_id = future['product_id']
        #     print("product_id:", product_id)
        #
        #     # Get Futures Position
        #     get_futures_pos_path = f"/api/v3/brokerage/cfm/positions/{product_id}"
        #     print("get_futures_pos_path:", get_futures_pos_path)
        #
        #     headers = self.jwt_authorization_header(request_method, get_futures_pos_path)
        #     get_futures_positions = self.cb_api_call(headers, request_method, get_futures_pos_path)
        #     print("get_futures_positions:", get_futures_positions)

        return list_futures_positions

    def get_future_positions(self):
        print(":get_future_positions:")

        request_method = "GET"

        # List Futures Positions
        list_futures_pos_path = "/api/v3/brokerage/cfm/positions"

        headers = self.jwt_authorization_header(request_method, list_futures_pos_path)
        # print("headers:", headers)

        list_futures_positions = self.cb_api_call(headers, request_method, list_futures_pos_path)
        # print("list_futures_positions", list_futures_positions)

        # for future in list_futures_positions['positions']:
        #     # print("list future:", future)
        #     # print("list future product_id:", future['product_id'])
        #     print("list future expiration_time:", future['expiration_time'])
        #     print("list future number_of_contracts:", future['number_of_contracts'])
        #     print("list future side:", future['side'])
        #     print("list future current_price:", future['current_price'])
        #     print("list future avg_entry_price:", future['avg_entry_price'])
        #     print("list future unrealized_pnl:", future['unrealized_pnl'])
        #     print("list future number_of_contracts:", future['number_of_contracts'])
        #
        #     product_id = future['product_id']
        #     print("product_id:", product_id)
        #
        #     # Get Futures Position
        #     get_futures_pos_path = f"/api/v3/brokerage/cfm/positions/{product_id}"
        #     print("get_futures_pos_path:", get_futures_pos_path)
        #
        #     headers = self.jwt_authorization_header(request_method, get_futures_pos_path)
        #     get_futures_positions = self.cb_api_call(headers, request_method, get_futures_pos_path)
        #     print("get_futures_positions:", get_futures_positions)

        return list_futures_positions

    def get_futures_balance_summary(self):
        print(":get_futures_balance_summary:")

        request_method = "GET"

        # Get Futures Balance Summary
        request_path = "/api/v3/brokerage/cfm/balance_summary"

        headers = self.jwt_authorization_header(request_method, request_path)
        # print("headers:", headers)

        balance_summary = self.cb_api_call(headers, request_method, request_path)
        # print("balance_summary", balance_summary)

        """
        Example:
        balance_summary {
            'balance_summary': {
                'futures_buying_power': {'value': '0.0', 'currency': 'USD'}, 
                'total_usd_balance': {'value': '0.0', 'currency': 'USD'}, 
                'cbi_usd_balance': {'value': '0.0', 'currency': 'USD'}, 
                'cfm_usd_balance': {'value': '0.0', 'currency': 'USD'}, 
                'total_open_orders_hold_amount': {'value': '0.0', 'currency': 'USD'}, 
                'unrealized_pnl': {'value': '0.0', 'currency': 'USD'}, 
                'daily_realized_pnl': {'value': '0', 'currency': 'USD'}, 
                'initial_margin': {'value': '0.0', 'currency': 'USD'}, 
                'available_margin': {'value': '0.0', 'currency': 'USD'}, 
                'liquidation_threshold': {'value': '0.0', 'currency': 'USD'}, 
                'liquidation_buffer_amount': {'value': '0.0', 'currency': 'USD'}, 
                'liquidation_buffer_percentage': '0.0'
            }
        }
        """

        return balance_summary

    def list_orders(self, p_product_id):
        print(":list_orders:")

        request_method = "GET"

        # List Orders
        # /orders/historical/batch?order_status=CANCELLED,EXPIRED

        # Keep this one simple for the headers JWT call
        request_path = "/api/v3/brokerage/orders/historical/batch"
        # print("request_path:", request_path)

        headers = self.jwt_authorization_header(request_method, request_path)
        # print("headers:", headers)

        url_query = "?"
        # url_query += "order_status=OPEN"
        url_query += "order_status=FILLED"
        # url_query += "&order_type=UNKNOWN_ORDER_TYPE"
        # url_query += "&side=UNKNOWN_ORDER_SIDE"
        url_query += "&product_id=" + p_product_id
        url_query += "&product_type=FUTURE"
        # url_query += "&order_placement_source=RETAIL_ADVANCED",
        # "retail_portfolio_id": "default"

        # Add all the options to the main API call
        request_path = "/api/v3/brokerage/orders/historical/batch" + url_query
        # /api/v3/brokerage/orders/historical/batch?product_id=BIT-26APR24-CD&order_side=BUY&product_type=FUTURE
        print("request_path:", request_path)

        get_orders = self.cb_api_call(headers, request_method, request_path)
        print("get_orders", get_orders)

        return get_orders

    def get_current_price(self, p_product_id):
        print(":get_current_price:")

    @staticmethod
    def generate_uuid4():
        return uuid.uuid4()

    def create_order(self, side, product_id, size):
        print(":create_order:")

        request_method = "POST"

        # Create Order
        request_path = "/api/v3/brokerage/orders"

        # client_order_id
        #   A unique ID provided by the client for their own identification purposes.
        #   This ID differs from the order_id generated for the order. If the ID provided is not unique,
        #   the order fails to be created and the order corresponding to that ID is returned.
        #   The client order id (client_oid) must be in UUID format which is generated by your trading application
        #   (for example: ef359184-6c68-4d34-9559-fcea14a7dad3). It can’t be in a string format. You will receive
        #   an “Invalid order id” error response if it’s not in UUID format. Also, please ensure you are copying
        #   your Client Order ID exactly as it is displayed.
        #   The client_oid will stay in the orders database and be associated with the order if the order doesn’t
        #   get canceled with zero fills.
        #   We don’t enforce or check for unique client_oid and it will be down to your implementation to make
        #   sure you are not repeating client_oid, if you do, you may encounter issues.

        # Fulfillment Policies
        #   Order type fulfillment policies (GTC, GTD, IOC, etc.) correspond to the time-in-force
        #   policy for that order type.
        #
        #   - Good Till Canceled (gtc): orders remain open on the book until canceled.
        #   - Good Till Date (gtd): orders are valid till a specified date or time.
        #   - Immediate Or Cancel (ioc): orders instantly cancel the remaining size of the
        #       limit order instead of opening it on the book.

        # Market Orders
        #   market_market_ioc
        # Limit Orders
        #   limit_limit_gtc
        #   limit_limit_gtd
        # Stop Orders
        #   stop_limit_stop_limit_gtc
        #   stop_limit_stop_limit_gtd

        headers = self.jwt_authorization_header(request_method, request_path)
        # print("headers:", headers)

        # A unique UUID that we make (should store and not repeat, must be in UUID format
        # Generate and print a UUID4
        client_order_id = self.generate_uuid4()
        print("Generated client_order_id:", client_order_id)

        payload = json.dumps({
            "client_order_id": str(client_order_id),
            "product_id": product_id,
            "side": side,
            "order_configuration": {
                "market_market_ioc": {
                    "quote_size": str(size)
                }
            },
            "leverage": "1.0"
        })
        pp(payload)

        # close_contract = cb_api_call(headers, request_method, request_path, payload)
        # print("close_contract", close_contract)

        return None

    def close_position(self, client_order_id, product_id, contract_size):
        print(":close_position:")
        """
        Closing Futures Positions
            When a contract expires, we automatically close your open position at the exchange 
            settlement price. You can also close your position before the contract expires 
            (for example, you may want to close your position if you’ve reached your 
            profit target, you want to prevent further losses, or you need to satisfy a margin requirement).
        
            There are two ways to close your futures position: (1) Close your position, 
            or (2) Create a separate trade to take the opposite position in the same 
            futures contract you are currently holding in your account. For example, 
            to close an open long position in the BTC 23 Feb 24 contract, place an order
            to sell the same number of BTC 23 Feb 24 contracts. If you were short to begin
            with, go long the same number of contracts to close your position.
        """
        request_method = "POST"

        # Close Position
        request_path = "/api/v3/brokerage/orders/close_position"

        headers = self.jwt_authorization_header(request_method, request_path)
        # print("headers:", headers)

        payload = json.dumps({
            "client_order_id": client_order_id,
            "product_id": product_id,
            "size": contract_size
        })

        # close_contract = self.cb_api_call(headers, request_method, request_path, payload)
        # print("close_contract", close_contract)


class TradeManager:

    def __init__(self, flask_app):
        print(":Initializing TradeManager:")
        self.flask_app = flask_app
        self.cb_adv_api = CoinbaseAdvAPI()

    def handle_aurox_signal(self, signal, product_id):
        print(":handle_aurox_signal:")

        if signal == 'long':
            print('Aurox Signal:', signal, product_id)
            # new_order = self.cb_adv_api.create_order("BUY", product_id, 1)
            # pp(new_order)

        elif signal == 'short':
            print('Aurox Signal:', signal, product_id)
            # new_order = self.cb_adv_api.create_order("SELL", product_id, 1)
            # pp(new_order)

        else:
            print('Aurox Signal TEST')

    def write_db_signal(self, data):
        print(":write_db_signal:")

        # Create a new AuroxSignal object from received data
        with self.flask_app.app_context():  # Push an application context
            try:
                new_signal = AuroxSignal(
                    timestamp=data['timestamp'],
                    price=data['price'].replace(',', ''),  # Remove commas for numeric processing if necessary
                    signal=data['signal'],
                    trading_pair=data['trading_pair'],
                    time_unit=data['timeUnit'],
                    message=data.get('message')  # Use .get for optional fields
                )

                # Add new_signal to the session and commit it
                db.session.add(new_signal)
                db.session.commit()

                print("New signal stored:", new_signal)

            except db_errors as e:
                print(f"Error fetching latest daily signal: {str(e)}")
                return None

    # def get_all_signals(self):
    #     print(":get_all_signals:")
    #     with self.flask_app.app_context():
    #         signals = AuroxSignal.query.all()
    #         return signals

    def get_latest_weekly_signal(self):
        print(":get_latest_weekly_signal:")
        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query\
                .filter(AuroxSignal.time_unit == '1 Week')\
                .order_by(AuroxSignal.timestamp.desc())\
                .first()
            return latest_signal

    def get_latest_daily_signal(self):
        print(":get_latest_daily_signal:")
        with (self.flask_app.app_context()):
            latest_signal = AuroxSignal.query\
                .filter(AuroxSignal.time_unit == '1 Day')\
                .order_by(AuroxSignal.timestamp.desc())\
                .first()
            return latest_signal


if __name__ == "__main__":

    cb_adv_api = CoinbaseAdvAPI()

    # get_bal_summary = cb_adv_api.get_futures_balance_summary()
    # pp(get_bal_summary)

    # list_future_positions = cb_adv_api.list_and_get_future_positions()
    # pp(list_future_positions)

    new_order = cb_adv_api.create_order("BUY", "BIT-26APR24-CDE", 1)
    pp(new_order)

    new_order = cb_adv_api.create_order("SELL", "BIT-26APR24-CDE", 1)
    pp(new_order)
