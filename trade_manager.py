from coinbase.rest import RESTClient
from coinbase.websocket import (WSClient, WSClientConnectionClosedException,
                                WSClientException)
from models.signals import AuroxSignal, FuturePriceAtSignal
from models.futures import CoinbaseFuture, AccountBalanceSummary, FuturePosition
from db import db, db_errors, or_
from dotenv import load_dotenv
from pprint import pprint as pp
import datetime
import pytz
import os
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

    def __init__(self, flask_app):
        print(":Initializing CoinbaseAdvAPI:")
        self.flask_app = flask_app
        self.client = RESTClient(api_key=API_KEY, api_secret=API_SECRET)

    def get_portfolios(self):
        print(":get_portfolio_breakdown:")

        get_portfolios = self.client.get_portfolios()
        # print("get_portfolios", get_portfolios)

        uuid = get_portfolios['portfolios'][0]['uuid']
        print("uuid", uuid)

        return uuid

    def get_portfolio_breakdown(self, portfolio_uuid):
        print(":get_portfolio_breakdown:")

        get_portfolio_breakdown = self.client.get_portfolio_breakdown(portfolio_uuid=portfolio_uuid)
        print("get_portfolio_breakdown", get_portfolio_breakdown)

        return

    def get_product(self, product_id="BTC-USDT"):
        print(":get_product:")

        get_product = self.client.get_product(product_id=product_id)
        print("get_product:", get_product)

        return get_product

    def list_products(self, product_type="FUTURE"):
        # print(":list_products:")

        get_products = self.client.get_products(product_type=product_type)
        # print("get_products:", get_products)

        return get_products

    def store_btc_futures_products(self, future_products):
        # print(":store_btc_futures_products:")
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
                        contract_expiry = datetime.datetime.strptime(
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
                        print(f"Failed to add future product {future['product_id']}: {e}")
                        db.session.rollback()

    def get_current_future_product(self, product_id):
        print(":get_current_future_product:")

        with self.flask_app.app_context():
            # Check if the future product already exists in the database
            future_product = CoinbaseFuture.query.filter_by(product_id=product_id).first()
            # print("\nfound future_product:", future_product)

        return future_product

    def get_balance_summary(self):
        print(":get_balance_summary:")

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
        print(':store_futures_balance_summary:')

        balance_summary_data = data['balance_summary']
        # pp(balance_summary_data)

        with self.flask_app.app_context():  # Push an application context
            try:
                # Try to find the existing balance summary, assuming only one record exists
                existing_balance_summary = AccountBalanceSummary.query.limit(1).all()
                # print("existing_balance_summary:", existing_balance_summary)

                if existing_balance_summary:
                    # Update existing record
                    existing_balance_summary[0].available_margin = float(balance_summary_data['available_margin']['value'])
                    existing_balance_summary[0].cbi_usd_balance = float(balance_summary_data['cbi_usd_balance']['value'])
                    existing_balance_summary[0].cfm_usd_balance = float(balance_summary_data['cfm_usd_balance']['value'])
                    existing_balance_summary[0].daily_realized_pnl = float(balance_summary_data['daily_realized_pnl']['value'])
                    existing_balance_summary[0].futures_buying_power = float(balance_summary_data['futures_buying_power']['value'])
                    existing_balance_summary[0].initial_margin = float(balance_summary_data['initial_margin']['value'])
                    existing_balance_summary[0].liquidation_buffer_amount = float(
                        balance_summary_data['liquidation_buffer_amount']['value'])
                    existing_balance_summary[0].liquidation_buffer_percentage = int(
                        balance_summary_data['liquidation_buffer_percentage'])
                    existing_balance_summary[0].liquidation_threshold = float(
                        balance_summary_data['liquidation_threshold']['value'])
                    existing_balance_summary[0].total_open_orders_hold_amount = float(
                        balance_summary_data['total_open_orders_hold_amount']['value'])
                    existing_balance_summary[0].total_usd_balance = float(balance_summary_data['total_usd_balance']['value'])
                    existing_balance_summary[0].unrealized_pnl = float(balance_summary_data['unrealized_pnl']['value'])
                    print("Updated existing balance summary")
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
                        total_open_orders_hold_amount=float(balance_summary_data['total_open_orders_hold_amount']['value']),
                        total_usd_balance=float(balance_summary_data['total_usd_balance']['value']),
                        unrealized_pnl=float(balance_summary_data['unrealized_pnl']['value']),
                    )
                    db.session.add(new_balance_summary)
                    print("Stored new balance summary")

                # Commit the changes to the database
                db.session.commit()
                print("Balance summary updated or created successfully.")
            except Exception as e:
                print(f"Failed to add/update balance summary {balance_summary_data}: {e}")
                db.session.rollback()

        print("Balance summary stored")

    @staticmethod
    def get_current_short_month_uppercase():
        # Get the current datetime
        current_date = datetime.datetime.now()

        # Format the month to short format and convert it to uppercase
        short_month = current_date.strftime('%b').upper()

        return short_month

    def get_this_months_future(self):
        # print(":get_this_months_future:")

        # Find this months future product
        with self.flask_app.app_context():
            # Get the current month's short name in uppercase
            short_month = self.get_current_short_month_uppercase()
            # print(f"Searching for futures contracts for the month: {short_month}")

            # Search the database for a matching futures contract
            future_entry = CoinbaseFuture.query.filter(
                CoinbaseFuture.display_name.contains(short_month)
            ).first()

            if future_entry:
                # print("\nFound future entry:", future_entry)
                return future_entry
            else:
                print("\n   No future entry found for this month.")
                return None

    def list_orders(self, product_id, order_status, product_type="FUTURE"):
        print(":list_orders:")

        list_orders = self.client.list_orders(order_status=order_status,
                                              product_id=product_id, product_type=product_type)
        # pp(list_orders)

        # Use if we have a lot of orders
        # get_orders['has_next']

        # for order in list_orders['orders']:
        #     # pp(order)
        #     # print("\n")
        #
        #     client_order_id = order['client_order_id']
        #     created_time = order['created_time']
        #     product_id = order['product_id']
        #     time_in_force = order['time_in_force']
        #     order_id = order['order_id']
        #     outstanding_hold_amount = order['outstanding_hold_amount']
        #     pending_cancel = order['pending_cancel']
        #     total_value_after_fees = order['total_value_after_fees']
        #
        #     if 'limit_limit_gtc' in order['order_configuration']:
        #         base_size = order['order_configuration']['limit_limit_gtc']['base_size']
        #         limit_price = order['order_configuration']['limit_limit_gtc']['limit_price']
        #         post_only = order['order_configuration']['limit_limit_gtc']['post_only']
        #         # print("base_size:", base_size)
        #         # print("limit_price:", limit_price)
        #         # print("post_only:", post_only)
        #     else:
        #         pass
        #         # print(order['order_configuration'])
        #     # print("client_order_id:", client_order_id)
        #     # print("created_time:", created_time)
        #     # print("product_id:", product_id)
        #     # print("time_in_force:", time_in_force)
        #     # print("order_id:", order_id)
        #     # print("outstanding_hold_amount:", outstanding_hold_amount)
        #     # print("pending_cancel:", pending_cancel)
        #     # print("total_value_after_fees:", total_value_after_fees)
        #     # print("total_value_after_fees:", total_value_after_fees)

        return list_orders

    def store_orders(self, orders):
        print(":store_orders:")

    def list_future_positions(self):
        print(":list_future_positions:")

        list_futures_positions = self.client.list_futures_positions()
        # pp(list_futures_positions)

        # for future in list_futures_positions['positions']:
        #     # print("list future:", future)
        #     print("list future product_id:", future['product_id'])
        #     print("list future expiration_time:", future['expiration_time'])
        #     print("list future number_of_contracts:", future['number_of_contracts'])
        #     print("list future side:", future['side'])
        #     print("list future current_price:", future['current_price'])
        #     print("list future avg_entry_price:", future['avg_entry_price'])
        #     print("list future unrealized_pnl:", future['unrealized_pnl'])
        #     print("list future number_of_contracts:", future['number_of_contracts'])

        return list_futures_positions

    def store_future_positions(self, p_list_futures_positions):
        print(":store_future_positions:")
        # print("p_list_futures_positions:", p_list_futures_positions)
        # Clear existing positions
        with self.flask_app.app_context():  # Push an application context
            try:
                if p_list_futures_positions and 'positions' in p_list_futures_positions and p_list_futures_positions['positions']:
                    # Clear existing positions
                    db.session.query(FuturePosition).delete()
                    for future in p_list_futures_positions['positions']:
                        # pp(future)
                        new_position = FuturePosition(
                            product_id=future['product_id'],
                            expiration_time=datetime.datetime.strptime(future['expiration_time'], "%Y-%m-%dT%H:%M:%SZ"),
                            side=future['side'],
                            number_of_contracts=int(future['number_of_contracts']),
                            current_price=float(future['current_price']),
                            avg_entry_price=float(future['avg_entry_price']),
                            unrealized_pnl=float(future['unrealized_pnl']),
                            daily_realized_pnl=float(future.get('daily_realized_pnl', 0))  # Handle optional fields
                        )
                        db.session.add(new_position)
                    db.session.commit()
                    print("Future positions updated.")
            except db_errors as e:
                db.session.rollback()
                # self.flask_app.logger.error(f"Error storing future positions: {e}")
                print(f"Error storing future positions: {e}")
            except ValueError as e:
                db.session.rollback()
                # self.flask_app.logger.error(f"Data conversion error: {e}")
                print(f"Data conversion error: {e}")
            except Exception as e:
                db.session.rollback()
                # self.flask_app.logger.error(f"Unexpected error: {e}")
                print(f"Unexpected error: {e}")

    def get_future_position(self, product_id):
        print(":get_future_position:")

        get_futures_positions = self.client.get_futures_position(product_id=product_id)
        # print("get_futures_positions:", get_futures_positions)

        return get_futures_positions

    def get_current_bid_ask_prices(self, product_id):
        print(":get_current_future_price:")

        get_bid_ask = self.client.get_best_bid_ask(product_ids=product_id)
        # print("get_bid_ask", get_bid_ask)

        return get_bid_ask

    @staticmethod
    def generate_uuid4():
        return uuid.uuid4()

    def create_order(self, side, product_id, size, limit_price, leverage="3", order_type='market_market_ioc'):
        print(":create_order:")

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

        # quote_size
        # Amount of quote currency to spend on order. Required for BUY orders.

        # base_size
        # Amount of base currency to spend on order. Required for SELL orders.

        # limit_price
        # Ceiling price for which the order should get filled.

        # A unique UUID that we make (should store and not repeat, must be in UUID format
        # TODO: Need to store this value in the DB
        # Generate and print a UUID4
        client_order_id = self.generate_uuid4()
        print("Generated client_order_id:", client_order_id)

        order_configuration = {
            "order_configuration": {
                order_type: {}
            },
            "side": side,
            "leverage": leverage
        }
        if side == "BUY":
            order_configuration['order_configuration'][order_type]["quote_size"] = str(size)
        elif side == "SELL":
            order_configuration['order_configuration'][order_type]["base_size"] = str(size)

        if 'limit' in order_type:
            order_configuration['order_configuration'][order_type]["limit_price"] = limit_price
            order_configuration['order_configuration'][order_type]["post_only"] = "false"
        print("order_configuration:", order_configuration)

        # TODO: Store in database

        order_created = self.client.create_order(client_order_id=client_order_id,
                                                 product_id=product_id,
                                                 side=side,
                                                 order_configuration=order_configuration)
        # TODO: Store in database

        print("order_created:", order_created)

        return order_created

    def edit_order(self, side, product_id):
        print(":edit_order:")

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
        close_position = self.client.close_position(client_order_id=client_order_id,
                                                    product_id=product_id,
                                                    size=contract_size)
        print("close:", close_position)

        return close_position


class TradeManager:

    def __init__(self, flask_app):
        print(":Initializing TradeManager:")
        self.flask_app = flask_app
        self.cb_adv_api = CoinbaseAdvAPI(flask_app)

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
        # Also write a record using the signal spot price, futures bid and ask
        #   and store the relationship ids to both
        with self.flask_app.app_context():  # Push an application context
            try:
                signal_spot_price = data['price'].replace(',', '')

                new_signal = AuroxSignal(
                    timestamp=data['timestamp'],
                    price=signal_spot_price,  # Remove commas for numeric processing if necessary
                    signal=data['signal'],
                    trading_pair=data['trading_pair'],
                    time_unit=data['timeUnit'],
                    # message=data.get('message')  # Use .get for optional fields
                )

                # Add new_signal to the session and commit it
                db.session.add(new_signal)
                # db.session.commit()
                db.session.flush()  # Flush to assign an ID to new_signal without committing transaction

                print("New signal stored:", new_signal)

                #
                # Now, get the bid and ask prices for the current futures product
                #
                current_future_product = self.cb_adv_api.get_this_months_future()
                # print(" current_future_product:", current_future_product)
                # print(" current_future_product product_id:", current_future_product.product_id)

                # Get the current bid and ask prices for the futures product related to this signal
                future_bid_ask_price = self.cb_adv_api.get_current_bid_ask_prices(current_future_product.product_id)
                future_bid_price = future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
                future_ask_price = future_bid_ask_price['pricebooks'][0]['asks'][0]['price']

                # Find the related futures product based on the current futures product
                # Assuming the current futures product maps directly to product_id in your CoinbaseFuture model
                if current_future_product:
                    # Create a FuturePriceAtSignal record linking the new signal and the futures product
                    new_future_price = FuturePriceAtSignal(
                        signal_spot_price=signal_spot_price,
                        future_bid_price=future_bid_price,
                        future_ask_price=future_ask_price,
                        signal_id=new_signal.id,
                        future_id=current_future_product.id
                    )
                    db.session.add(new_future_price)
                    print("Associated bid/ask prices stored for the signal")

                db.session.commit()

            except db_errors as e:
                print(f"Error fetching latest daily signal: {str(e)}")
                return None

    def get_latest_weekly_signal(self):
        print(":get_latest_weekly_signal:")
        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .filter(AuroxSignal.time_unit == '1 Week') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            return latest_signal

    def get_latest_daily_signal(self):
        print(":get_latest_daily_signal:")
        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .filter(AuroxSignal.time_unit == '1 Day') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            return latest_signal

    def compare_last_daily_to_todays_date(self):
        print(":compare_last_daily_to_todays_date:")
        latest_signal = self.get_latest_daily_signal()
        if latest_signal:
            # Strip the 'Z' and parse the datetime
            signal_time = datetime.datetime.fromisoformat(latest_signal.timestamp.rstrip('Z'))

            # Ensuring it's UTC
            signal_time = signal_time.replace(tzinfo=pytz.utc)

            now = datetime.datetime.now(pytz.utc)  # Current time in UTC

            # Calculate time difference
            time_diff = now - signal_time

            # Check if the difference is less than or equal to 24 hours
            if time_diff <= datetime.timedelta(days=1):
                print("Within 24 hours, proceed to place trade.")
                return True
            else:
                print("More than 24 hours since the last signal, wait for the next one.")
        else:
            print("No daily signal found.")

    def check_for_contract_expires(self):
        print(":check_for_contract_expires:")

        # NOTE: Futures markets are open for trading from Sunday 6 PM to
        #  Friday 5 PM ET (excluding observed holidays),
        #  with a 1-hour break each day from 5 PM – 6 PM ET

        list_future_products = self.cb_adv_api.list_products("FUTURE")
        current_month = self.cb_adv_api.get_current_short_month_uppercase()
        self.cb_adv_api.store_btc_futures_products(list_future_products)
        current_future_product = self.cb_adv_api.get_this_months_future()
        # print(" current_future_product:", current_future_product.product_id)

        if current_future_product:
            # Make sure contract_expiry is timezone-aware
            contract_expiry = current_future_product.contract_expiry.replace(tzinfo=pytz.utc)
            # print("Contract expiry:", contract_expiry)

            # Current time in UTC
            now = datetime.datetime.now(pytz.utc)
            # print("Now:", now)

            # Calculate time difference
            time_diff = contract_expiry - now
            # print("total_seconds:", time_diff.total_seconds())

            # Check if the contract has expired
            if time_diff.total_seconds() <= 0:
                print("Contract has expired, close trades.")
                # Here you would add code to handle closing trades
                print(">>> Close out any positions!!!")
            else:
                days = time_diff.days
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(
                    f"\nContract for:"
                    f"  {current_future_product.product_id}\n"
                    f"  Month: {current_month} \n"
                    f"  expires in {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds.")
        else:
            print(" No future product found for this month.")

    def tracking_current_position_profit_loss(self):
        print(":tracking_current_position_profit_loss:")

        current_future = self.cb_adv_api.get_this_months_future()
        future_position = self.cb_adv_api.get_future_position(product_id=current_future.product_id)

        # Only run if we have ongoing positions
        if future_position['position']:
            current_future_product = self.cb_adv_api.get_current_future_product(current_future.product_id)
            contract_size = future_position['position']['number_of_contracts']
            print(" contract_size:", contract_size)

            product_contract_size = current_future_product.contract_size
            avg_entry_price = float(future_position['position']['avg_entry_price']) * product_contract_size
            current_price = float(future_position['position']['current_price']) * product_contract_size
            # print("avg_entry_price:", avg_entry_price)
            # print("current_price:", current_price)

            calc_profit_or_loss = round(avg_entry_price - current_price, 4)
            # print(f"    calc_profit_or_loss: ${calc_profit_or_loss}")

            # Percentage change: (New Value - Original Value) / Original Value × 100
            calc_percentage = round((avg_entry_price - current_price) / current_price * 100, 3)
            # print(f"    calc_percentage: %{calc_percentage}")

            print("Contract Expires on", future_position['position']['expiration_time'])

            # Check when the product contract expires and print it out
            self.check_for_contract_expires()

            print(">>> Profit / Loss:")
            if calc_percentage >= 2:
                print(f"    Take profit at 2% or higher %{calc_percentage}")
                print(f"    Good Profit: ${calc_profit_or_loss}")

                # client_order_id = '4ef6c115-c5c7-4915-89d1-077b56e79c31'
                # self.cb_adv_api.close_position(client_order_id, current_future.product_id, contract_size)

            elif 2 > calc_percentage > 0.5:
                print(f"    Not ready to take profit %{calc_percentage}")
                print(f"    Ok Profit: ${calc_profit_or_loss}")
            elif 0.5 >= calc_percentage >= 0:
                print(f"    Neutral  %{calc_percentage}")
                print(f"    Not enough profit: ${calc_profit_or_loss}")
            elif calc_percentage < 0:
                print(f"    Trade negate %{calc_percentage}")
                print(f"    No profit, loss of: ${calc_profit_or_loss}")
        else:
            print(f"    No open positions: {future_position}")


if __name__ == "__main__":
    print(__name__)

    # TODO: Need to switch to RESTClient calls
    # TODO: Need to track orders OPEN and FILLED (keep updated_
    # TODO: Do we need the websocket to watch prices?

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
