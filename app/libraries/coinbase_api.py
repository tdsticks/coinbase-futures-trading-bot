from coinbase.rest import RESTClient
from app.models import db, set_db_errors, and_
from app.models.futures import (CoinbaseFuture, AccountBalanceSummary,
                                FuturePosition, FuturesOrder, FuturesCandleData)
from dotenv import load_dotenv
import calendar
from datetime import datetime, timedelta
import pytz
from pprint import pprint as pp
import uuid

load_dotenv()


class CoinbaseAdvAPI:

    def __init__(self, app):
        # print(":Initializing CoinbaseAdvAPI:")
        self.log = app.custom_log.log
        self.log(True, "D", None, ":Initializing CoinbaseAdvAPI:")

        self.app = app
        self.db_errors = set_db_errors

        api_key = self.app.config['API_KEY']
        api_secret = self.app.config['API_SECRET']
        # UUID = self.app.config['UUID']

        self.current_price = 0

        self.client = RESTClient(api_key=api_key, api_secret=api_secret, verbose=False)

    @staticmethod
    def parse_datetime(date_str):
        """Parse an ISO 8601 datetime string to a formatted datetime string for SQLite."""
        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        return None

    def get_portfolios(self):
        # print(":get_portfolio_breakdown:")
        self.log(True, "I", None, ":get_portfolio_breakdown:")

        get_portfolios = self.client.get_portfolios()
        # print("get_portfolios", get_portfolios)

        uuid = get_portfolios['portfolios'][0]['uuid']
        print("uuid", uuid)

        return uuid

    def get_portfolio_breakdown(self, portfolio_uuid):
        # print(":get_portfolio_breakdown:")
        self.log(True, "I", None, ":get_portfolio_breakdown:")

        get_portfolio_breakdown = self.client.get_portfolio_breakdown(portfolio_uuid=portfolio_uuid)
        # print("get_portfolio_breakdown", get_portfolio_breakdown)
        self.log(True, "I", "get_portfolio_breakdown", get_portfolio_breakdown)

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
        self.log(True, "D", None,
                 ":store_futures_balance_summary:")

        balance_summary_data = data['balance_summary']
        # pp(balance_summary_data)

        with self.app.app_context():  # Push an application context
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
                    # self.app.db.session.add(new_balance_summary)
                    db.session.add(new_balance_summary)
                    # print("Stored new balance summary")

                # Commit the changes to the database
                # self.app.db.session.commit()
                db.session.commit()
                # print("Balance summary updated or created successfully.")
            except Exception as e:
                self.log(True, "E",
                         "Failed to add/update balance summary",
                         balance_summary_data, e)
                # self.app.db.session.rollback()
                db.session.rollback()
        # print("Balance summary stored")

    def get_product(self, product_id="BTC-USDT"):
        # print(":get_product:")
        # self.log(True, "D", None, ":get_product:")

        get_product = self.client.get_product(product_id=product_id)
        # print("get_product:", get_product)
        # self.log(True, "I", "get_product", get_product)

        return get_product

    def list_products(self, product_type="FUTURE"):
        self.log(True, "D", None, ":list_products:")
        # self.log(True, "I", "product_type", product_type)
        # self.log(True, "I", "self.client", self.client)

        get_products = self.client.get_products(product_type=product_type)
        # self.log(True, "I", "get_products", get_products)

        return get_products

    def check_for_contract_expires(self):
        self.log(True, "D", None, ":check_for_contract_expires:")

        # NOTE: Futures markets are open for trading from Sunday 6 PM to
        #  Friday 5 PM ET (excluding observed holidays),
        #  with a 1-hour break each day from 5 PM – 6 PM ET

        # Get the futures contract from Coinbase API
        list_future_products = self.list_products("FUTURE")

        if 'products' in list_future_products:
            # self.log(True, "I",
            #          "  Products Exist", len(list_future_products['products']))
            self.store_btc_futures_products(list_future_products)

        # Get the current month's contract
        current_future_product = self.get_relevant_future_from_db()
        self.log(True, "I",
                 "   Current Future Product",
                 current_future_product.product_id)

        current_month = self.get_current_short_month_uppercase()
        self.log(True, "I",
                 "   Current Month", current_month)

        next_month = self.get_next_short_month_uppercase()
        self.log(True, "I",
                 "   Next Month", next_month)

        if current_future_product:
            contract_expiry = current_future_product.contract_expiry.replace(tzinfo=pytz.utc)
            now = datetime.now(pytz.utc)
            time_diff = contract_expiry - now

            days, seconds = time_diff.days, time_diff.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60

            # contract_grace_days = 3
            contract_grace_days = self.app.config['GRACE_DAYS']

            # FOR TESTING ONLY
            # days = 10

            # Check if the contract has expired
            if time_diff.total_seconds() <= 0:
                self.log(True, "W", None, "-----------------------------------")
                self.log(True, "W", None, ">>> Contract has expired!")
                self.log(True, "W", None, ">>> Close out any positions!!!")
                self.log(True, "W", None, "-----------------------------------")
                self.log(True, "I", None, "Switching to next month's contract.")

                # Identify and switch to the next contract
                next_month_product, next_month = self.find_next_month_contract(list_future_products, next_month)

                if next_month_product:
                    self.log(True, "I",
                             "   > next_month_product.product_id",
                             next_month_product['product_id'])
                    return next_month_product['product_id'], next_month
            elif days <= contract_grace_days:
                # If the contract expires in less than or equal to 3 days
                contract_msg = (f"  > Contract {current_future_product.product_id} is close to expiring"
                                f" in {days} days, {hours} hours, and {minutes} minutes.")
                self.log(True, "I", None, contract_msg)
                self.log(True, "I", None, "  > Switching to next month's contract.")

                # Identify and switch to the next contract
                next_month_product, next_month = self.find_next_month_contract(list_future_products, next_month)

                if next_month_product:
                    self.log(True, "I",
                             "   > next_month_product.product_id",
                             next_month_product['product_id'])
                    return next_month_product['product_id'], next_month
            else:
                contract_msg = (f"  Current contract {current_future_product.product_id} is safe to trade. "
                                f"It expires in {days} days, {hours} hours, and {minutes} minutes.")
                self.log(True, "I", None, contract_msg)
                return None, None
        else:
            self.log(True, "I", None, "  !!! No current future product found")
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

    def store_btc_futures_products(self, future_products):
        self.log(True, "D", None, ":store_btc_futures_products:")

        for future in future_products['products']:
            # print("future product:", future)
            if 'BTC' in future['future_product_details']['contract_root_unit']:
                # self.log(True, "D", "future product", future)

                with self.app.app_context():  # Push an application context
                    try:
                        # Convert necessary fields
                        product_id = future['product_id']
                        price = float(future['price']) if future['price'] else None
                        price_change_24h = float(future['price_percentage_change_24h']) if future[
                            'price_percentage_change_24h'] else None
                        volume_24h = float(future['volume_24h']) if future['volume_24h'] else None
                        volume_change_24h = float(future['volume_percentage_change_24h']) if future[
                            'volume_percentage_change_24h'] else None
                        # self.log(True, "I", "contract_expiry", future['future_product_details']['contract_expiry'])
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

                            # self.app.db.session.add(future_entry)
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

                        # self.app.db.session.commit()
                        db.session.commit()

                    except Exception as e:
                        # print(f"Failed to add future product {future['product_id']}: {e}")
                        self.log(True, "E",
                                 "Failed to add future product",
                                 future['product_id'],
                                 e)

                        # self.app.db.session.rollback()
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
        # self.log(True, "D", None,
        #                         ":get_relevant_future_from_db:")

        # Find this months future product
        with self.app.app_context():

            # Get the current month's short name in uppercase
            short_month = self.get_current_short_month_uppercase()

            if month_override:
                short_month = month_override

            self.log(True, "I", "   Getting for futures contracts for the month", short_month)

            # Search the database for a matching futures contract
            future_contract = CoinbaseFuture.query.filter(
                CoinbaseFuture.display_name.contains(short_month)
            ).first()

            if future_contract:
                # print("\nFound future entry:", future_entry)
                self.log(True, "I",
                         "       Found future contract", future_contract.product_id)
                return future_contract
            else:
                # print("\n   No future entry found for this month.")
                self.log(True, "W",
                         None, " >>> No future contract found for this month.")
                return None

    def list_future_positions(self):
        self.log(True, "D", None,
                 ":list_future_positions:")

        list_futures_positions = self.client.list_futures_positions()
        # pp(list_futures_positions)

        return list_futures_positions

    def get_future_position(self, product_id: str):
        self.log(True, "D", None,
                 ":get_future_position:")

        get_futures_positions = self.client.get_futures_position(product_id=product_id)
        # pp(get_futures_positions)

        return get_futures_positions

    def store_future_positions(self, p_list_futures_positions):
        # self.log(True, "D", None,
        #              ":store_future_positions:")
        # pp(p_list_futures_positions)

        # Clear existing positions
        with (self.app.app_context()):  # Push an application context
            try:
                if p_list_futures_positions and 'positions' in p_list_futures_positions:
                    # Clear existing positions
                    # self.app.db.session.query(FuturePosition).delete()
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
                        # self.app.db.session.add(new_position)
                        db.session.add(new_position)

                    # self.app.db.session.commit()
                    db.session.commit()

                    self.log(True, "I", None,
                             "  > Open Future position updated")
            except self.db_errors as e:
                # self.app.db.session.rollback()
                db.session.rollback()
                self.log(True, "E", "Error storing future position", e)
            except ValueError as e:
                # self.app.db.session.rollback()
                db.session.rollback()
                self.log(True, "E", "Data conversion error", e)
            except Exception as e:
                # self.app.db.session.rollback()
                db.session.rollback()
                self.log(True, "E", "Unexpected error", e)

    def get_current_bid_ask_prices(self, product_id):
        # self.log(True, "D", None, ":get_current_bid_ask_prices:")

        get_bid_ask = self.client.get_best_bid_ask(product_ids=product_id)
        # print("get_bid_ask", get_bid_ask)

        return get_bid_ask

    def get_current_market_trades(self, product_id):
        self.log(True, "D", None, ":get_current_market_trades:")

        get_market_trades = self.client.get_public_market_trades(
            product_id=product_id,
            limit=1)
        # print("get_market_trades", get_market_trades)

        return get_market_trades

    def get_current_average_price(self, product_id):
        # self.log(True, "D", None, ":get_current_future_price:")

        # Get Current Bid Ask Prices
        cur_future_bid_ask_price = self.get_current_bid_ask_prices(product_id)
        cur_future_bid_price = cur_future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
        cur_future_ask_price = cur_future_bid_ask_price['pricebooks'][0]['asks'][0]['price']
        cur_prices_msg = (f"    Prd: {product_id} - "
                          f"Current Futures: Bid: ${cur_future_bid_price} "
                          f"Ask: ${cur_future_ask_price}")
        self.log(True, "I", None, cur_prices_msg)

        cur_future_avg_price = (int(cur_future_bid_price) + int(cur_future_ask_price)) / 2
        # self.log(True, "I",
        #                         "   Current Future Avg Price", cur_future_avg_price)

        return cur_future_bid_price, cur_future_ask_price, cur_future_avg_price

    def get_candles(self, product_id, start=None, end=None):
        self.log(True, "D", None, ":get_candles:")
        """
            start = datetime(2023, 5, 1)
            end = datetime(2023, 5, 2)
        """
        granularity = "ONE_MINUTE"
        # granularity = "FIVE_MINUTE"

        # Get today if we don't have a start and end time
        if start is None and end is None:
            start = datetime.now() - timedelta(hours=1)
            end = datetime.now()
        start_time = start - timedelta(hours=1)
        end_time = end
        self.log(True, "D", None, f"start: {start}, end: {end}")

        start_unix_time = str(int(start_time.timestamp()))
        end_unix_time = str(int(end_time.timestamp()))
        self.log(True, "D", None, f"start_time: {start_time}, end_time: {end_time}")

        get_candles = self.client.get_candles(product_id=product_id, start=start_unix_time,
                                              end=end_unix_time, granularity=granularity)
        # self.log(True, "I", "get_candles", get_candles['candles'])

        return get_candles

    # Example function to save candle data to the database
    def save_futures_candles_to_db(self, product_id, candles):
        self.log(True, "D", None, ":save_futures_candles_to_db:")

        with self.app.app_context():
            for candle in reversed(candles['candles']):
                try:
                    start_time = datetime.fromtimestamp(int(candle['start']))
                    low = float(candle['low'])
                    high = float(candle['high'])
                    open_ = float(candle['open'])
                    close = float(candle['close'])
                    volume = float(candle['volume'])

                    # Check if the record already exists
                    existing_candle = FuturesCandleData.query.filter_by(product_id=product_id, start_time=start_time).first()

                    if existing_candle:
                        # Update the existing record
                        existing_candle.low = low
                        existing_candle.high = high
                        existing_candle.open = open_
                        existing_candle.close = close
                        existing_candle.volume = volume
                        # self.log(True, "I", "Updated existing candle", existing_candle)
                    else:
                        # Create a new record
                        new_candle = FuturesCandleData(
                            product_id=product_id,
                            start_time=start_time,
                            low=low,
                            high=high,
                            open=open_,
                            close=close,
                            volume=volume
                        )
                        db.session.add(new_candle)
                        # self.log(True, "I", "Added new candle", new_candle)
                    db.session.commit()
                except Exception as e:
                    self.log(True, "I", "Error processing candle", candle, f"Error: {e}")
                    db.session.rollback()

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
        self.log(True, "D", "create_order")
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
        enable_order_creation = self.app.config['ENABLE_ORDER_CREATION']

        # Live trading enabled
        if enable_order_creation:
            self.log(True, "W", "Enable Order Creation", enable_order_creation)

            # NOTE: A unique UUID that we make (should store and not repeat, must be in UUID format
            # Generate and print a UUID4
            client_order_id = self.generate_uuid4()
            # print("Generated client_order_id:", client_order_id, type(client_order_id))

            # Convert UUID to a string
            client_order_id_str = str(client_order_id)
            # print("Client Order ID as string:", client_order_id_str)

            order_created = {}

            quote_size = ''
            base_size = ''
            post_only = False
            order_type_db_record = 'LIMIT'  # Default
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
            #     order_type_db_record = 'MARKET'  # Default
            #     order_created = self.client.market_order_buy(client_order_id=client_order_id_str,
            #                                                  product_id=product_id,
            #                                                  # leverage=leverage,
            #                                                  quote_size=quote_size)
            #
            # elif side == "SELL" and order_type == 'market_market_ioc':
            #     order_type_db_record = 'MARKET'  # Default
            #     order_created = self.client.market_order_sell(client_order_id=client_order_id_str,
            #                                                   product_id=product_id,
            #                                                   # leverage=leverage,
            #                                                   base_size=base_size)
            self.log(True, "I", "Order Created - bot_note", bot_note)
            # pp(order_created)

            if order_created.get('success'):
                self.log(True, "I", None, "Order successfully created")
                self.log(True, "D", "success_response", order_created.get('success_response'))

            if order_created.get('failure_reason'):
                self.log(True, "I", None, "Order creation failed")
                self.log(True, "D", "Failure", order_created.get('failure_reason'))

                if order_created.get('error_response'):
                    self.log(True, "E", "Failure - Error Message",
                             order_created.get('error_response').get('message'))
                    self.log(True, "E", "Failure - Error Details",
                             order_created.get('error_response').get('error_details'))
                elif order_created.get('success'):
                    self.log(True, "I", None, "Failure -  Order successfully created")
                    self.log(True, "D", "Failure - success_response",
                             order_created.get('success_response'))
                else:
                    self.log(True, "D", "No detailed error message provided.")

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
                "order_status": "OPEN",
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
            self.log(True, "W", "   >>> Order Creation Disabled")

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
        # self.log(True, "I", None, "get_current_take_profit_order_from_db")

        open_futures = None

        # NOTE: We should only get one if we're only trading one future (BTC)

        with self.app.app_context():  # Push an application context
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
                    # self.log(True, "I", "All open_futures", open_futures)
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
                    # self.log(True, "I", "One open_futures", open_futures)

                return open_futures
            except Exception as e:
                self.log(True, "E",
                         "Database error getting", msg1=e)
        # print("open_futures:", open_futures)
        return open_futures

    def get_dca_filled_orders_from_db(self, dca_side: str):
        # self.log(True, "I", None,
        #                         "get_dca_filled_orders_from_db")
        dca_total_filled_price = 0
        # dca_avg_filled_price = 0
        dca_count = 0  # This includes the MAIN initial order
        dca_total_base_size = 0
        quantity = self.app.config['LADDER_QUANTITY']
        # self.log(True, "I", "    quantity", quantity)

        # dca_note_list = ['DCA1', 'DCA2', 'DCA3', 'DCA4', 'DCA5']
        dca_note_list = ["DCA" + str(x) for x in range(1, quantity + 1)]
        # self.log(True, "I", "    dca_note_list", dca_note_list)

        for i, dca in enumerate(dca_note_list):
            # print("dca_note_list - i:", i)
            dca_order = self.get_current_take_profit_order_from_db(order_status="FILLED",
                                                                   side=dca_side, bot_note=dca,
                                                                   get_all_orders=False)
            if dca_order:
                # self.log(True, "I", "dca_order", dca_order)
                # self.log(True, "I", "    dca_order.limit_price", dca_order.limit_price)
                # self.log(True, "I", "    dca_order.average_filled_price", dca_order.average_filled_price)

                dca_base_size = int(dca_order.base_size)
                # self.log(True, "I", "    dca_base_size", dca_base_size)

                dca_filled_total = int(dca_order.average_filled_price) * dca_base_size
                # self.log(True, "I", "    dca_filled_total", dca_filled_total)

                dca_count += 1
                dca_total_base_size += dca_base_size

                # Get the total filled price (avg filled price + contract size)
                dca_total_filled_price += round(dca_filled_total)
                # self.log(True, "I", "    DCA Total Filled Price 1", dca_total_filled_price)

        # self.log(True, "I", "    DCA Total Filled Price 2", dca_total_filled_price)
        # self.log(True, "I", "    DCA Total Base Size", dca_total_base_size)
        # self.log(True, "I", "    DCA Count", dca_count)

        if dca_count > 0:
            dca_total_filled_price = round(dca_total_filled_price)
        # self.log(True, "I", "    DCA Total Filled Price 1", dca_total_filled_price)

        return dca_total_filled_price, dca_total_base_size

    def cancel_order(self, order_ids: list):
        self.log(True, "D", "cancel_order")
        # self.log(True, "I", "    order_ids", order_ids)

        cancelled_order = None
        if len(order_ids) > 0:
            cancelled_order = self.client.cancel_orders(order_ids=order_ids)
            # self.log(True, "I", "cancelled_order", cancelled_order)
        else:
            pass
            # self.log(True, "W", " !!! No order ids to cancel")
        return cancelled_order

    def update_cancelled_orders(self):
        self.log(True, "I",
                 None, ":update_cancelled_orders:")

        with self.app.app_context():  # Push an application context
            try:
                # Search the database for a matching futures contract
                cancelled_futures = FuturesOrder.query.filter(
                    and_(
                        FuturesOrder.order_status == 'CANCELLED',
                        FuturesOrder.creation_origin == "bot_order",
                        FuturesOrder.bot_active == 1,
                    )
                ).all()
                self.log(True, "I", "cancelled_futures", cancelled_futures)

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
                        self.log(True, "I",
                                 "updated_cancelled_order",
                                 updated_cancelled_order)
            except Exception as e:
                self.log(True, "E",
                         "Database error getting", msg1=e)

    def update_bot_active_orders(self):
        # self.log(True, "I",
        #              None, "update_bot_active_orders")

        with self.app.app_context():  # Push an application context
            try:
                # Search the database for a matching futures contract
                bot_active_orders = FuturesOrder.query.filter(
                    and_(
                        FuturesOrder.creation_origin == "bot_order",
                        FuturesOrder.bot_active == 1,
                    )
                ).all()
                self.log(True, "I",
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
                        self.log(True, "I",
                                 "updated_bot_active_order",
                                 updated_bot_active_order)
            except Exception as e:
                self.log(True, "E",
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
        self.log(True, "D", None, ":store_order:")
        # self.log(True, "I", "order_data", order_data)

        with self.app.app_context():  # Push an application context
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
                        order.order_status = order_data['order_status']
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
                        # self.app.db.session.add(order)
                        db.session.add(order)

                    # Commit changes or new entry to the database
                    # self.app.db.session.commit()
                    db.session.commit()

                    order_stored = f"    Order Client ID:{client_order_id} processed: {'updated' if order.id else 'created'}"
                    self.log(True, "I", None, order_stored)
                else:
                    self.log(True, "I", None,
                             " No order ID provided or storing order failed. Check input data.")
            except self.db_errors as e:
                self.log(True, "I",
                         "    Error either getting or storing the Order record",
                         str(e))

                # self.app.db.session.rollback()
                db.session.rollback()

                return None

    def store_or_update_orders_from_api(self, orders_data):
        # self.log(True, "D", None, ":store_or_update_orders_from_api:")

        for order in orders_data['orders']:
            # pp(order)

            with self.app.app_context():  # Ensure you're within the Flask app context
                # Try to find an existing order by order_id
                existing_order = FuturesOrder.query.filter_by(order_id=order.get('order_id')).first()
                # self.log(True, "I", "existing order", existing_order)

                if existing_order:
                    pass
                    # print("\nUpdating existing order:", existing_order.order_id)
                else:
                    # print("\nCreating new order with order_id:", order.get('order_id'))
                    existing_order = FuturesOrder()  # Create a new instance if not found
                    # self.app.db.session.add(existing_order)
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
                    # self.app.db.session.commit()
                    db.session.commit()
                    # print("Order stored or updated successfully.")
                except Exception as e:
                    # self.app.db.session.rollback()
                    db.session.rollback()
                    self.log(True, "E",
                             "Failed to store or update order", (e))

    def update_order_fields(self, client_order_id: str, field_values: dict = None):
        self.log(True, "D", None, ":update_order_fields:")
        # self.log(True, "I", "field_values", field_values)

        with self.app.app_context():  # Push an application context
            try:
                if client_order_id:
                    # Query for an existing order
                    order = FuturesOrder.query.filter_by(client_order_id=client_order_id).first()
                    self.log(True, "I", "    found order", order)

                    if order and field_values:
                        # Order exists, update its details
                        for field, value in field_values.items():
                            # self.log(True, "I", "field", field)
                            # self.log(True, "I", "value", value)

                            # Set the order field with the value
                            # Dynamically set the attribute based on field name
                            setattr(order, field, value)

                        # Commit changes or new entry to the database
                        # self.app.db.session.commit()
                        db.session.commit()
                        self.log(True, "I", "Order Client ID",
                                 client_order_id, "  field values updated")

                        return "    Successfully updated order record"
                else:
                    self.log(True, "W", None,
                             "No Client Order ID provided or order creation failed. Check input data.")
                    return f"   No Client Order ID provided client_order_id: {client_order_id}"
            except self.db_errors as e:
                self.log(True, "E",
                         "    Error either getting or storing the Order record",
                         str(e))
                # self.app.db.session.rollback()
                db.session.rollback()
                return "    update_order_fields - Database Error"

    def close_position(self, client_order_id, product_id, contract_size):
        self.log(True, "I", None, ":close_position:")
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
        self.log(True, "I", "close", close_position)

        return close_position
