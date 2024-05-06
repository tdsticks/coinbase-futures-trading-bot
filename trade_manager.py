from coinbase.rest import RESTClient
from coinbase import jwt_generator
import configparser
import http.client
from coinbase.websocket import (WSClient, WSClientConnectionClosedException,
                                WSClientException)
from models.signals import AuroxSignal, FuturePriceAtSignal
from models.futures import (CoinbaseFuture, AccountBalanceSummary,
                            FuturePosition, FuturesOrder)
from db import db, db_errors, joinedload, and_, session
from dotenv import load_dotenv
from pprint import pprint as pp
from datetime import datetime, time, timedelta
import pytz
import os
import calendar
import uuid
import json
# import numpy as np
import pandas as pd

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
UUID = os.getenv('UUID')

config = configparser.ConfigParser()
config.read('bot_config.ini')
config.sections()


# print("UUID:", UUID)
# print("API_KEY:", API_KEY)

# NOTE: Aurox Ax Signal Guide
#   https://docs.getaurox.com/product-docs/aurox-terminal-guides/indicator-guides/
#       aurox-indicator/how-the-aurox-indicator-functions-part-1

# NOTE: Futures markets are open for trading from Sunday 6 PM to
#  Friday 5 PM ET (excluding observed holidays),
#  with a 1-hour break each day from 5 PM – 6 PM ET


class LogOrConsole:

    def __init__(self, flask_app):
        """
        Class to send messages to logging or console or both
        """
        self.flask_app = flask_app

    def log_or_console(self, log=True, level="I", subject=None, msg1=None, msg2=None):
        """
        Function to send messages to logging or console or both
        :param log: Send the messages to logging, enabled by default
        :param level: Set the logger level (D=DEBUG, I=INFO, W=WARNING, E=ERROR, C=CRITICAL)
        :param subject: Allows for a subject in the message
        :param msg1: First message
        :param msg2: Second message if we need it
        :return: None
        """

        # Function to ensure any type of msg is converted to string properly
        def to_string(msg):
            if isinstance(msg, str):
                return msg
            elif msg is None:
                return ''
            else:
                return str(msg)

        # Convert messages to string, safely handling non-string types
        msg1_str = to_string(msg1)
        msg2_str = to_string(msg2)

        # Combine messages
        entire_message = msg1_str
        if msg2_str:
            entire_message += " " + msg2_str

        # Prepend subject if it's provided
        if subject:
            entire_message = f"{subject}: {entire_message}"

        if log:
            if level == "D" and self.flask_app.config['DEBUG'] == 1:
                self.flask_app.logger.debug(entire_message)
            if level == "I":
                self.flask_app.logger.info(entire_message)
            if level == "W":
                self.flask_app.logger.warning(entire_message)
            if level == "E":
                self.flask_app.logger.error(entire_message)
            if level == "C":
                self.flask_app.logger.critical(entire_message)


class CoinbaseAdvAPI:

    def __init__(self, flask_app):
        # print(":Initializing CoinbaseAdvAPI:")
        self.flask_app = flask_app
        self.loc = LogOrConsole(flask_app)  # Send to Log or Console or both
        self.client = RESTClient(api_key=API_KEY, api_secret=API_SECRET)
        self.conn = http.client.HTTPSConnection("api.coinbase.com")
        self.loc.log_or_console(True, "D", None, ":Initializing CoinbaseAdvAPI:")
        # self.client.get_fills()

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
        # print(":cb_api_call:")

        # Check to see if we have a payload, otherwise assign it empty
        if payload_param is not None:
            payload = payload_param
        else:
            payload = ''
        # print("payload:", payload)

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

    @staticmethod
    def parse_datetime(date_str):
        """Parse an ISO 8601 datetime string to a formatted datetime string for SQLite."""
        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        return None

    def get_portfolios(self):
        # print(":get_portfolio_breakdown:")
        self.loc.log_or_console(True, "I", None, ":get_portfolio_breakdown:")

        get_portfolios = self.client.get_portfolios()
        # print("get_portfolios", get_portfolios)

        uuid = get_portfolios['portfolios'][0]['uuid']
        print("uuid", uuid)

        return uuid

    def get_portfolio_breakdown(self, portfolio_uuid):
        # print(":get_portfolio_breakdown:")
        self.loc.log_or_console(True, "I", None, ":get_portfolio_breakdown:")

        get_portfolio_breakdown = self.client.get_portfolio_breakdown(portfolio_uuid=portfolio_uuid)
        # print("get_portfolio_breakdown", get_portfolio_breakdown)
        self.loc.log_or_console(True, "I", "get_portfolio_breakdown", get_portfolio_breakdown)

        return

    def get_balance_summary(self):
        # print(":get_balance_summary:")

        balance_summary = self.client.get_futures_balance_summary()
        # pp(balance_summary)

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

    def store_futures_balance_summary(self, data):
        # print(':store_futures_balance_summary:')
        self.loc.log_or_console(True, "D", None,
                                ":store_futures_balance_summary:")

        balance_summary_data = data['balance_summary']
        # pp(balance_summary_data)

        with self.flask_app.app_context():  # Push an application context
            try:
                # Try to find the existing balance summary, assuming only one record exists
                existing_balance_summary = AccountBalanceSummary.query.limit(1).all()
                # print("existing_balance_summary:", existing_balance_summary)

                if existing_balance_summary:
                    # Update existing record
                    existing_balance_summary[0].available_margin = float(
                        balance_summary_data['available_margin']['value'])
                    existing_balance_summary[0].cbi_usd_balance = float(
                        balance_summary_data['cbi_usd_balance']['value'])
                    existing_balance_summary[0].cfm_usd_balance = float(
                        balance_summary_data['cfm_usd_balance']['value'])
                    existing_balance_summary[0].daily_realized_pnl = float(
                        balance_summary_data['daily_realized_pnl']['value'])
                    existing_balance_summary[0].futures_buying_power = float(
                        balance_summary_data['futures_buying_power']['value'])
                    existing_balance_summary[0].initial_margin = float(balance_summary_data['initial_margin']['value'])
                    existing_balance_summary[0].liquidation_buffer_amount = float(
                        balance_summary_data['liquidation_buffer_amount']['value'])
                    existing_balance_summary[0].liquidation_buffer_percentage = int(
                        balance_summary_data['liquidation_buffer_percentage'])
                    existing_balance_summary[0].liquidation_threshold = float(
                        balance_summary_data['liquidation_threshold']['value'])
                    existing_balance_summary[0].total_open_orders_hold_amount = float(
                        balance_summary_data['total_open_orders_hold_amount']['value'])
                    existing_balance_summary[0].total_usd_balance = float(
                        balance_summary_data['total_usd_balance']['value'])
                    existing_balance_summary[0].unrealized_pnl = float(balance_summary_data['unrealized_pnl']['value'])
                    # print("Updated existing balance summary")
                else:
                    # Create new record if it does not exist
                    new_balance_summary = AccountBalanceSummary(
                        available_margin=float(balance_summary_data['available_margin']['value']),
                        cbi_usd_balance=float(balance_summary_data['cbi_usd_balance']['value']),
                        cfm_usd_balance=float(balance_summary_data['cfm_usd_balance']['value']),
                        daily_realized_pnl=float(balance_summary_data['daily_realized_pnl']['value']),
                        futures_buying_power=float(balance_summary_data['futures_buying_power']['value']),
                        initial_margin=float(balance_summary_data['initial_margin']['value']),
                        liquidation_buffer_amount=float(balance_summary_data['liquidation_buffer_amount']['value']),
                        liquidation_buffer_percentage=int(balance_summary_data['liquidation_buffer_percentage']),
                        liquidation_threshold=float(balance_summary_data['liquidation_threshold']['value']),
                        total_open_orders_hold_amount=float(
                            balance_summary_data['total_open_orders_hold_amount']['value']),
                        total_usd_balance=float(balance_summary_data['total_usd_balance']['value']),
                        unrealized_pnl=float(balance_summary_data['unrealized_pnl']['value']),
                    )
                    db.session.add(new_balance_summary)
                    # print("Stored new balance summary")

                # Commit the changes to the database
                db.session.commit()
                # print("Balance summary updated or created successfully.")
            except Exception as e:
                self.loc.log_or_console(True, "E",
                                        "Failed to add/update balance summary",
                                        balance_summary_data, e)
                db.session.rollback()
        # print("Balance summary stored")

    def get_product(self, product_id="BTC-USDT"):
        # print(":get_product:")
        # self.loc.log_or_console(True, "D", None, ":get_product:")

        get_product = self.client.get_product(product_id=product_id)
        # print("get_product:", get_product)
        # self.loc.log_or_console(True, "I", "get_product", get_product)

        return get_product

    def list_products(self, product_type="FUTURE"):
        # print(":list_products:")
        # self.loc.log_or_console(True, "D", None, ":list_products:")

        get_products = self.client.get_products(product_type=product_type)
        # print("get_products:", get_products)
        # self.loc.log_or_console(True, "I", "get_products", get_products)

        return get_products

    def store_btc_futures_products(self, future_products):
        # print(":store_btc_futures_products:")
        # self.loc.log_or_console(True, "D", None, ":store_btc_futures_products:")
        # print("future_products:", future_products, type(future_products))

        for future in future_products['products']:
            # print("future product:", future)
            if 'BTC' in future['future_product_details']['contract_root_unit']:
                # print("future product:", future)

                with self.flask_app.app_context():  # Push an application context
                    try:
                        # Convert necessary fields
                        product_id = future['product_id']
                        price = float(future['price']) if future['price'] else None
                        price_change_24h = float(future['price_percentage_change_24h']) if future[
                            'price_percentage_change_24h'] else None
                        volume_24h = float(future['volume_24h']) if future['volume_24h'] else None
                        volume_change_24h = float(future['volume_percentage_change_24h']) if future[
                            'volume_percentage_change_24h'] else None
                        contract_expiry = datetime.strptime(
                            future['future_product_details']['contract_expiry'], "%Y-%m-%dT%H:%M:%SZ")
                        contract_size = float(future['future_product_details']['contract_size'])

                        # Check if the future product already exists in the database
                        future_entry = CoinbaseFuture.query.filter_by(product_id=product_id).first()
                        # print("\nfound future_entry:", future_entry)

                        # If it doesn't exist, create the new record using just product_id
                        if not future_entry:
                            # print("\nno future entry found, adding it")
                            future_entry = CoinbaseFuture(product_id=future['product_id'])
                            db.session.add(future_entry)

                        # Set or update all fields
                        future_entry.price = price
                        future_entry.price_change_24h = price_change_24h
                        future_entry.volume_24h = volume_24h
                        future_entry.volume_change_24h = volume_change_24h
                        future_entry.display_name = future['display_name']
                        future_entry.product_type = future['product_type']
                        future_entry.contract_expiry = contract_expiry
                        future_entry.contract_size = contract_size
                        future_entry.contract_root_unit = future['future_product_details']['contract_root_unit']
                        future_entry.venue = future['future_product_details']['venue']
                        future_entry.status = future['status']
                        future_entry.trading_disabled = future['trading_disabled']

                        db.session.commit()
                    except Exception as e:
                        # print(f"Failed to add future product {future['product_id']}: {e}")
                        self.loc.log_or_console(True, "E",
                                                "Failed to add future product",
                                                future['product_id'],
                                                e)
                        db.session.rollback()

    @staticmethod
    def get_current_short_month_uppercase():
        # Get the current datetime
        current_date = datetime.now()

        # Format the month to short format and convert it to uppercase
        short_month = current_date.strftime('%b').upper()
        return short_month

    @staticmethod
    def get_next_short_month_uppercase():
        # Get the current datetime
        current_date = datetime.now()

        # Determine the month and handle year rollover
        year = current_date.year + (current_date.month // 12)
        next_month = (current_date.month % 12) + 1
        next_short_month = calendar.month_abbr[next_month].upper()
        return next_short_month

    def get_relevant_future_from_db(self, month_override=None):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_relevant_future_from_db:")

        # Find this months future product
        with self.flask_app.app_context():

            # Get the current month's short name in uppercase
            short_month = self.get_current_short_month_uppercase()

            if month_override:
                short_month = month_override

            # print(f"Searching for futures contracts for the month: {short_month}")
            self.loc.log_or_console(True, "I",
                                    "   Searching for futures contracts for the month", short_month)

            # Search the database for a matching futures contract
            future_contract = CoinbaseFuture.query.filter(
                CoinbaseFuture.display_name.contains(short_month)
            ).first()

            if future_contract:
                # print("\nFound future entry:", future_entry)
                self.loc.log_or_console(True, "I",
                                        "       Found future contract", future_contract.product_id)
                return future_contract
            else:
                # print("\n   No future entry found for this month.")
                self.loc.log_or_console(True, "W",
                                        None, " >>> No future contract found for this month.")
                return None

    def list_future_positions(self):
        self.loc.log_or_console(True, "D", None,
                                ":list_future_positions:")

        list_futures_positions = self.client.list_futures_positions()
        # pp(list_futures_positions)

        return list_futures_positions

    def get_future_position(self, product_id: str):
        self.loc.log_or_console(True, "D", None,
                                ":get_future_position:")

        get_futures_positions = self.client.get_futures_position(product_id=product_id)
        # pp(get_futures_positions)

        return get_futures_positions

    def store_future_positions(self, p_list_futures_positions):
        self.loc.log_or_console(True, "D", None,
                                ":store_future_positions:")
        # pp(p_list_futures_positions)

        # Clear existing positions
        with (self.flask_app.app_context()):  # Push an application context
            try:
                if p_list_futures_positions and 'positions' in p_list_futures_positions:
                    # Clear existing positions
                    db.session.query(FuturePosition).delete()

                    for future in p_list_futures_positions['positions']:
                        new_position = FuturePosition(
                            product_id=future['product_id'],
                            # creation_origin=creation_origin,
                            expiration_time=datetime.strptime(future['expiration_time'], "%Y-%m-%dT%H:%M:%SZ"),
                            side=future['side'],
                            number_of_contracts=int(future['number_of_contracts']),
                            current_price=float(future['current_price']),
                            avg_entry_price=float(future['avg_entry_price']),
                            unrealized_pnl=float(future['unrealized_pnl']),
                            daily_realized_pnl=float(future.get('daily_realized_pnl', 0))  # Handle optional fields
                        )
                        db.session.add(new_position)
                    db.session.commit()
                    self.loc.log_or_console(True, "I", None,
                                            "   Future position updated")
            except db_errors as e:
                db.session.rollback()
                self.loc.log_or_console(True, "E", "Error storing future position", e)
            except ValueError as e:
                db.session.rollback()
                self.loc.log_or_console(True, "E", "Data conversion error", e)
            except Exception as e:
                db.session.rollback()
                self.loc.log_or_console(True, "E", "Unexpected error", e)

    def get_current_bid_ask_prices(self, product_id):
        # self.loc.log_or_console(True, "D", None, ":get_current_bid_ask_prices:")

        get_bid_ask = self.client.get_best_bid_ask(product_ids=product_id)
        # print("get_bid_ask", get_bid_ask)

        return get_bid_ask

    def get_current_average_price(self, product_id):
        # self.loc.log_or_console(True, "D", None, ":get_current_future_price:")

        # Get Current Bid Ask Prices
        cur_future_bid_ask_price = self.get_current_bid_ask_prices(product_id)
        cur_future_bid_price = cur_future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
        cur_future_ask_price = cur_future_bid_ask_price['pricebooks'][0]['asks'][0]['price']
        cur_prices_msg = (f"    Prd: {product_id} - "
                          f"Current Futures: Bid: ${cur_future_bid_price} "
                          f"Ask: ${cur_future_ask_price}")
        self.loc.log_or_console(True, "I", None, cur_prices_msg)

        cur_future_avg_price = (int(cur_future_bid_price) + int(cur_future_ask_price)) / 2
        # self.loc.log_or_console(True, "I",
        #                         "   Current Future Avg Price", cur_future_avg_price)

        return cur_future_bid_price, cur_future_ask_price, cur_future_avg_price

    @staticmethod
    def generate_uuid4():
        return uuid.uuid4()

    @staticmethod
    def adjust_price_to_nearest_increment(price, increment=5):
        # Round the price to the nearest increment
        return str(round(price / increment) * increment)

    def create_order(self, side: str, product_id: str, size: str, bot_note: str,
                     limit_price: str = None, leverage: str = "3",
                     order_type: str = 'limit_limit_gtc'):
        self.loc.log_or_console(True, "D", "create_order")
        # print(f"    order_type: {order_type} "
        #       f"side: {side}, "
        #       f"product_id: {product_id}, "
        #       f"size: {size}, "
        #       f"leverage: {leverage}")

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

        # Limit Price
        # Needs to be string with no decimals

        # quote_size
        # Amount of quote currency to spend on order. Required for BUY orders.

        # base_size
        # Amount of base currency to spend on order. Required for SELL orders.

        # limit_price
        # Ceiling price for which the order should get filled.

        order_created = {}
        enable_live_trading = config['trade.conditions']['enable_live_trading']
        self.loc.log_or_console(True, "D", "enable_live_trading", enable_live_trading)

        # Live trading enabled
        if enable_live_trading:

            # NOTE: A unique UUID that we make (should store and not repeat, must be in UUID format
            # Generate and print a UUID4
            client_order_id = self.generate_uuid4()
            # print("Generated client_order_id:", client_order_id, type(client_order_id))

            # Convert UUID to a string
            client_order_id_str = str(client_order_id)
            # print("Client Order ID as string:", client_order_id_str)

            quote_size = ''
            base_size = ''
            post_only = False
            order_type_db_record = 'MARKET'  # Default
            creation_origin = 'bot_order'

            if order_type == 'limit_limit_gtc':
                base_size = str(size)
                order_type_db_record = 'LIMIT'
            # elif order_type == 'market_market_ioc':
            #     order_type_db_record = 'MARKET'
            #     if side == "BUY":
            #         quote_size = str(size)
            #     elif side == "SELL":
            #         base_size = str(size)
            # print("order_configuration:")
            # pp(order_configuration)

            pre_order_for_storing = {
                "order_id": None,
                "product_id": product_id,
                "side": side,
                "client_order_id": client_order_id_str,
                "success": False,
                "failure_reason": None,
                "error_message": None,
                "error_details": None,
                "order_type": order_type_db_record,
                "creation_origin": creation_origin,
                "bot_note": bot_note,
                "bot_active": 1,
                "quote_size": quote_size,
                "base_size": base_size,
                "limit_price": limit_price,
                "leverage": leverage,
                "post_only": post_only,
                "end_time": None
            }
            # print("pre_order_for_storing:")
            # pp(pre_order_for_storing)

            self.store_order(pre_order_for_storing)

            if side == "BUY" and order_type == 'limit_limit_gtc':
                order_created = self.client.limit_order_gtc_buy(client_order_id=client_order_id_str,
                                                                product_id=product_id,
                                                                base_size=base_size,
                                                                # leverage=leverage,
                                                                limit_price=limit_price)

            elif side == "SELL" and order_type == 'limit_limit_gtc':
                order_created = self.client.limit_order_gtc_sell(client_order_id=client_order_id_str,
                                                                 product_id=product_id,
                                                                 base_size=base_size,
                                                                 # leverage=leverage,
                                                                 limit_price=limit_price)

            # elif side == "BUY" and order_type == 'market_market_ioc':
            #     order_created = self.client.market_order_buy(client_order_id=client_order_id_str,
            #                                                  product_id=product_id,
            #                                                  # leverage=leverage,
            #                                                  quote_size=quote_size)
            #
            # elif side == "SELL" and order_type == 'market_market_ioc':
            #     order_created = self.client.market_order_sell(client_order_id=client_order_id_str,
            #                                                   product_id=product_id,
            #                                                   # leverage=leverage,
            #                                                   base_size=base_size)
            # print(f"\norder_created: bot_note: {bot_note}")
            # pp(order_created)

            if order_created.get('success'):
                self.loc.log_or_console(True, "I", "Order successfully created")
                self.loc.log_or_console(True, "D", None, order_created.get('success_response'))

            if order_created.get('failure_reason'):
                self.loc.log_or_console(True, "I", "Order creation failed")
                self.loc.log_or_console(True, "D", None, order_created.get('failure_reason'))

                if order_created.get('error_response'):
                    self.loc.log_or_console(True, "E", "Error Message",
                                            order_created.get('error_response').get('message'))
                    self.loc.log_or_console(True, "E", "Error Details",
                                            order_created.get('error_response').get('error_details'))
                else:
                    self.loc.log_or_console(True, "D", "No detailed error message provided.")

            post_order_for_storing = {
                "order_id": order_created['order_id'],
                "product_id": product_id,
                "side": side,
                "client_order_id": client_order_id_str,
                "success": order_created['success'],
                "order_type": order_type_db_record,
                "creation_origin": creation_origin,
                "bot_note": bot_note,
                "bot_active": 1,
                "quote_size": quote_size,
                "base_size": base_size,
                "limit_price": limit_price,
                "leverage": leverage,
                "post_only": post_only
            }

            if "failure_reason" in order_created:
                post_order_for_storing["failure_reason"] = order_created['failure_reason']
            else:
                post_order_for_storing["failure_reason"] = None

            if "error_message" in order_created:
                post_order_for_storing["error_message"] = order_created['error_message']
            else:
                post_order_for_storing["error_message"] = None

            if "error_details" in order_created:
                post_order_for_storing["error_details"] = order_created['error_details']
            else:
                post_order_for_storing["error_details"] = None

            if "end_time" in order_created:
                post_order_for_storing["end_time"] = order_created['end_time']
            else:
                post_order_for_storing["end_time"] = None
            # print("post_order_for_storing:")
            # pp(post_order_for_storing)

            self.store_order(post_order_for_storing)
            # print("Order Created and Store in the DB")
        else:
            self.loc.log_or_console(True, "D", "Live Trading Disabled")

        return order_created

    def list_orders(self, product_id, order_status, product_type="FUTURE"):
        # print(":list_orders:")

        # MARKET: A market order
        # LIMIT: A limit order
        # order_type

        # order_status: Optional[List[str]] = None,
        list_orders = self.client.list_orders(order_status=order_status,
                                              product_id=product_id, product_type=product_type)
        return list_orders

    def get_order(self, order_id: str):
        # print("\n:get_order:")
        # print("order_id:", order_id, type(order_id))

        get_order = self.client.get_order(order_id=order_id)
        # print(" get_order:", get_order)

        return get_order

    def get_current_take_profit_order_from_db(self, order_status: str, side: str,
                                              bot_note: str, get_all_orders=False):
        # self.loc.log_or_console(True, "I", None, "get_current_take_profit_order_from_db")

        open_futures = None

        # NOTE: We should only get one if we're only trading one future (BTC)

        with self.flask_app.app_context():  # Push an application context
            try:

                if get_all_orders:
                    # Search the database for a matching futures contract
                    open_futures = FuturesOrder.query.filter(
                        and_(
                            FuturesOrder.order_status == order_status,
                            FuturesOrder.creation_origin == "bot_order",
                            FuturesOrder.bot_note == bot_note,
                            FuturesOrder.bot_active == 1,
                            FuturesOrder.side == side
                        )
                    ).all()
                    # self.loc.log_or_console(True, "I",
                    #                         "open_futures", open_futures)
                else:
                    # Search the database for a matching futures contract
                    open_futures = FuturesOrder.query.filter(
                        and_(
                            FuturesOrder.order_status == order_status,
                            FuturesOrder.creation_origin == "bot_order",
                            FuturesOrder.bot_note == bot_note,
                            FuturesOrder.bot_active == 1,
                            FuturesOrder.side == side
                        )
                    ).first()
                    # self.loc.log_or_console(True, "I", "open_futures", open_futures)

                return open_futures
            except Exception as e:
                self.loc.log_or_console(True, "E",
                                        "Database error getting", msg1=e)
        # print("open_futures:", open_futures)
        return open_futures

    def get_dca_filled_orders_from_db(self, dca_side: str):
        # self.loc.log_or_console(True, "I", None,
        #                         "get_dca_filled_orders_from_db")
        dca_avg_filled_price = 0
        dca_avg_filled_price_2 = 0
        dca_count = 1  # This includes the MAIN initial order

        quantity = int(config['dca.ladder.trade_percentages']['ladder_quantity'])
        # self.loc.log_or_console(True, "I", "    quantity", quantity)

        # dca_note_list = ['DCA1', 'DCA2', 'DCA3', 'DCA4', 'DCA5']
        dca_note_list = ["DCA" + str(x) for x in range(1, quantity + 1)]
        # self.loc.log_or_console(True, "I", "    dca_note_list", dca_note_list)

        for i, dca in enumerate(dca_note_list):
            # print("dca_note_list - i:", i)
            dca_order = self.get_current_take_profit_order_from_db(order_status="FILLED",
                                                                   side=dca_side, bot_note=dca)
            if dca_order:
                # self.loc.log_or_console(True, "I", "dca_order", dca_order)
                # self.loc.log_or_console(True, "I", "    dca_order.limit_price", dca_order.limit_price)
                # self.loc.log_or_console(True, "I", "    dca_order.average_filled_price", dca_order.average_filled_price)

                dca_contract_num_str = f"dca_trade_{str(i + 1)}_contracts"
                # print("dca_contract_num_str:", dca_contract_num_str)

                current_pos_contract_size = int(config['dca.ladder.trade_percentages'][dca_contract_num_str])
                # print("current_pos_contract_size:", current_pos_contract_size)

                dca_count += 1
                dca_avg_filled_price += round(int(dca_order.average_filled_price))
                dca_avg_filled_price_2 += round(int(dca_order.average_filled_price) * current_pos_contract_size)

        # print("dca_avg_filled_price:", dca_avg_filled_price)
        # print("dca_avg_filled_price_2:", dca_avg_filled_price_2)
        return dca_avg_filled_price, dca_avg_filled_price_2, dca_count

    def cancel_order(self, order_ids: list):
        self.loc.log_or_console(True, "D", "cancel_order")
        # self.loc.log_or_console(True, "I", "    order_ids", order_ids)

        cancelled_order = None
        if len(order_ids) > 0:
            cancelled_order = self.client.cancel_orders(order_ids=order_ids)
            # self.loc.log_or_console(True, "I", "cancelled_order", cancelled_order)
        else:
            pass
            # self.loc.log_or_console(True, "W", " !!! No order ids to cancel")
        return cancelled_order

    def update_cancelled_orders(self):
        self.loc.log_or_console(True, "I",
                                None, "update_cancelled_orders")

        with self.flask_app.app_context():  # Push an application context
            try:
                # Search the database for a matching futures contract
                cancelled_futures = FuturesOrder.query.filter(
                    and_(
                        FuturesOrder.order_status == 'CANCELLED',
                        FuturesOrder.creation_origin == "bot_order",
                        FuturesOrder.bot_active == 1,
                    )
                ).all()
                # self.loc.log_or_console(True, "I",
                #                         "cancelled_futures", cancelled_futures)

                # If we have cancelled futures, update the bot_active
                if cancelled_futures:
                    for cancelled_future in cancelled_futures:
                        field_values = {
                            "bot_active": 0
                        }
                        # Update order so we don't the system doesn't try
                        # to use it for future orders
                        updated_cancelled_order = self.update_order_fields(
                            client_order_id=cancelled_future.client_order_id,
                            field_values=field_values)
                        self.loc.log_or_console(True, "I",
                                                "updated_cancelled_order",
                                                updated_cancelled_order)
            except Exception as e:
                self.loc.log_or_console(True, "E",
                                        "Database error getting", msg1=e)

    def update_bot_active_orders(self):
        self.loc.log_or_console(True, "I",
                                None, "update_bot_active_orders")

        with self.flask_app.app_context():  # Push an application context
            try:
                # Search the database for a matching futures contract
                bot_active_orders = FuturesOrder.query.filter(
                    and_(
                        FuturesOrder.creation_origin == "bot_order",
                        FuturesOrder.bot_active == 1,
                    )
                ).all()
                self.loc.log_or_console(True, "I",
                                        "bot_active_orders", bot_active_orders)

                # If we have cancelled futures, update the bot_active
                if bot_active_orders:
                    for bot_active_order in bot_active_orders:
                        field_values = {
                            "bot_active": 0
                        }
                        # Update order so we don't the system doesn't try
                        # to use it for future orders
                        updated_bot_active_order = self.update_order_fields(
                            client_order_id=bot_active_order.client_order_id,
                            field_values=field_values)
                        self.loc.log_or_console(True, "I",
                                                "updated_bot_active_order",
                                                updated_bot_active_order)
            except Exception as e:
                self.loc.log_or_console(True, "E",
                                        "Database error getting", msg1=e)

    def edit_order(self, order_id, size=None, price=None):
        print("\n:edit_order:")
        # print("order_id:", order_id, type(order_id))
        # print("size:", size, type(size))
        # print("price:", price, type(price))

        order_edited = self.client.edit_order(order_id=order_id, size=size, price=price)
        # print(" order_edited:", order_edited)

        # TODO: Try using the JWT API call for this

        # request_method = "POST"

        # # Edit Order
        # request_path = f"/api/v3/brokerage/orders/edit"
        # headers = self.jwt_authorization_header(request_method, request_path)
        #
        # payload = json.dumps({
        #     "price": price,
        #     "size": size,
        #     "order_id": order_id
        # })
        # print("payload:")
        # pp(payload)
        #
        # edit_order_request_path = f"/api/v3/brokerage/orders/edit"
        # edit_order = self.cb_api_call(headers, request_method, edit_order_request_path, payload)
        # print("edit_order:", edit_order)

        # def get_order(self, order_id: str, **kwargs) -> Dict[str, Any]:
        #     """
        #     **Get Order**

        # get_order = self.client.get_order(order_id=order_id)
        # pp(get_order)

        # preview_edit_order = self.client.preview_edit_order(order_id=order_id, size=size, price=price)
        # print(" preview_edit_order:", preview_edit_order)

        # post_order_edit_for_storing = {
        #         "order_id": order_edited['order_id'],
        #         "product_id": order_edited['product_id'],
        #         "side": order_edited['side'],
        #         "client_order_id": order_edited['client_order_id'],
        #         "success": order_edited['success'],
        #         "order_type": order_edited['order_type'],
        #         "quote_size": order_edited['quote_size'],
        #         "base_size": order_edited['base_size'],
        #         "limit_price": order_edited['limit_price'],
        #         "leverage": order_edited['leverage'],
        #         "post_only": order_edited['post_only']
        #     }
        # pp(post_order_edit_for_storing)

        # self.store_order(post_order_edit_for_storing)

    def store_order(self, order_data):
        self.loc.log_or_console(True, "D", None, ":store_order:")
        # self.loc.log_or_console(True, "I", "order_data", order_data)

        with self.flask_app.app_context():  # Push an application context
            try:
                client_order_id = order_data['client_order_id']
                # print(" client_order_id:", client_order_id)

                if client_order_id:
                    # Query for an existing order
                    order = FuturesOrder.query.filter_by(client_order_id=client_order_id).first()
                    # print(" found order:", order)

                    if order:
                        # Order exists, update its details
                        order.order_id = order_data['order_id']
                        order.product_id = order_data['product_id']
                        order.order_type = order_data["order_type"]
                        order.creation_origin = order_data["creation_origin"]
                        order.bot_note = order_data['bot_note']
                        order.bot_active = order_data['bot_active']
                        order.side = order_data['side']
                        order.quote_size = order_data["quote_size"]
                        order.base_size = order_data["base_size"]
                        order.limit_price = order_data["limit_price"]
                        order.leverage = order_data["leverage"]
                        order.success = order_data['success']
                        order.failure_reason = order_data['failure_reason']
                        order.error_message = order_data['error_message']
                        order.error_details = order_data['error_details']
                        order.post_only = order_data["post_only"]
                        order.end_time = order_data["end_time"]
                    else:
                        # No existing order, create a new one
                        order = FuturesOrder(
                            product_id=order_data['product_id'],
                            client_order_id=order_data['client_order_id'],
                            order_type=order_data["order_type"],
                            creation_origin=order_data["creation_origin"],
                            bot_note=order_data["bot_note"],
                            bot_active=order_data['bot_active'],
                            side=order_data["side"],
                            quote_size=order_data["quote_size"],
                            base_size=order_data["base_size"],
                            limit_price=order_data["limit_price"],
                            leverage=order_data["leverage"],
                            success=order_data["success"],
                            failure_reason=order_data["failure_reason"],
                            error_message=order_data["error_message"],
                            error_details=order_data["error_details"],
                            post_only=order_data["post_only"],
                            end_time=order_data["end_time"]
                        )
                        db.session.add(order)

                    # Commit changes or new entry to the database
                    db.session.commit()

                    order_stored = f"    Order Client ID:{client_order_id} processed: {'updated' if order.id else 'created'}"
                    self.loc.log_or_console(True, "I", None, order_stored)
                else:
                    self.loc.log_or_console(True, "I", None,
                                            " No order ID provided or order creation failed. Check input data.")
            except db_errors as e:
                self.loc.log_or_console(True, "I",
                                        "    Error either getting or storing the Order record",
                                        str(e))
                db.session.rollback()
                return None

    def store_or_update_orders_from_api(self, orders_data):
        # self.loc.log_or_console(True, "D", None, ":store_or_update_orders_from_api:")

        for order in orders_data['orders']:
            # pp(order)

            with self.flask_app.app_context():  # Ensure you're within the Flask app context
                # Try to find an existing order by order_id
                existing_order = FuturesOrder.query.filter_by(order_id=order.get('order_id')).first()
                # self.loc.log_or_console(True, "I", "existing order", existing_order)

                if existing_order:
                    pass
                    # print("\nUpdating existing order:", existing_order.order_id)
                else:
                    # print("\nCreating new order with order_id:", order.get('order_id'))
                    existing_order = FuturesOrder()  # Create a new instance if not found
                    db.session.add(existing_order)
                # pp(order)

                # Update or set fields from order_data
                existing_order.order_id = order.get('order_id')
                existing_order.client_order_id = order.get('client_order_id')
                existing_order.product_id = order.get('product_id')
                existing_order.product_type = order.get('product_type')
                existing_order.order_type = order.get('order_type')
                existing_order.order_status = order.get('status')
                existing_order.time_in_force = order.get('time_in_force')
                existing_order.order_placement_source = order.get('order_placement_source')
                existing_order.side = order.get('side')

                for order_config in order.get('order_configuration'):
                    order_type = order.get('order_configuration')[order_config]
                    existing_order.limit_price = order_type.get('limit_price')
                    existing_order.base_size = order_type.get('base_size')
                    existing_order.post_only = order_type.get('post_only')

                existing_order.leverage = order.get('leverage')
                existing_order.margin_type = order.get('margin_type')
                existing_order.is_liquidation = order.get('is_liquidation')
                existing_order.quote_size = order.get('quote_size')
                existing_order.size_in_quote = order.get('size_in_quote')
                existing_order.size_inclusive_of_fees = order.get('size_inclusive_of_fees')
                existing_order.number_of_fills = order.get('number_of_fills')
                existing_order.filled_size = order.get('filled_size')
                existing_order.filled_value = order.get('filled_value')
                existing_order.average_filled_price = order.get('average_filled_price')
                existing_order.completion_percentage = order.get('completion_percentage')
                existing_order.fee = order.get('fee')
                existing_order.total_fees = order.get('total_fees')
                existing_order.total_value_after_fees = order.get('total_value_after_fees')
                existing_order.outstanding_hold_amount = order.get('outstanding_hold_amount')
                existing_order.success = order.get('success', False)
                existing_order.settled = order.get('settled')

                edit_history = order.get('edit_history', False)
                if edit_history:
                    edit_history_str = ",".join(str(element) for element in edit_history)
                else:
                    edit_history_str = ''
                existing_order.edit_history = edit_history_str
                existing_order.cancel_message = order.get('cancel_message')
                existing_order.pending_cancel = order.get('pending_cancel')
                existing_order.reject_message = order.get('reject_message')
                existing_order.reject_reason = order.get('reject_reason')
                existing_order.failure_reason = order.get('failure_reason')
                existing_order.error_message = order.get('error_message')
                existing_order.error_details = order.get('error_details')
                existing_order.end_time = self.parse_datetime(order.get('end_time'))
                existing_order.created_time = self.parse_datetime(order.get('created_time'))
                existing_order.last_fill_time = self.parse_datetime(order.get('last_fill_time'))
                existing_order.trigger_status = order.get('trigger_status')

                # Commit changes to the database
                try:
                    db.session.commit()
                    # print("Order stored or updated successfully.")
                except Exception as e:
                    db.session.rollback()
                    self.loc.log_or_console(True, "E",
                                            "Failed to store or update order", (e))

    def update_order_fields(self, client_order_id: str, field_values: dict = None):
        self.loc.log_or_console(True, "D", None, ":update_order_fields:")
        # self.loc.log_or_console(True, "I", "field_values", field_values)

        with self.flask_app.app_context():  # Push an application context
            try:
                if client_order_id:
                    # Query for an existing order
                    order = FuturesOrder.query.filter_by(client_order_id=client_order_id).first()
                    self.loc.log_or_console(True, "I", "    found order", order)

                    if order and field_values:
                        # Order exists, update its details
                        for field, value in field_values.items():
                            # self.loc.log_or_console(True, "I", "field", field)
                            # self.loc.log_or_console(True, "I", "value", value)

                            # Set the order field with the value
                            # Dynamically set the attribute based on field name
                            setattr(order, field, value)

                        # Commit changes or new entry to the database
                        db.session.commit()
                        self.loc.log_or_console(True, "I", "Order Client ID",
                                                client_order_id, "  field values updated")

                        return "    Successfully updated order record"
                else:
                    self.loc.log_or_console(True, "W", None,
                                            "No Client Order ID provided or order creation failed. Check input data.")
                    return f"   No Client Order ID provided client_order_id: {client_order_id}"
            except db_errors as e:
                self.loc.log_or_console(True, "E",
                                        "    Error either getting or storing the Order record",
                                        str(e))
                db.session.rollback()
                return "    update_order_fields - Database Error"

    def close_position(self, client_order_id, product_id, contract_size):
        self.loc.log_or_console(True, "I", None, ":close_position:")
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
        close_position = self.client.close_position(client_order_id=client_order_id,
                                                    product_id=product_id,
                                                    size=contract_size)
        self.loc.log_or_console(True, "I", "close", close_position)

        return close_position


class TradeManager:

    def __init__(self, flask_app):
        # print(":Initializing TradeManager:")
        self.flask_app = flask_app
        self.loc = LogOrConsole(flask_app)  # Send to Log or Console or both
        self.cb_adv_api = CoinbaseAdvAPI(flask_app)

        self.loc.log_or_console(True, "D", None, ":Initializing TradeManager:")

    def write_db_signal(self, data):
        self.loc.log_or_console(True, "I", None, ":write_db_signal:")

        # TODO: May need to convert these timestamps from Aurox as they're in ISO format

        # Create a new AuroxSignal object from received data
        # Also write a record using the signal spot price, futures bid and ask
        #   and store the relationship ids to both
        with self.flask_app.app_context():  # Push an application context
            try:
                # BUG: Still having issues with not storing duplicates from Aurox webhook

                # Convert timestamp to datetime object if necessary
                # timestamp = data['timestamp']
                timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
                timestamp = timestamp.replace(tzinfo=pytz.utc)
                # self.loc.log_or_console(True, "I", "timestamp", timestamp)

                signal_spot_price = data['price'].replace(',', '')

                # Define a unique key combination for updating or inserting signals
                unique_key = {
                    'trading_pair': data['trading_pair'],
                    'time_unit': data['timeUnit']
                }

                # Attempt to find an existing signal with the same trading pair and time unit
                existing_signal = AuroxSignal.query.filter_by(**unique_key).order_by(
                    AuroxSignal.timestamp.desc()).first()
                self.loc.log_or_console(True, "I", "    > Existing Signal", existing_signal)

                new_signal = None

                try:
                    # Check for existing signal to prevent duplicates
                    if existing_signal:
                        # Update existing record
                        existing_signal.timestamp = timestamp
                        existing_signal.price = signal_spot_price
                        existing_signal.signal = data['signal']
                        db.session.add(existing_signal)
                        self.loc.log_or_console(True, "I", "    > Updated existing signal", existing_signal)
                    else:
                        # Create a new signal if none exists for the specific time unit and trading pair
                        new_signal = AuroxSignal(
                            timestamp=timestamp,
                            price=signal_spot_price,
                            signal=data['signal'],
                            trading_pair=data['trading_pair'],
                            time_unit=data['timeUnit']
                        )
                        db.session.add(new_signal)
                        self.loc.log_or_console(True, "I", "    > Stored new signal", new_signal)

                    db.session.commit()  # Commit changes at the end of processing
                except db_errors as e:
                    self.loc.log_or_console(True, "E",
                                            "    >>> Error with storing or retrieving AuroxSignal",
                                            str(e))
                    db.session.rollback()

                next_months_product_id, next_month = self.check_for_contract_expires()

                # Now, get the bid and ask prices for the current futures product
                relevant_future_product = self.cb_adv_api.get_relevant_future_from_db(month_override=next_month)
                # self.loc.log_or_console(True, "I", "relevant_future_product product_id",
                #                         relevant_future_product.product_id)

                # Get the current bid and ask prices for the futures product related to this signal
                future_bid_price = 0
                future_ask_price = 0
                try:
                    future_bid_ask_price = self.cb_adv_api.get_current_bid_ask_prices(
                        relevant_future_product.product_id)
                    future_bid_price = future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
                    future_ask_price = future_bid_ask_price['pricebooks'][0]['asks'][0]['price']
                except AttributeError as e:
                    self.loc.log_or_console(True, "E",
                                            "Unable to get Future Bid and Ask Prices",
                                            "AttributeError:", e)
                except ValueError as e:
                    self.loc.log_or_console(True, "E",
                                            "Unable to get Future Bid and Ask Prices",
                                            "ValueError:", e)

                if next_months_product_id:
                    self.loc.log_or_console(True, "I",
                                            "    > next_months_product_id", next_months_product_id)
                    self.loc.log_or_console(True, "I",
                                            "    > next_month", next_month)

                if new_signal:
                    signal_id = new_signal.id
                else:
                    signal_id = existing_signal.id
                self.loc.log_or_console(True, "I", "    > Signal ID", signal_id)

                try:
                    # Find the related futures product based on the current futures product
                    if relevant_future_product:
                        existing_future_price_signal = FuturePriceAtSignal.query.filter_by(signal_id=signal_id).first()
                        if existing_future_price_signal:
                            # Correct the updating process by setting each field separately
                            existing_future_price_signal.signal_spot_price = float(signal_spot_price)
                            existing_future_price_signal.future_bid_price = future_bid_price
                            existing_future_price_signal.future_ask_price = future_ask_price
                            existing_future_price_signal.future_id = relevant_future_product.id
                            self.loc.log_or_console(True, "I", "Updated existing future price signal details")
                        else:
                            # If no existing record, create a new one
                            new_future_price_signal = FuturePriceAtSignal(
                                signal_id=signal_id,
                                signal_spot_price=float(signal_spot_price),
                                future_bid_price=future_bid_price,
                                future_ask_price=future_ask_price,
                                future_id=relevant_future_product.id
                            )
                            db.session.add(new_future_price_signal)
                            self.loc.log_or_console(True, "I", "Stored new future price signal")
                        db.session.commit()
                except db_errors as e:
                    self.loc.log_or_console(True, "E",
                                            "    >>> Error with storing or retrieving FuturePriceAtSignal",
                                            str(e))
                    db.session.rollback()
            except db_errors as e:
                self.loc.log_or_console(True, "E",
                                        "    >>> Error with storing or retrieving the Aurox signal",
                                        str(e))

    def get_latest_weekly_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_weekly_signal:")

        with self.flask_app.app_context():
            # Query the latest weekly signal including related future price data
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '1 Week') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_five_day_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_five_day_signal:")

        with self.flask_app.app_context():

            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '5 Days') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_three_day_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_three_day_signal:")

        with self.flask_app.app_context():

            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '3 Days') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_two_day_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_two_day_signal:")

        with self.flask_app.app_context():

            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '2 Days') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_daily_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_daily_signal:")

        with self.flask_app.app_context():

            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '1 Day') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_12_hour_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_12_hourly_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '12 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_8_hour_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_8_hourly_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '8 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_6_hour_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_6_hour_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '6 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_4_hour_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_4_hourly_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '4 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_3_hour_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_3_hour_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '3 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_2_hour_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_2_hour_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '2 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_1_hour_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_1_hour_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '1 Hour') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_30_minute_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_30_minute_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '30 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_20_minute_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_20_minute_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '20 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_15_minute_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_15_minute_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '15 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_10_minute_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_10_minute_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '10 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_5_minute_signal(self):
        # self.loc.log_or_console(True, "D", None,
        #                         ":get_latest_5_minute_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '5 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    @staticmethod
    def calculate_signal_score(signal: str, score: float):
        # self.loc.log_or_console(True, "D", None, ":calculate_signal_score:")
        calc_score = 0
        # long = BUY
        if signal == "long":
            calc_score += score
        # short = SELL
        elif signal == "short":
            calc_score -= score
        return calc_score

    def decide_trade_direction(self, calc_score):
        # self.loc.log_or_console(True, "D", None, ":decide_trade_direction:")

        # Define thresholds for long and short decisions
        # long_threshold = 100
        # short_threshold = -100
        long_threshold = int(config['trade.conditions']['trade_direction_long_threshold'])
        short_threshold = int(config['trade.conditions']['trade_direction_short_threshold'])

        if calc_score >= long_threshold:
            self.loc.log_or_console(True, "I",
                                    "   >>> Strong bullish sentiment detected with a score of",
                                    calc_score, "Going long.")
            return 'long'
        elif calc_score <= short_threshold:
            self.loc.log_or_console(True, "I",
                                    "   >>> Strong bearish sentiment detected with a score of",
                                    calc_score, "Going short.")
            return 'short'
        elif long_threshold > calc_score > short_threshold:
            self.loc.log_or_console(True, "I",
                                    "   >>> Neutral sentiment detected with a score of",
                                    calc_score, "Holding off.")
            return 'neutral'

    def decide_trade_direction_new(self, calc_score, long_threshold_str, short_threshold_str):
        # self.loc.log_or_console(True, "D", None, ":decide_trade_direction_new:")

        direction = 'neutral'
        dir_value = 0

        # Define thresholds for long and short decisions
        long_threshold = float(config['trade.conditions'][long_threshold_str])
        short_threshold = float(config['trade.conditions'][short_threshold_str])

        # decide_msg = f"Long: {long_threshold} Short: {short_threshold}"
        # self.loc.log_or_console(True, "I", "   > Trading Thresholds", decide_msg)
        # self.loc.log_or_console(True, "I", "   >    Calc Score", calc_score)

        if calc_score >= long_threshold:
            # self.loc.log_or_console(True, "I",
            #                         "   >>> Strong bullish sentiment detected with a score of",
            #                         calc_score, "Going long.")
            direction = 'long'
            dir_value = 1
        elif calc_score <= short_threshold:
            # self.loc.log_or_console(True, "I",
            #                         "   >>> Strong bearish sentiment detected with a score of",
            #                         calc_score, "Going short.")
            direction = 'short'
            dir_value = -1
        elif long_threshold > calc_score > short_threshold:
            # self.loc.log_or_console(True, "I",
            #                         "   >>> Neutral sentiment detected with a score of",
            #                         calc_score, "Holding off.")
            direction = 'neutral'
            dir_value = 0

        return direction, dir_value

    def decide_direction_strength(self, p_total_grp_dir_val):
        # self.loc.log_or_console(True, "D", None, ":decide_direction_strength:")

        if p_total_grp_dir_val >= 3:
            trade_value = 'STRONG_LONG'
        elif p_total_grp_dir_val >= 2:
            trade_value = 'MODERATE_LONG'
        elif p_total_grp_dir_val >= 1:
            trade_value = 'WEAK_LONG'
        elif p_total_grp_dir_val <= -3:
            trade_value = 'STRONG_SHORT'
        elif p_total_grp_dir_val <= -2:
            trade_value = 'MODERATE_SHORT'
        elif p_total_grp_dir_val <= -1:
            trade_value = 'WEAK_SHORT'
        else:
            trade_value = 'NEUTRAL'

        # self.loc.log_or_console(True, "I","   >>> Group Direction Value:", p_total_grp_dir_val)
        return trade_value

    def calc_all_signals_score_for_direction(self, week_sig, day_sig, twelve_sig, eight_sig, four_sig,
                                             hour_sig, fifteen_sig):
        self.loc.log_or_console(True, "D", None, "----------------------------")
        self.loc.log_or_console(True, "D", None, ":calc_all_signals_score_for_direction:")

        # NOTE: Created a scoring systems based on the signal timeframes. If the score is
        #   high or low enough based on the market direction (long or short), then we may
        #   be safer to trade in a particular direction

        calculated_score = 0

        # REVIEW: Should we adjust the weight of these values? using hours currently

        weekly_weight = int(config['trade.conditions']['weekly_weight'])
        daily_weight = int(config['trade.conditions']['daily_weight'])
        twelve_hr_weight = int(config['trade.conditions']['twelve_hr_weight'])
        eight_hr_weight = int(config['trade.conditions']['eight_hr_weight'])
        four_hr_weight = int(config['trade.conditions']['four_hr_weight'])
        one_hour_weight = int(config['trade.conditions']['one_hour_weight'])
        fifteen_min_weight = float(config['trade.conditions']['fifteen_min_weight'])

        weekly_ts_formatted = None
        daily_ts_formatted = None
        twelve_hour_ts_formatted = None
        eight_hour_ts_formatted = None
        four_hour_ts_formatted = None
        one_hour_ts_formatted = None
        fifteen_min_ts_formatted = None

        def display_signal_and_calc_signal_score(signal_record, weight, p_calc_score):
            # future_avg_price = 0
            # for future_price_data in signal_record.future_prices:
            #     signal_future_bid_price = future_price_data.future_bid_price
            #     signal_future_ask_price = future_price_data.future_ask_price
            #     future_avg_price = (signal_future_bid_price + signal_future_ask_price) / 2

            signals_dt = signal_record.timestamp
            ts_formatted = signals_dt.strftime("%B %d, %Y, %I:%M %p")

            # msg = (f"   > {signal_record.time_unit} - Signal: {signal_record.signal} "
            #        f"| Date: {ts_formatted} "
            #        f"| Avg Future Price: ${future_avg_price}")
            # self.loc.log_or_console(True, "D", None, msg)

            p_calc_score += self.calculate_signal_score(signal_record.signal, weight)
            return p_calc_score, ts_formatted

        if week_sig:
            (calculated_score, weekly_ts_formatted) = display_signal_and_calc_signal_score(week_sig,
                                                                                           weekly_weight,
                                                                                           calculated_score)
            # self.loc.log_or_console(True, "I","   >>> 1W Score", calculated_score)
        if day_sig:
            (calculated_score, daily_ts_formatted) = display_signal_and_calc_signal_score(day_sig,
                                                                                          daily_weight,
                                                                                          calculated_score)
            # self.loc.log_or_console(True, "I", "   >>> 1D Score", calculated_score)
        if twelve_sig:
            (calculated_score, twelve_hour_ts_formatted) = display_signal_and_calc_signal_score(twelve_sig,
                                                                                                twelve_hr_weight,
                                                                                                calculated_score)
            # self.loc.log_or_console(True, "I", "   >>> 12H Score", calculated_score)
        if eight_sig:
            (calculated_score, eight_hour_ts_formatted) = display_signal_and_calc_signal_score(eight_sig,
                                                                                               eight_hr_weight,
                                                                                               calculated_score)
            # self.loc.log_or_console(True, "I", "   >>> 8H Score", calculated_score)
        if four_sig:
            (calculated_score, four_hour_ts_formatted) = display_signal_and_calc_signal_score(four_sig,
                                                                                              four_hr_weight,
                                                                                              calculated_score)
            # self.loc.log_or_console(True, "I", "   >>> 4H Score", calculated_score)
        if hour_sig:
            (calculated_score, one_hour_ts_formatted) = display_signal_and_calc_signal_score(hour_sig,
                                                                                             one_hour_weight,
                                                                                             calculated_score)
            # self.loc.log_or_console(True, "I", "   >>> 1H Score", calculated_score)
        if fifteen_sig:
            (calculated_score, fifteen_min_ts_formatted) = display_signal_and_calc_signal_score(fifteen_sig,
                                                                                                fifteen_min_weight,
                                                                                                calculated_score)
            # self.loc.log_or_console(True, "I", "   >>> 15m Score", calculated_score)

        timestamp_obj = {
            "weekly_ts_fmt": weekly_ts_formatted,
            "daily_ts_fmt": daily_ts_formatted,
            "twelve_hr_ts_fmt": twelve_hour_ts_formatted,
            "eight_hr_ts_fmt": eight_hour_ts_formatted,
            "four_hr_ts_fmt": four_hour_ts_formatted,
            "one_hr_ts_fmt": one_hour_ts_formatted,
            "fifteen_min_ts_fmt": fifteen_min_ts_formatted,
        }

        # self.loc.log_or_console(True, "I",
        #                         "   >>> Total Trading Score", calculated_score)

        signal_calc_trade_direction = self.decide_trade_direction(calculated_score)
        # self.loc.log_or_console(True, "I",
        #                         "   >>> Position Trade Direction",
        #                         signal_calc_trade_direction)

        return signal_calc_trade_direction, calculated_score, timestamp_obj

    def calc_all_signals_score_for_dir_new(self, signals_dict):
        self.loc.log_or_console(True, "D", None, "----------------------------")
        self.loc.log_or_console(True, "D", None, ":calc_all_signals_score_for_dir_new:")

        # NOTE: Created a scoring systems based on the signal timeframes. If the score is
        #   high or low enough based on the market direction (long or short), then we may
        #   be safer to trade in a particular direction

        # REVIEW: Should we adjust the weight of these values? using hours currently

        grp1_calc_score = 0
        grp2_calc_score = 0
        grp3_calc_score = 0
        grp1_max = 0
        grp2_max = 0
        grp3_max = 0

        # Loop through all of group 1 (higher timeframes) and calculate the signal weight together
        for time_frame, signal in signals_dict["group1"].items():
            if signal:
                signal_weight = float(config['trade.conditions'][f'{time_frame}_weight'])
                grp1_calc_score += self.calculate_signal_score(signal.signal, signal_weight)
                grp1_max += signal_weight
                signal_dir = 1 if signal.signal == 'long' else -1
                # msg = f" {time_frame} - Signal: {signal.signal} Weight: {signal_weight * signal_dir}"
                # self.loc.log_or_console(True, "I", "   > Group 1 Signals", msg)

        # Loop through all of group 2 (middle timeframes) and calculate the signal weight together
        for time_frame, signal in signals_dict["group2"].items():
            if signal:
                signal_weight = float(config['trade.conditions'][f'{time_frame}_weight'])
                grp2_calc_score += self.calculate_signal_score(signal.signal, signal_weight)
                grp2_max += signal_weight
                signal_dir = 1 if signal.signal == 'long' else -1
                # msg = f" {time_frame} - Signal: {signal.signal} Weight: {signal_weight * signal_dir}"
                # self.loc.log_or_console(True, "I", "   > Group 2 Signals", msg)

        # Loop through all of group 3 (lower timeframes) and calculate the signal weight together
        for time_frame, signal in signals_dict["group3"].items():
            if signal:
                signal_weight = float(config['trade.conditions'][f'{time_frame}_weight'])
                grp3_calc_score += self.calculate_signal_score(signal.signal, signal_weight)
                grp3_calc_score = round(grp3_calc_score, 3)
                grp3_max += signal_weight
                signal_dir = 1 if signal.signal == 'long' else -1
                # msg = f" {time_frame} - Signal: {signal.signal} Weight: {signal_weight * signal_dir}"
                # self.loc.log_or_console(True, "I", "   > Group 3 Signals", msg)

        # Log out the signal weights min and max, plus calculated score
        grp1_msg = f"Max: {grp1_max} Score {grp1_calc_score} Mix: {-grp1_max}"
        self.loc.log_or_console(True, "I", "   > Group 1", grp1_msg)

        grp2_msg = f"Max: {grp2_max} Score {grp2_calc_score} Mix: {-grp2_max}"
        self.loc.log_or_console(True, "I", "   > Group 2", grp2_msg)

        grp3_msg = f"Max: {grp3_max} Score {grp3_calc_score} Mix: {-grp3_max}"
        self.loc.log_or_console(True, "I", "   > Group 3", grp3_msg)

        # Get the general trade direction, plus set a direction value
        grp1_direction, grp1_dir_val = self.decide_trade_direction_new(grp1_calc_score,
                                                                       'group_1_direction_long',
                                                                       'group_1_direction_short')

        grp2_direction, grp2_dir_val = self.decide_trade_direction_new(grp2_calc_score,
                                                                       'group_2_direction_long',
                                                                       'group_2_direction_short')

        grp3_direction, grp3_dir_val = self.decide_trade_direction_new(grp3_calc_score,
                                                                       'group_3_direction_long',
                                                                       'group_3_direction_short')
        # self.loc.log_or_console(True, "I", "   > Group 1 Direction Val",
        #                         grp1_direction, grp1_dir_val)
        # self.loc.log_or_console(True, "I", "   > Group 2 Direction Val",
        #                         grp2_direction, grp2_dir_val)
        # self.loc.log_or_console(True, "I", "   > Group 3 Direction Val",
        #                         grp3_direction, grp3_dir_val)

        # TODO: we're using the 1, -1, 0 for each group, but the method is designed for total value

        grp1_strength_trade_val = self.decide_direction_strength(grp1_dir_val)
        self.loc.log_or_console(True, "I", "   >>> Group 1 (HTF) Strength Trade Value",
                                grp1_strength_trade_val, grp1_dir_val)

        grp2_strength_trade_val = self.decide_direction_strength(grp2_dir_val)
        self.loc.log_or_console(True, "I", "   >>> Group 2 (MTF) Strength Trade Value",
                                grp2_strength_trade_val, grp2_dir_val)

        grp3_strength_trade_val = self.decide_direction_strength(grp3_dir_val)
        self.loc.log_or_console(True, "I", "   >>> Group 3 (LTF) Strength Trade Value",
                                grp3_strength_trade_val, grp3_dir_val)

        total_grp_dir_value = grp1_dir_val + grp2_dir_val + grp3_dir_val
        # self.loc.log_or_console(True, "I", "   >>> Total Group Direction Value", total_grp_dir_value)

        total_strength_trade_val = self.decide_direction_strength(total_grp_dir_value)
        # self.loc.log_or_console(True, "I", "   >>> Total Strength Trade Value", total_strength_trade_val)

        return total_grp_dir_value, total_strength_trade_val

    def compare_last_daily_to_todays_date(self):
        self.loc.log_or_console(True, "I", None, ":compare_last_daily_to_todays_date:")

        latest_signal = self.get_latest_daily_signal()
        if latest_signal:
            # Strip the 'Z' and parse the datetime
            signal_time = datetime.fromisoformat(latest_signal.timestamp.rstrip('Z'))

            # Ensuring it's UTC
            signal_time = signal_time.replace(tzinfo=pytz.utc)

            now = datetime.now(pytz.utc)  # Current time in UTC

            # Calculate time difference
            time_diff = now - signal_time

            # Check if the difference is less than or equal to 24 hours
            if time_diff <= datetime.timedelta(days=1):
                # print("Within 24 hours, proceed to place trade.")
                self.loc.log_or_console(True, "I", None, "Within 24 hours, proceed to place trade.")
                return True
            else:
                # print("More than 24 hours since the last signal, wait for the next one.")
                self.loc.log_or_console(True, "W", None,
                                        "More than 24 hours since the last signal, wait for the next one.")
        else:
            # print("No daily signal found.")
            self.loc.log_or_console(True, "W", None,
                                    "No daily signal found.")

    def check_for_contract_expires(self):
        self.loc.log_or_console(True, "D", None,
                                ":NEW_check_for_contract_expires:")

        # NOTE: Futures markets are open for trading from Sunday 6 PM to
        #  Friday 5 PM ET (excluding observed holidays),
        #  with a 1-hour break each day from 5 PM – 6 PM ET

        # Get the futures contract from Coinbase API
        list_future_products = self.cb_adv_api.list_products("FUTURE")
        self.cb_adv_api.store_btc_futures_products(list_future_products)

        # Get the current month's contract
        current_future_product = self.cb_adv_api.get_relevant_future_from_db()
        self.loc.log_or_console(True, "I",
                                "   Current Future Product",
                                current_future_product.product_id)

        current_month = self.cb_adv_api.get_current_short_month_uppercase()
        self.loc.log_or_console(True, "I",
                                "   Current Month", current_month)

        next_month = self.cb_adv_api.get_next_short_month_uppercase()
        self.loc.log_or_console(True, "I",
                                "   Next Month", next_month)

        if current_future_product:
            contract_expiry = current_future_product.contract_expiry.replace(tzinfo=pytz.utc)
            now = datetime.now(pytz.utc)
            time_diff = contract_expiry - now

            days, seconds = time_diff.days, time_diff.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60

            # contract_grace_days = 3
            contract_grace_days = int(config['end.of.contract.switch.period']['grace_days'])

            # FOR TESTING ONLY
            # days = 10

            # Check if the contract has expired
            if time_diff.total_seconds() <= 0:
                self.loc.log_or_console(True, "W", None, "-----------------------------------")
                self.loc.log_or_console(True, "W", None, ">>> Contract has expired!")
                self.loc.log_or_console(True, "W", None, ">>> Close out any positions!!!")
                self.loc.log_or_console(True, "W", None, "-----------------------------------")
                self.loc.log_or_console(True, "I", None, "Switching to next month's contract.")

                # Identify and switch to the next contract
                next_month_product, next_month = self.find_next_month_contract(list_future_products, next_month)

                if next_month_product:
                    self.loc.log_or_console(True, "I",
                                            "   > next_month_product.product_id",
                                            next_month_product['product_id'])
                    return next_month_product['product_id'], next_month
            elif days <= contract_grace_days:
                # If the contract expires in less than or equal to 3 days
                contract_msg = (f"  > Contract {current_future_product.product_id} is close to expiring"
                                f" in {days} days, {hours} hours, and {minutes} minutes.")
                self.loc.log_or_console(True, "I", None, contract_msg)
                self.loc.log_or_console(True, "I", None, "  > Switching to next month's contract.")

                # Identify and switch to the next contract
                next_month_product, next_month = self.find_next_month_contract(list_future_products, next_month)

                if next_month_product:
                    self.loc.log_or_console(True, "I",
                                            "   > next_month_product.product_id",
                                            next_month_product['product_id'])
                    return next_month_product['product_id'], next_month
            else:
                contract_msg = (f"  Current contract {current_future_product.product_id} is safe to trade. "
                                f"It expires in {days} days, {hours} hours, and {minutes} minutes.")
                self.loc.log_or_console(True, "I", None, contract_msg)
                return None, None
        else:
            self.loc.log_or_console(True, "I", None, "  !!! No current future product found")
            return None, None

    @staticmethod
    def find_next_month_contract(future_products, next_month):
        """Identify the next month's future contract based on the current product."""
        # print("future_products:")
        next_contact = None
        for fp in future_products['products']:
            f_products_contract_root_unit = fp['future_product_details']['contract_root_unit']

            # Limit to only BTC contacts
            if f_products_contract_root_unit == "BTC":
                display_name = fp['display_name']

                # Filter down to the next month futures contract
                if next_month in display_name:
                    next_contact = fp
        return next_contact, next_month

    def ladder_orders(self, side: str, product_id: str, bid_price, ask_price,
                      quantity: int = 5, manual_price: str = ''):
        self.loc.log_or_console(True, "D", None, "||||||||||||||||||||||||")
        self.loc.log_or_console(True, "D", None, ":ladder_orders:")

        # Prevent more than 10
        if quantity > 10:
            quantity = 10

        # NOTE: This is part of our strategy in placing DCA limit orders if the trade goes against us,
        #   even though both the Weekly and Daily signals are in our favor. This not only helps
        #   cover the volatility of the market and all the effects it, it also can help be more profitable
        #   if we're carefully. We also need to adjust the closing Long or Short order we'll place to
        #   help with risk management and taking profit.

        size = "1"
        leverage = "3"
        order_type = "limit_limit_gtc"
        cur_future_price = ""

        if manual_price == '':
            if side == "BUY":  # BUY / LONG
                cur_future_price = bid_price
            elif side == "SELL":  # SELL / SHORT
                cur_future_price = ask_price
            # print("cur_future_price:", cur_future_price)
        else:
            cur_future_price = manual_price
        self.loc.log_or_console(True, "I", "cur_future_price", cur_future_price)

        # dca_note_list = ['DCA1', 'DCA2', 'DCA3', 'DCA4', 'DCA5']
        dca_note_list = ["DCA" + str(x) for x in range(1, quantity + 1)]
        self.loc.log_or_console(True, "I", "    dca_note_list",
                                dca_note_list)

        # Generate the DCA percentages list dynamically based on 'quantity'
        # dca_per_offset_list = [0.01, 0.02, 0.03, 0.04, 0.05]
        dca_per_offset_list = [
            float(config['dca.ladder.trade_percentages'][f'dca_trade_{i + 1}_per'])
            for i in range(quantity)
        ]
        self.loc.log_or_console(True, "I", "    dca_per_offset_list",
                                dca_per_offset_list)

        dca_contract_size_list = [
            str(config['dca.ladder.trade_percentages'][f'dca_trade_{i + 1}_contracts'])
            for i in range(quantity)
        ]
        self.loc.log_or_console(True, "I", "    dca_contract_size_list",
                                dca_contract_size_list)

        def create_dca_orders():
            for i, note in enumerate(dca_note_list):
                if i <= quantity - 1:
                    dcg_limit_price = ""
                    dca_trade_per_offset = int(float(cur_future_price) * dca_per_offset_list[i])
                    self.loc.log_or_console(True, "D",
                                            "   DCA Trade Per Offset",
                                            dca_trade_per_offset)

                    # Calculate the DCA orders (Long or Short)
                    if side == "BUY":  # BUY / LONG
                        dcg_limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                            int(cur_future_price) - dca_trade_per_offset)
                        self.loc.log_or_console(True, "D",
                                                "   > Buy Long dcg_limit_price: $",
                                                dcg_limit_price)

                    elif side == "SELL":  # SELL / SHORT
                        dcg_limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                            int(cur_future_price) + dca_trade_per_offset)
                        self.loc.log_or_console(True, "D",
                                                "   > Sell Short dcg_limit_price: $",
                                                dcg_limit_price)

                    contract_size = dca_contract_size_list[i]

                    # Create DCA Trade
                    dca_order_created = self.cb_adv_api.create_order(side=side,
                                                                     product_id=product_id,
                                                                     size=contract_size,
                                                                     limit_price=dcg_limit_price,
                                                                     leverage=leverage,
                                                                     order_type=order_type,
                                                                     bot_note=note)
                    self.loc.log_or_console(True, "D", "DCA order_created!", dca_order_created)

        create_dca_orders()

    def is_trading_time(self, current_time):
        self.loc.log_or_console(True, "I", None, "---> Checking for open market...")
        """Check if the current time is within trading hours.
            Trading hours are Sunday 6 PM to Friday 5 PM ET, with a break from 5 PM to 6 PM daily.
        """
        # Define the Eastern Time Zone
        eastern = pytz.timezone('America/New_York')

        # Convert current time to Eastern Time if it isn't already
        if current_time.tzinfo is None or current_time.tzinfo.utcoffset(current_time) is None:
            current_time = pytz.utc.localize(current_time).astimezone(eastern)
        else:
            current_time = current_time.astimezone(eastern)

        # Check day of the week (Monday is 0 and Sunday is 6)
        weekday = current_time.weekday()

        # Get the current time as a time object
        current_time_only = current_time.time()

        # Define trading break time
        break_start = time(17, 0, 0)  # 5 PM
        break_end = time(18, 0, 0)  # 6 PM

        # Trading conditions
        is_during_week = weekday < 5  # Monday to Friday
        is_before_break = current_time_only < break_start
        is_after_break = current_time_only >= break_end
        is_sunday_after_6pm = weekday == 6 and current_time_only >= time(18, 0, 0)  # After 6 PM on Sunday
        is_friday_before_5pm = weekday == 4 and current_time_only < break_start  # Before 5 PM on Friday

        # Determine if it's a valid trading time
        if is_during_week and (is_before_break or is_after_break):
            self.loc.log_or_console(True, "I", None, " >>> Futures market is OPEN! <<<")
            return True
        elif is_sunday_after_6pm or is_friday_before_5pm:
            self.loc.log_or_console(True, "I", None, " >>> Futures market is OPEN! <<<")
            return True
        self.loc.log_or_console(True, "W", None, " >>> Futures market is CLOSED. <<<")
        return False

    def check_trading_conditions(self):
        self.loc.log_or_console(True, "D", None, "--------------------------")
        self.loc.log_or_console(True, "D", None, ":check_trading_conditions:")

        # Update any cancelled orders in the database (in case we close things manually, etc.)
        self.cb_adv_api.update_cancelled_orders()

        #######################
        # Do we have an existing trades?
        #######################

        next_months_product_id, next_month = self.check_for_contract_expires()
        if next_months_product_id:
            self.loc.log_or_console(True, "I", "Next Months Product ID", next_months_product_id)
            self.loc.log_or_console(True, "I", "Next Month", next_month)

        # Get Current Positions from API, we just need to acknowledge this position exists
        #  and get the position side
        future_positions = self.cb_adv_api.list_future_positions()
        # print("Future Positions:")
        # pp(future_positions)

        weekly_signals = self.get_latest_weekly_signal()
        daily_signals = self.get_latest_daily_signal()
        twelve_hour_signals = self.get_latest_12_hour_signal()
        eight_hour_signals = self.get_latest_8_hour_signal()
        four_hour_signals = self.get_latest_4_hour_signal()
        one_hour_signals = self.get_latest_1_hour_signal()
        fifteen_min_signals = self.get_latest_15_minute_signal()

        # signals_list = [weekly_signals, daily_signals, twelve_hour_signals,eight_hour_signals,four_hour_signals,one_hour_signals,fifteen_min_signals]

        signal_calc_trade_direction, signal_score, ts_obj = self.calc_all_signals_score_for_direction(weekly_signals,
                                                                                                      daily_signals,
                                                                                                      twelve_hour_signals,
                                                                                                      eight_hour_signals,
                                                                                                      four_hour_signals,
                                                                                                      one_hour_signals,
                                                                                                      fifteen_min_signals)

        # market_direction, signal_score_2, ts_obj_2  = self.calc_all_signals_score_for_direction_2(weekly_signals, daily_signals, twelve_hour_signals,eight_hour_signals,four_hour_signals,one_hour_signals,fifteen_min_signals)
        # print(" >>> market_direction:", market_direction)
        # print(" >>> signal_score_2:", signal_score_2)
        # print("ts_obj_2:", ts_obj_2)

        weekly_ts_formatted = ts_obj['weekly_ts_fmt']
        daily_ts_formatted = ts_obj['daily_ts_fmt']
        twelve_hour_ts_formatted = ts_obj['twelve_hr_ts_fmt']
        eight_hour_ts_formatted = ts_obj['eight_hr_ts_fmt']
        four_hour_ts_formatted = ts_obj['four_hr_ts_fmt']
        one_hour_ts_formatted = ts_obj['one_hr_ts_fmt']
        fifteen_min_ts_formatted = ts_obj['fifteen_min_ts_fmt']

        # Make sure we have a future position
        if len(future_positions['positions']) > 0:
            self.loc.log_or_console(True, "I", None, "  > We have an active position(s) <")

            position_side = future_positions['positions'][0]['side']
            # print("position_side:", position_side)

            side = ""
            if position_side == "LONG":
                side = "BUY"
            elif position_side == "SHORT":
                side = "SELL"

            # Now, get the Future Order from the DB so we have more accurate data
            cur_position_order = self.cb_adv_api.get_current_take_profit_order_from_db(
                order_status="FILLED", side=side, bot_note="MAIN")
            # self.loc.log_or_console(True, "I", "Cur Position Order", cur_position_order)

            # Clear and store the active future position
            self.cb_adv_api.store_future_positions(future_positions)

            # Make sure we have a FILLED order from our position
            if cur_position_order:
                # Get the position from the database
                # NOTE: We should only get one if we're only trading one future (BTC)
                with (self.flask_app.app_context()):  # Push an application context
                    try:
                        # NOTE: position doesn't have the all most accurate data we need, so
                        #  we uses the order to help supplement what we need
                        positions = FuturePosition.query.all()
                        # self.loc.log_or_console(True, "I", "positions", positions)
                        for position in positions:
                            self.tracking_current_position_profit_loss(position, cur_position_order, next_month)
                            self.track_take_profit_order(position, cur_position_order)

                    except Exception as e:
                        self.loc.log_or_console(True, "E", "Unexpected error:", msg1=e)
            else:
                self.loc.log_or_console(True, "W",
                                        "    >>> NO Current Position Order Found", cur_position_order)
        else:
            self.loc.log_or_console(True, "I", None, " >>> No Open Position")
            self.loc.log_or_console(True, "I", None,
                                    " >>> Check if its a good market to place a trade")

            # NOTE: Check to cancel any OPEN orders

            future_contract = self.cb_adv_api.get_relevant_future_from_db()
            remaining_open_orders = self.cb_adv_api.list_orders(product_id=future_contract.product_id,
                                                                order_status="OPEN")
            if 'orders' in remaining_open_orders:
                self.loc.log_or_console(True, "D",
                                        "remaining_open_orders count",
                                        len(remaining_open_orders['orders']))
                order_ids = []
                client_order_ids = []
                for order in remaining_open_orders['orders']:
                    order_ids.append(order['order_id'])
                    client_order_ids.append(order['client_order_id'])

                # Pass the order_id as a list. Can place multiple order ids if necessary,
                #   but not in this case
                cancelled_order = self.cb_adv_api.cancel_order(order_ids=order_ids)
                self.loc.log_or_console(True, "I", "    > cancelled_order", cancelled_order)

                field_values = {
                    "bot_active": 0,
                    "order_status": "CANCELLED"
                }

                # for order in remaining_open_orders['orders']:
                for client_order_id in client_order_ids:
                    # Update order so we don't the system doesn't try to use it for future orders
                    updated_cancelled_order = self.cb_adv_api.update_order_fields(
                        client_order_id=client_order_id,
                        field_values=field_values
                    )
                    self.loc.log_or_console(True, "I", "    > updated_cancelled_order", updated_cancelled_order)

                # Now, update an other Future Order records setting bot_active = 0
                self.cb_adv_api.update_bot_active_orders()

            #
            # If our overall position trade direction isn't neutral, then proceed
            #
            if signal_calc_trade_direction != "neutral":
                self.loc.log_or_console(True, "I", None,
                                        "-----------------------------------")
                self.loc.log_or_console(True, "I", None,
                                        " >>> Signals are strong either bullish or bearish, "
                                        "see if we should place a trade")

                # NOTE: Next, let's look at the fifteen minute and how close to the
                #  last signal and price of when we should place a limit order.
                #  How are in price are we away from the last signal?
                #  What is a good price threshold?
                #  Is 15 Minute signal side the same as the signal_calc_trade_direction side?

                fifteen_min_trade_signal = fifteen_min_signals.signal

                # NOTE: Does the 15 Min match the overall signal trade direction of the Aurox signals?

                if fifteen_min_trade_signal == signal_calc_trade_direction:
                    self.loc.log_or_console(True, "I", None,
                                            "   >>> YES, the 15 Min matches the overall trade direction")

                    # Check to see if next months product id is populated
                    if next_months_product_id is None:
                        # Get this months current product
                        relevant_future_product = self.cb_adv_api.get_relevant_future_from_db()
                        self.loc.log_or_console(True, "I", "    Relevant Future Product",
                                                relevant_future_product.product_id)
                        product_id = relevant_future_product.product_id
                    else:
                        product_id = next_months_product_id

                    bid_price, ask_price, avg_price = self.cb_adv_api.get_current_average_price(product_id=product_id)
                    self.loc.log_or_console(True, "I",
                                            "   bid ask avg_price", avg_price)

                    limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(avg_price)
                    self.loc.log_or_console(True, "I",
                                            "   Current Limit Price", limit_price)

                    fifteen_min_future_avg_price = 0
                    for future_price in fifteen_min_signals.future_prices:
                        future_bid_price = future_price.future_bid_price
                        future_ask_price = future_price.future_ask_price
                        fifteen_min_future_avg_price = round((future_bid_price + future_ask_price) / 2)
                    self.loc.log_or_console(True, "I",
                                            "   Fifteen Min Future Avg Price",
                                            fifteen_min_future_avg_price)

                    # Just setting a high default number to check again
                    percentage_diff = 10

                    # The signal price should be lower than current price (price rising)
                    check_signal_and_current_price_diff = 0
                    if signal_calc_trade_direction == 'long':
                        check_signal_and_current_price_diff = int(limit_price) - int(fifteen_min_future_avg_price)
                        percentage_diff = round((check_signal_and_current_price_diff
                                                 / int(fifteen_min_future_avg_price)) * 100, 2)

                    elif signal_calc_trade_direction == 'short':
                        check_signal_and_current_price_diff = int(fifteen_min_future_avg_price) - int(limit_price)
                        percentage_diff = round((check_signal_and_current_price_diff
                                                 / int(fifteen_min_future_avg_price)) * 100, 2)

                    # NOTE: Make sure the price difference from the 15 Min signal and current price
                    #   isn't too far off or beyond 1%, so we try to be safe and get more profit

                    # Set a limit value is here (1 = 1%)
                    # percentage_diff_limit = 1
                    percentage_diff_limit = float(config['trade.conditions']['percentage_diff_limit'])
                    per_diff_msg = (f"   >>> Checking! Signal Direction "
                                    f"{signal_calc_trade_direction} "
                                    f" Per Diff {percentage_diff}% < {percentage_diff_limit}% Limit")
                    self.loc.log_or_console(True, "I", None, per_diff_msg)

                    if percentage_diff < percentage_diff_limit:
                        good_per_diff_msg = (f"   >>> Proceeding! current price diff of "
                                             f"{check_signal_and_current_price_diff} "
                                             f"which is {percentage_diff}%")
                        self.loc.log_or_console(True, "W", None, good_per_diff_msg)

                        trade_side = ""

                        # LONG = BUY
                        # SHORT = SELL
                        if signal_calc_trade_direction == "long":
                            trade_side = "BUY"
                        elif signal_calc_trade_direction == "short":
                            trade_side = "SELL"

                        size = "1"
                        leverage = "3"
                        order_type = "limit_limit_gtc"
                        order_msg = (f"    >>> Trade side:{trade_side} Order type:{order_type} "
                                     f"Limit Price:{limit_price} Size:{size} Leverage:{leverage}")
                        self.loc.log_or_console(True, "I", None, order_msg)

                        # Create a new MAIN order
                        order_created = self.cb_adv_api.create_order(side=trade_side,
                                                                     product_id=product_id,
                                                                     size=size,
                                                                     limit_price=limit_price,
                                                                     leverage=leverage,
                                                                     order_type=order_type,
                                                                     bot_note="MAIN")
                        print("MAIN order_created:", order_created)

                        # TODO: Need to see if the MAIN order is filled first before placing ladder orders

                        # How many ladder orders? (10 max)
                        # ladder_order_qty = 8
                        ladder_order_qty = int(config['dca.ladder.trade_percentages']['ladder_quantity'])

                        # Create the DCA ladder orders
                        self.ladder_orders(quantity=ladder_order_qty,
                                           side=trade_side,
                                           product_id=product_id,
                                           bid_price=bid_price,
                                           ask_price=ask_price)
                    else:
                        bad_per_diff_msg = (f"   >>> Holding off, current price diff of "
                                            f"{check_signal_and_current_price_diff} "
                                            f"which is {percentage_diff}%")
                        self.loc.log_or_console(True, "W", None, bad_per_diff_msg)
                else:
                    self.loc.log_or_console(True, "W", None,
                                            "   >>> NO, the 15 Min does not match the overall trade direction")
                    fifteen_min_pos_trade_dir_msg = (f"     >>> 15 Min Signal: {fifteen_min_trade_signal} "
                                                     f"!= Signal Trade Direction: {signal_calc_trade_direction}")
                    self.loc.log_or_console(True, "W", None,
                                            fifteen_min_pos_trade_dir_msg)
            else:
                self.loc.log_or_console(True, "W", None,
                                        "Signal score is neutral, let's wait... Score:", signal_score)

                weekly_msg = f"Weekly Signal: {weekly_signals.signal} | Date: {weekly_ts_formatted}"
                daily_msg = f"Daily Signal: {daily_signals.signal} | Date: {daily_ts_formatted}"
                twelve_msg = f"12 Hr Signal: {twelve_hour_signals.signal} | Date: {twelve_hour_ts_formatted}"
                eight_msg = f"8 Hr Signal: {eight_hour_signals.signal} | Date: {eight_hour_ts_formatted}"
                four_msg = f"4 Hr Signal: {four_hour_signals.signal} | Date: {four_hour_ts_formatted}"
                hour_msg = f"1 Hr Signal: {one_hour_signals.signal} | Date: {one_hour_ts_formatted}"
                fifteen_msg = f"15 Min Signal: {fifteen_min_signals.signal} | Date: {fifteen_min_ts_formatted}"
                self.loc.log_or_console(True, "W", None, weekly_msg)
                self.loc.log_or_console(True, "W", None, daily_msg)
                self.loc.log_or_console(True, "W", None, twelve_msg)
                self.loc.log_or_console(True, "W", None, eight_msg)
                self.loc.log_or_console(True, "W", None, four_msg)
                self.loc.log_or_console(True, "W", None, hour_msg)
                self.loc.log_or_console(True, "W", None, fifteen_msg)

    def tracking_current_position_profit_loss(self, position, order, next_month):
        self.loc.log_or_console(True, "D", None, "---------------------------------------")
        self.loc.log_or_console(True, "D", None, ":tracking_current_position_profit_loss:")

        # print(" position:", position)
        # print(" order:", order)

        # Only run if we have ongoing positions
        if position:
            product_id = position.product_id
            self.loc.log_or_console(True, "I", "  position.product_id:", product_id)

            side = position.side
            self.loc.log_or_console(True, "I", "  position.side:", side)

            # print("next_month:", next_month)
            # self.loc.log_or_console(True, "I", "  next_month:", next_month)

            relevant_future_product = self.cb_adv_api.get_relevant_future_from_db(month_override=next_month)
            product_contract_size = relevant_future_product.contract_size
            # self.loc.log_or_console(True, "I", "  product_contract_size:", product_contract_size)

            if order is not None:
                # print("  Profit / Loss: order", order)
                # print("  Profit / Loss: order.average_filled_price", order.average_filled_price)

                dca_side = ''

                # If we're LONG, then we need to place a profitable BUY order
                if side == "LONG":  # BUY / LONG
                    dca_side = "BUY"
                # If we're SHORT, then we need to place a profitable SELL order
                elif side == "SHORT":  # SELL / SHORT
                    dca_side = "SELL"

                dca_avg_filled_price, dca_avg_filled_price_2, dca_count = self.cb_adv_api.get_dca_filled_orders_from_db(
                    dca_side=dca_side)
                self.loc.log_or_console(True, "I", "    dca_count", dca_count)
                self.loc.log_or_console(True, "I", "    dca_avg_filled_price", dca_avg_filled_price)

                # Get the average filled price from the Future Order
                avg_filled_price = round((int(order.average_filled_price) + dca_avg_filled_price) / dca_count)
                self.loc.log_or_console(True, "I", "    avg_filled_price", avg_filled_price)

                # Get the current price from the Future Position
                current_price = round(int(position.current_price), 2)
                # self.loc.log_or_console(True, "I", "    current_price", current_price)

                number_of_contracts = position.number_of_contracts
                # self.loc.log_or_console(True, "I", "    number_of_contracts", number_of_contracts)

                # Calculate total cost and current value per contract
                total_initial_cost = avg_filled_price * number_of_contracts * product_contract_size
                total_current_value = current_price * number_of_contracts * product_contract_size
                # self.loc.log_or_console(True, "I", "  total_initial_cost", total_initial_cost)
                # self.loc.log_or_console(True, "I", "  total_current_value", total_current_value)

                # Calculate profit or loss for all contracts
                # NOTE: We need to factor in what side of the market: long or short
                calc_profit_or_loss = 0
                if position.side.lower() == 'long':  # Assuming 'buy' denotes a long position
                    calc_profit_or_loss = round(total_current_value - total_initial_cost, 4)
                elif position.side.lower() == 'short':  # Assuming 'sell' denotes a short position
                    calc_profit_or_loss = round(total_initial_cost - total_current_value, 4)
                # self.loc.log_or_console(True, "I", "  calc_profit_or_loss", calc_profit_or_loss)

                if total_initial_cost != 0:  # Prevent division by zero
                    calc_percentage = round((calc_profit_or_loss / total_initial_cost) * 100, 4)
                else:
                    calc_percentage = 0
                self.loc.log_or_console(True, "I", "  calc_percentage:", calc_percentage)

                # print("Contract Expires on", future_position['position']['expiration_time'])
                # print(" Contract Expires on", position.expiration_time)

                self.loc.log_or_console(True, "I", None, ">>>>>>>>>>>>>>>>>>>>>>>>>>>")
                self.loc.log_or_console(True, "I", None, ">>> Profit / Loss <<<")
                self.loc.log_or_console(True, "I", "Product Id", product_id)
                self.loc.log_or_console(True, "I", "Position Side", side)
                self.loc.log_or_console(True, "I", "Avg Entry Price $", avg_filled_price)
                self.loc.log_or_console(True, "I", "Current Price $", current_price)
                self.loc.log_or_console(True, "I", "# of Contracts", number_of_contracts)
                if calc_percentage >= 2:
                    self.loc.log_or_console(True, "I", "Take profit at 2% or higher %", calc_percentage)
                    self.loc.log_or_console(True, "I", "Good Profit $", calc_profit_or_loss)
                elif 2 > calc_percentage > 0.5:
                    self.loc.log_or_console(True, "I", "Not ready to take profit %", calc_percentage)
                    self.loc.log_or_console(True, "I", "Ok Profit $", calc_profit_or_loss)
                elif 0.5 >= calc_percentage >= 0:
                    self.loc.log_or_console(True, "I", "Neutral %", calc_percentage)
                    self.loc.log_or_console(True, "I", "Not enough profit $", calc_profit_or_loss)
                elif calc_percentage < 0:
                    self.loc.log_or_console(True, "I", "Trade negative %", calc_percentage)
                    self.loc.log_or_console(True, "I", "No profit, loss of $", calc_profit_or_loss)
                self.loc.log_or_console(True, "I", None, ">>>>>>>>>>>>>>>>>>>>>>>>>>>")
            else:
                self.loc.log_or_console(True, "W", "No open order", order)
        else:
            self.loc.log_or_console(True, "W", "No open positions", position)

    def track_take_profit_order(self, position, order):
        self.loc.log_or_console(True, "D", None, "-------------------------")
        self.loc.log_or_console(True, "D", None, ":track_take_profit_order:")

        # NOTE: This is where we place an opposing order, so if we're longing the market,
        #   We need to place a Sell order at our take profit.
        #   As well, if we're shorting the market, we need to place a Buy order to take profit

        # REVIEW: Figure out the take profit, especially if we have more orders added
        #   The average price may be key here, plus the percentage we want to profit from
        #   or a opposing signal, or the end of the contract date

        # print("position:", position)
        # print("order:", order)

        # Only run if we have ongoing positions and order
        if position and order:

            product_id = position.product_id
            take_profit_side = ""
            dca_side = ""
            side = position.side
            # self.loc.log_or_console(True, "I", "position.side", side)

            # If we're LONG, then we need to place a profitable BUY order
            if side == "LONG":  # BUY / LONG
                take_profit_side = "SELL"
                dca_side = "BUY"
            # If we're SHORT, then we need to place a profitable SELL order
            elif side == "SHORT":  # SELL / SHORT
                take_profit_side = "BUY"
                dca_side = "SELL"
            self.loc.log_or_console(True, "I", "    take_profit_side", take_profit_side)

            # TODO: Need to test if the average price changes based on more positions (contracts)
            #   This may need to be adjusted back to using the Position record vs the Order record
            #   if more contracts are bought

            # Now, get the ALL Future Orders from the DB so we have more accurate data
            take_profit_order = self.cb_adv_api.get_current_take_profit_order_from_db(
                order_status="OPEN", side=take_profit_side, bot_note="TAKE_PROFIT", get_all_orders=True)
            # self.loc.log_or_console(True, "I", "  > take_profit_order exists 1", take_profit_order)

            # BUG: Need to fix duplicate Take Profit orders, creating work around for now

            # NOTE: If we have more than one Take Profit, keep one and cancel the rest

            if len(take_profit_order) > 1:
                # Loop through all of the take profit orders, except one (we keep that)
                for tp in range(0, len(take_profit_order) - 1):
                    loop_tp_order = take_profit_order[tp]
                    loop_tp_order_id = loop_tp_order.order_id
                    loop_tp_client_order_id = loop_tp_order.client_order_id
                    # self.loc.log_or_console(True, "I", "    >>> tp", tp, loop_tp_order)
                    # self.loc.log_or_console(True, "I", "    tp.order_id", loop_tp_order_id)

                    # Pass the order_id as a list. Can place multiple order ids if necessary, but not in this case
                    cancelled_order = self.cb_adv_api.cancel_order(order_ids=[loop_tp_order_id])
                    self.loc.log_or_console(True, "I",
                                            "    Cancelled Extra Order", cancelled_order)
                    field_values = {
                        "bot_active": 0,
                        "order_status": "CANCELLED"
                    }
                    # Update order so we don't the system doesn't try to use it for future orders
                    updated_cancelled_order = self.cb_adv_api.update_order_fields(
                        client_order_id=loop_tp_client_order_id,
                        field_values=field_values)
                    self.loc.log_or_console(True, "I",
                                            "    Updated Extra Cancelled Order", updated_cancelled_order)

            # Run this again to get only one take profit order
            take_profit_order = self.cb_adv_api.get_current_take_profit_order_from_db(
                order_status="OPEN", side=take_profit_side, bot_note="TAKE_PROFIT", get_all_orders=False)
            # self.loc.log_or_console(True, "I",
            #                         "   > take_profit_order exists 1.5", take_profit_order)

            # Now see if we have a take profit order already open
            if take_profit_order is not None:
                # self.loc.log_or_console(True, "I", "  > take_profit_order exists 2", take_profit_order)
                existing_take_profit_order = True
            else:
                existing_take_profit_order = False
                self.loc.log_or_console(True, "W", "    No take_profit_order", take_profit_order)

            # NOTE: Find all the FILLED DCA orders to get the average price

            number_of_contracts = position.number_of_contracts
            # self.loc.log_or_console(True, "I", "    Number Of Contracts", number_of_contracts)

            dca_avg_filled_price, dca_avg_filled_price_2, dca_count = self.cb_adv_api.get_dca_filled_orders_from_db(
                dca_side=dca_side)
            self.loc.log_or_console(True, "I", "    DCA Count", dca_count)
            # self.loc.log_or_console(True, "I", "    DCA Avg Filled Price", dca_avg_filled_price)
            # self.loc.log_or_console(True, "I", "    DCA Avg dca_avg_filled_price_2 Price", dca_avg_filled_price_2)

            main_order_avg_filled_price = int(order.average_filled_price)
            # self.loc.log_or_console(True, "I", "    MAIN Order Avg Filled Price", main_order_avg_filled_price)

            avg_filled_price = round((main_order_avg_filled_price + dca_avg_filled_price) / dca_count)
            # self.loc.log_or_console(True, "I", "    ALL ORDERS Avg Filled Price", avg_filled_price)

            avg_filled_price_2 = round((main_order_avg_filled_price + dca_avg_filled_price_2) / number_of_contracts)
            # self.loc.log_or_console(True, "I", "    ALL ORDERS Avg Filled Price 2", avg_filled_price_2)

            # take_profit_percentage = 0.01
            take_profit_percentage = float(config['take.profit.order']['take_profit_percentage'])
            tp_per_msg = f" Take Profit Percentage: {take_profit_percentage * 100}%"
            self.loc.log_or_console(True, "I", None, tp_per_msg)

            # Calculate the take profit price (Long or Short)
            take_profit_offset_price = int(float(avg_filled_price) * take_profit_percentage)
            # self.loc.log_or_console(True, "I", "     Take Profit Offset Price", take_profit_offset_price)

            # Calculate the take profit price (Long or Short)
            take_profit_offset_price_2 = int(float(avg_filled_price_2) * take_profit_percentage)
            # self.loc.log_or_console(True, "I", "     Take Profit Offset Price 2", take_profit_offset_price_2)

            take_profit_price = ""

            # If we're LONG, then we need to place a profitable SELL order
            if side == "LONG":  # BUY / LONG
                take_profit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                    int(avg_filled_price) + take_profit_offset_price_2)
                self.loc.log_or_console(True, "I", "    > SELL Short take_profit_price: $",
                                        take_profit_price)

            # If we're SHORT, then we need to place a profitable BUY order
            elif side == "SHORT":  # SELL / SHORT
                take_profit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                    int(avg_filled_price) - take_profit_offset_price_2)
                self.loc.log_or_console(True, "I", "    > BUY Long take_profit_price: $",
                                        take_profit_price)

            order_type = "limit_limit_gtc"

            # If we don't have an existing take profit order, create one
            if existing_take_profit_order is False:
                self.loc.log_or_console(True, "I", None,
                                        "  >>> Create new take_profit_order")

                # Take Profit Order
                order_created = self.cb_adv_api.create_order(side=take_profit_side,
                                                             product_id=product_id,
                                                             size=number_of_contracts,
                                                             limit_price=take_profit_price,
                                                             leverage='',
                                                             order_type=order_type,
                                                             bot_note="TAKE_PROFIT")
                self.loc.log_or_console(True, "I", None,
                                        "   >>> TAKE_PROFIT order_created!")
                self.loc.log_or_console(True, "I", "    >>> Order:", order_created)

            else:  # Otherwise, let's edit and update the order based on the market and position(s)
                self.loc.log_or_console(True, "I", None,
                                        "  >>> Check Existing Take Profit Order...")
                # pp(take_profit_order)
                tp_order_id = take_profit_order.order_id
                tp_client_order_id = take_profit_order.client_order_id
                # self.loc.log_or_console(True, "I", "tp_order_id", tp_order_id)
                # self.loc.log_or_console(True, "I", "tp_client_order_id", tp_client_order_id)

                # For limit GTC orders only
                size = take_profit_order.base_size
                # self.loc.log_or_console(True, "I", "take_profit_order size", size)

                # See if we need to update the size based on the existing number of
                # contracts in the position
                if int(number_of_contracts) > int(size):
                    new_size = number_of_contracts
                    self.loc.log_or_console(True, "W",
                                            "    take_profit_order new_size", new_size)
                else:
                    new_size = size
                # print(" take_profit_order new_size:", new_size)

                # FOR TESTING
                # take_profit_price = "62230"
                # new_size = str(2)

                # REVIEW: Since the edit_order API call isn't working (and I've reached out to support),
                #  I'll just cancel the order and place a new one. This shouldn't run that often for
                #  the DCA take profit orders, however, I do want to solve this for trailing take profit

                # NOTE: In order to update the order, we need to get it first, then check the values against
                #   if we have an updates contact "size" or "price" based on the DCA orders, if not
                #   then we can skip this

                base_size = take_profit_order.base_size
                limit_price = take_profit_order.limit_price

                check_price_size_msg = f" {int(limit_price)} != {int(take_profit_price)} or {base_size} != {new_size}"
                self.loc.log_or_console(True, "I",
                                        "    Check Price Size Msg", check_price_size_msg)

                # Check to see if either price or size don't match
                if (int(limit_price) != int(take_profit_price)) is True or (int(base_size) != int(new_size)) is True:
                    self.loc.log_or_console(True, "I", None,
                                            "   >>> Either the prices are off or the contract sizes are off")
                    self.loc.log_or_console(True, "I", None,
                                            "   >>> Cancel the existing take profit or and place a new one!")

                    # NOTE: Cancel the existing take profit order, update it's db record,
                    #  then place a new take profit with the the updated price and size

                    if len(tp_order_id) > 0:
                        # Pass the order_id as a list. Can place multiple order ids if necessary, but not in this case
                        cancelled_order = self.cb_adv_api.cancel_order(order_ids=[tp_order_id])
                        self.loc.log_or_console(True, "I",
                                                "    cancelled_order", cancelled_order)

                        field_values = {
                            "bot_active": 0,
                            "order_status": "CANCELLED"
                        }
                        # Update order so we don't the system doesn't try to use it for future orders
                        updated_cancelled_order = self.cb_adv_api.update_order_fields(
                            client_order_id=tp_client_order_id,
                            field_values=field_values)
                        self.loc.log_or_console(True, "I",
                                                "    updated_cancelled_order", updated_cancelled_order)

                    self.loc.log_or_console(True, "I", None,
                                            "   >>> Creating new order with updated PRICE or SIZE settings!")
                    # Take Profit Order
                    take_profit_order_created = self.cb_adv_api.create_order(side=take_profit_side,
                                                                             product_id=product_id,
                                                                             size=new_size,
                                                                             limit_price=take_profit_price,
                                                                             leverage='',
                                                                             order_type=order_type,
                                                                             bot_note="TAKE_PROFIT")
                    self.loc.log_or_console(True, "I",
                                            "   >>> take_profit_order_created", take_profit_order_created)
                else:
                    self.loc.log_or_console(True, "I", None,
                                            "   ...No changes with take profit order in PRICE or SIZE...")
        else:
            self.loc.log_or_console(True, "W",
                                    "    No open positions | orders", position, order)


if __name__ == "__main__":
    print(__name__)

    ############################
    # def on_message(msg):
    #     print(msg)
    # ws_client = WSClient(api_key=API_KEY, api_secret=API_SECRET, on_message=on_message, verbose=True)
    # ws_client.open()
    # # ws_client.subscribe(["BTC-USD"], ["heartbeats", "ticker"])
    # ws_client.subscribe(["BIT-26APR24-CDE"], ["heartbeats", "ticker"])
    # ws_client.sleep_with_exception_check(30)
    # # ws_client.run_forever_with_exception_check()
    # ws_client.close()

    ############################
    # def on_message(msg):
    #     print(msg)
    # ws_client = WSClient(api_key=API_KEY, api_secret=API_SECRET, on_message=on_message, verbose=True)
    #
    # try:
    #     ws_client.open()
    #     ws_client.subscribe(product_ids=["BTC-USD",], channels=["ticker", "heartbeats"])
    #     ws_client.run_forever_with_exception_check()
    # except WSClientConnectionClosedException as e:
    #     print("Connection closed! Retry attempts exhausted.")
    # except WSClientException as e:
    #     print("Error encountered!")
