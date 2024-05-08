import configparser
import os
from datetime import datetime, time
import logs
import pytz
from dotenv import load_dotenv

# Custom Libraries
from coinbase_api import CoinbaseAdvAPI
from signals_processor import SignalProcessor
from email_manager import EmailManager

# Models
from models.futures import (FuturePosition)

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
UUID = os.getenv('UUID')

config = configparser.ConfigParser()
config.read('bot_config.ini')
config.sections()


class TradeManager:

    def __init__(self, flask_app, mail_cls):
        # print(":Initializing TradeManager:")
        self.flask_app = flask_app
        self.log = logs.Log(flask_app)  # Send to Log or Console or both
        self.email_mgr = EmailManager(flask_app, mail_cls)
        self.cb_adv_api = CoinbaseAdvAPI(flask_app, mail_cls)
        self.signal_processor = SignalProcessor(flask_app, self.cb_adv_api)
        self.log.log(True, "D", None, ":Initializing TradeManager:")

    def check_for_contract_expires(self):
        self.log.log(True, "D", None,
                     ":NEW_check_for_contract_expires:")

        # NOTE: Futures markets are open for trading from Sunday 6 PM to
        #  Friday 5 PM ET (excluding observed holidays),
        #  with a 1-hour break each day from 5 PM – 6 PM ET

        # Get the futures contract from Coinbase API
        list_future_products = self.cb_adv_api.list_products("FUTURE")
        self.cb_adv_api.store_btc_futures_products(list_future_products)

        # Get the current month's contract
        current_future_product = self.cb_adv_api.get_relevant_future_from_db()
        self.log.log(True, "I",
                     "   Current Future Product",
                     current_future_product.product_id)

        current_month = self.cb_adv_api.get_current_short_month_uppercase()
        self.log.log(True, "I",
                     "   Current Month", current_month)

        next_month = self.cb_adv_api.get_next_short_month_uppercase()
        self.log.log(True, "I",
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
                self.log.log(True, "W", None, "-----------------------------------")
                self.log.log(True, "W", None, ">>> Contract has expired!")
                self.log.log(True, "W", None, ">>> Close out any positions!!!")
                self.log.log(True, "W", None, "-----------------------------------")
                self.log.log(True, "I", None, "Switching to next month's contract.")

                # Identify and switch to the next contract
                next_month_product, next_month = self.find_next_month_contract(list_future_products, next_month)

                if next_month_product:
                    self.log.log(True, "I",
                                 "   > next_month_product.product_id",
                                 next_month_product['product_id'])
                    return next_month_product['product_id'], next_month
            elif days <= contract_grace_days:
                # If the contract expires in less than or equal to 3 days
                contract_msg = (f"  > Contract {current_future_product.product_id} is close to expiring"
                                f" in {days} days, {hours} hours, and {minutes} minutes.")
                self.log.log(True, "I", None, contract_msg)
                self.log.log(True, "I", None, "  > Switching to next month's contract.")

                # Identify and switch to the next contract
                next_month_product, next_month = self.find_next_month_contract(list_future_products, next_month)

                if next_month_product:
                    self.log.log(True, "I",
                                 "   > next_month_product.product_id",
                                 next_month_product['product_id'])
                    return next_month_product['product_id'], next_month
            else:
                contract_msg = (f"  Current contract {current_future_product.product_id} is safe to trade. "
                                f"It expires in {days} days, {hours} hours, and {minutes} minutes.")
                self.log.log(True, "I", None, contract_msg)
                return None, None
        else:
            self.log.log(True, "I", None, "  !!! No current future product found")
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
        self.log.log(True, "D", None, "||||||||||||||||||||||||")
        self.log.log(True, "D", None, ":ladder_orders:")

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
        self.log.log(True, "I", "cur_future_price", cur_future_price)

        # dca_note_list = ['DCA1', 'DCA2', 'DCA3', 'DCA4', 'DCA5']
        dca_note_list = ["DCA" + str(x) for x in range(1, quantity + 1)]
        self.log.log(True, "I", "    dca_note_list",
                     dca_note_list)

        # Generate the DCA percentages list dynamically based on 'quantity'
        # dca_per_offset_list = [0.01, 0.02, 0.03, 0.04, 0.05]
        dca_per_offset_list = [
            float(config['dca.ladder.trade_percentages'][f'dca_trade_{i + 1}_per'])
            for i in range(quantity)
        ]
        self.log.log(True, "I", "    dca_per_offset_list",
                     dca_per_offset_list)

        dca_contract_size_list = [
            str(config['dca.ladder.trade_percentages'][f'dca_trade_{i + 1}_contracts'])
            for i in range(quantity)
        ]
        self.log.log(True, "I", "    dca_contract_size_list",
                     dca_contract_size_list)

        def create_dca_orders():
            for i, note in enumerate(dca_note_list):
                if i <= quantity - 1:
                    dcg_limit_price = ""
                    dca_trade_per_offset = int(float(cur_future_price) * dca_per_offset_list[i])
                    self.log.log(True, "D",
                                 "   DCA Trade Per Offset",
                                 dca_trade_per_offset)

                    # Calculate the DCA orders (Long or Short)
                    if side == "BUY":  # BUY / LONG
                        dcg_limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                            int(cur_future_price) - dca_trade_per_offset)
                        self.log.log(True, "D",
                                     "   > Buy Long dcg_limit_price: $",
                                     dcg_limit_price)

                    elif side == "SELL":  # SELL / SHORT
                        dcg_limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                            int(cur_future_price) + dca_trade_per_offset)
                        self.log.log(True, "D",
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
                    self.log.log(True, "D", "DCA order_created!", dca_order_created)

        create_dca_orders()

    def is_trading_time(self, current_time):
        self.log.log(True, "I", None, "---> Checking for open market...")
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
            self.log.log(True, "I", None, " >>> Futures market is OPEN! <<<")
            return True
        elif is_sunday_after_6pm or is_friday_before_5pm:
            self.log.log(True, "I", None, " >>> Futures market is OPEN! <<<")
            return True
        self.log.log(True, "W", None, " >>> Futures market is CLOSED. <<<")
        return False

    def check_trading_conditions(self):
        self.log.log(True, "D", None, "--------------------------")
        self.log.log(True, "D", None, ":check_trading_conditions:")

        # Update any cancelled orders in the database (in case we close things manually, etc.)
        self.cb_adv_api.update_cancelled_orders()

        #######################
        # Do we have an existing trades?
        #######################

        next_months_product_id, next_month = self.check_for_contract_expires()
        if next_months_product_id:
            self.log.log(True, "I", "Next Months Product ID", next_months_product_id)
            self.log.log(True, "I", "Next Month", next_month)

        # Get Current Positions from API, we just need to acknowledge this position exists
        #  and get the position side
        future_positions = self.cb_adv_api.list_future_positions()
        # print("Future Positions:")
        # pp(future_positions)

        fifteen_min_signals = self.signal_processor.get_latest_fifteen_min_signal()

        trading_permitted, trade_direction, groups = self.signal_processor.run()
        self.log.log(True, "I", " >>> Trade Permitted", trading_permitted)
        self.log.log(True, "I", " >>> Trade Direction", trade_direction)
        # self.log.log(True, "I", " >>> Group Data", groups)
        # for group in groups:
        #     self.log.log(True, "I", " >>> Group Data", groups[group])

        # Make sure we have a future position
        if len(future_positions['positions']) > 0:
            self.log.log(True, "I", None, "  >>> We have an ACTIVE position(s) <<<")

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
            # self.log.log(True, "I", "Cur Position Order", cur_position_order)

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
                        # self.log.log(True, "I", "positions", positions)
                        for position in positions:
                            self.tracking_current_position_profit_loss(position, cur_position_order, next_month)
                            self.track_take_profit_order(position, cur_position_order)

                    except Exception as e:
                        self.log.log(True, "E", "Unexpected error:", msg1=e)
            else:
                self.log.log(True, "W",
                             "    >>> NO Current Position Order Found", cur_position_order)
        else:
            self.log.log(True, "I", None, " >>> No Open Position")
            self.log.log(True, "I", None,
                         " >>> Check if its a good market to place a trade")

            # NOTE: Check to cancel any OPEN orders and cancel them

            future_contract = self.cb_adv_api.get_relevant_future_from_db()
            remaining_open_orders = self.cb_adv_api.list_orders(product_id=future_contract.product_id,
                                                                order_status="OPEN")
            if 'orders' in remaining_open_orders:
                self.log.log(True, "D",
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
                self.log.log(True, "I", "    > cancelled_order", cancelled_order)

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
                    self.log.log(True, "I", "    > updated_cancelled_order", updated_cancelled_order)

                # Now, update an other Future Order records setting bot_active = 0
                self.cb_adv_api.update_bot_active_orders()

            #
            # If our overall position trade direction isn't neutral, then proceed
            #
            if trade_direction != "neutral":
                self.log.log(True, "I", None,
                             "-----------------------------------")
                if trade_direction == 'long':
                    self.log.log(True, "I", None,
                                 " >>> Signals are strong bullish, "
                                 "see if we should place a trade on the 15 min")
                else:
                    self.log.log(True, "I", None,
                                 " >>> Signals are strong bearish, "
                                 "see if we should place a trade on the 15 min")

                # NOTE: Next, let's look at the fifteen minute and how close to the
                #  last signal and price of when we should place a limit order.
                #  How are in price are we away from the last signal?
                #  What is a good price threshold?
                #  Is 15 Minute signal side the same as the signal_calc_trade_direction side?

                fifteen_min_trade_signal = fifteen_min_signals.signal
                self.log.log(True, "I", None, " >>> 15 Min Signal Direction", fifteen_min_trade_signal)
                self.log.log(True, "I", None, " >>> Trade Signal Direction", trade_direction)

                # NOTE: Does the 15 Min match the overall signal trade direction of the Aurox signals?

                if fifteen_min_trade_signal == trade_direction:
                    self.log.log(True, "I", None,
                                 "   >>> YES, the 15 Min matches the overall trade direction")

                    # Check to see if next months product id is populated
                    if next_months_product_id is None:
                        # Get this months current product
                        relevant_future_product = self.cb_adv_api.get_relevant_future_from_db()
                        self.log.log(True, "I", "    Relevant Future Product",
                                     relevant_future_product.product_id)
                        product_id = relevant_future_product.product_id
                    else:
                        product_id = next_months_product_id

                    bid_price, ask_price, avg_price = self.cb_adv_api.get_current_average_price(product_id=product_id)
                    self.log.log(True, "I",
                                 "   bid ask avg_price", avg_price)

                    limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(avg_price)
                    self.log.log(True, "I",
                                 "   Current Limit Price", limit_price)

                    fifteen_min_future_avg_price = 0
                    for future_price in fifteen_min_signals.future_prices:
                        future_bid_price = future_price.future_bid_price
                        future_ask_price = future_price.future_ask_price
                        fifteen_min_future_avg_price = round((future_bid_price + future_ask_price) / 2)
                    self.log.log(True, "I",
                                 "   Fifteen Min Future Avg Price",
                                 fifteen_min_future_avg_price)

                    # Just setting a high default number to check again
                    percentage_diff = 10

                    # LONG = BUY
                    # SHORT = SELL
                    trade_side = ""

                    # The signal price should be lower than current price (price rising)
                    check_signal_and_current_price_diff = 0
                    if trade_direction == 'long':
                        trade_side = "BUY"
                        check_signal_and_current_price_diff = int(limit_price) - int(fifteen_min_future_avg_price)
                        percentage_diff = round((check_signal_and_current_price_diff
                                                 / int(fifteen_min_future_avg_price)) * 100, 2)

                    elif trade_direction == 'short':
                        trade_side = "SELL"
                        check_signal_and_current_price_diff = int(fifteen_min_future_avg_price) - int(limit_price)
                        percentage_diff = round((check_signal_and_current_price_diff
                                                 / int(fifteen_min_future_avg_price)) * 100, 2)

                    # NOTE: Make sure the price difference from the 15 Min signal and current price
                    #   isn't too far off or beyond 1%, so we try to be safe and get more profit

                    # Set a limit value is here (1 = 1%)
                    # percentage_diff_limit = 1
                    percentage_diff_limit = float(config['trade.conditions']['percentage_diff_limit'])
                    per_diff_msg = (f"   >>> Checking! Signal Direction "
                                    f"{trade_direction} "
                                    f" Per Diff {percentage_diff}% < {percentage_diff_limit}% Limit")
                    self.log.log(True, "I", None, per_diff_msg)

                    if percentage_diff < percentage_diff_limit:
                        good_per_diff_msg = (f"   >>> Proceeding! current price diff of "
                                             f"{check_signal_and_current_price_diff} "
                                             f"which is {percentage_diff}%")
                        self.log.log(True, "W", None, good_per_diff_msg)

                        size = "1"
                        leverage = "3"
                        order_type = "limit_limit_gtc"
                        order_msg = (f"    >>> Trade side:{trade_side} Order type:{order_type} "
                                     f"Limit Price:{limit_price} Size:{size} Leverage:{leverage}")
                        self.log.log(True, "I", None, order_msg)

                        # Create a new MAIN order
                        order_created = self.cb_adv_api.create_order(side=trade_side,
                                                                     product_id=product_id,
                                                                     size=size,
                                                                     limit_price=limit_price,
                                                                     leverage=leverage,
                                                                     order_type=order_type,
                                                                     bot_note="MAIN")
                        print("MAIN order_created:", order_created)

                        email_body = (f"New Order Placed!"
                                      f"\nTrade side:{trade_side}"
                                      f"\nOrder type:{order_type} "
                                      f"\nLimit Price:{limit_price}"
                                      f"\nSize:{size}"
                                      f"\nLeverage:{leverage}")
                        self.email_mgr.send_email(subject="New Order Placed!",
                                                  body=email_body)

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
                        self.log.log(True, "W", None, bad_per_diff_msg)
                else:
                    self.log.log(True, "W", None,
                                 "   >>> NO, the 15 Min does not match the overall trade direction")
                    fifteen_min_pos_trade_dir_msg = (f"     >>> 15 Min Signal: {fifteen_min_trade_signal} "
                                                     f"!= Signal Trade Direction: {trade_direction}")
                    self.log.log(True, "W", None,
                                 fifteen_min_pos_trade_dir_msg)
            else:
                self.log.log(True, "W", None,
                             "\nSignal score is neutral, let's wait...", )
                for group in groups:
                    self.log.log(True, "I", "   >>> ", group, "\n")
                    self.log.log(True, "I", "       > Direction", groups[group]['direction'], "\n")
                    self.log.log(True, "I", "       > Strength", groups[group]['strength'], "\n")
                    self.log.log(True, "I", "       > Score", groups[group]['score'], "\n")
                    self.log.log(True, "I", "       > Normalized Score",
                                 groups[group]['normalized_score'], "\n")
                    self.log.log(True, "I", "\n")

    def place_trade_and_ladder(self):
        self.log.log(True, "D", None, "--------------------------")
        self.log.log(True, "D", None, ":place_trade_and_ladder:")

    def tracking_current_position_profit_loss(self, position, order, next_month):
        self.log.log(True, "D", None, "---------------------------------------")
        self.log.log(True, "D", None, ":tracking_current_position_profit_loss:")

        # print(" position:", position)
        # print(" order:", order)

        # Only run if we have ongoing positions
        if position:
            product_id = position.product_id
            self.log.log(True, "I", "  position.product_id:", product_id)

            side = position.side
            self.log.log(True, "I", "  position.side:", side)

            # print("next_month:", next_month)
            # self.log.log(True, "I", "  next_month:", next_month)

            relevant_future_product = self.cb_adv_api.get_relevant_future_from_db(month_override=next_month)
            product_contract_size = relevant_future_product.contract_size
            # self.log.log(True, "I", "  product_contract_size:", product_contract_size)

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
                self.log.log(True, "I", "    dca_count", dca_count)
                self.log.log(True, "I", "    dca_avg_filled_price", dca_avg_filled_price)

                # Get the average filled price from the Future Order
                avg_filled_price = round((int(order.average_filled_price) + dca_avg_filled_price) / dca_count)
                self.log.log(True, "I", "    avg_filled_price", avg_filled_price)

                # Get the current price from the Future Position
                current_price = round(int(position.current_price), 2)
                # self.log.log(True, "I", "    current_price", current_price)

                number_of_contracts = position.number_of_contracts
                # self.log.log(True, "I", "    number_of_contracts", number_of_contracts)

                # Calculate total cost and current value per contract
                total_initial_cost = avg_filled_price * number_of_contracts * product_contract_size
                total_current_value = current_price * number_of_contracts * product_contract_size
                # self.log.log(True, "I", "  total_initial_cost", total_initial_cost)
                # self.log.log(True, "I", "  total_current_value", total_current_value)

                # Calculate profit or loss for all contracts
                # NOTE: We need to factor in what side of the market: long or short
                calc_profit_or_loss = 0
                if position.side.lower() == 'long':  # Assuming 'buy' denotes a long position
                    calc_profit_or_loss = round(total_current_value - total_initial_cost, 4)
                elif position.side.lower() == 'short':  # Assuming 'sell' denotes a short position
                    calc_profit_or_loss = round(total_initial_cost - total_current_value, 4)
                # self.log.log(True, "I", "  calc_profit_or_loss", calc_profit_or_loss)

                if total_initial_cost != 0:  # Prevent division by zero
                    calc_percentage = round((calc_profit_or_loss / total_initial_cost) * 100, 4)
                else:
                    calc_percentage = 0
                self.log.log(True, "I", "  calc_percentage:", calc_percentage)

                # print("Contract Expires on", future_position['position']['expiration_time'])
                # print(" Contract Expires on", position.expiration_time)

                self.log.log(True, "I", None, ">>>>>>>>>>>>>>>>>>>>>>>>>>>")
                self.log.log(True, "I", None, ">>> Profit / Loss <<<")
                self.log.log(True, "I", "Product Id", product_id)
                self.log.log(True, "I", "Position Side", side)
                self.log.log(True, "I", "Avg Entry Price $", avg_filled_price)
                self.log.log(True, "I", "Current Price $", current_price)
                self.log.log(True, "I", "# of Contracts", number_of_contracts)
                if calc_percentage >= 2:
                    self.log.log(True, "I", "Take profit at 2% or higher %", calc_percentage)
                    self.log.log(True, "I", "Good Profit $", calc_profit_or_loss)
                elif 2 > calc_percentage > 0.5:
                    self.log.log(True, "I", "Not ready to take profit %", calc_percentage)
                    self.log.log(True, "I", "Ok Profit $", calc_profit_or_loss)
                elif 0.5 >= calc_percentage >= 0:
                    self.log.log(True, "I", "Neutral %", calc_percentage)
                    self.log.log(True, "I", "Not enough profit $", calc_profit_or_loss)
                elif calc_percentage < 0:
                    self.log.log(True, "I", "Trade negative %", calc_percentage)
                    self.log.log(True, "I", "No profit, loss of $", calc_profit_or_loss)
                self.log.log(True, "I", None, ">>>>>>>>>>>>>>>>>>>>>>>>>>>")
            else:
                self.log.log(True, "W", "No open order", order)
        else:
            self.log.log(True, "W", "No open positions", position)

    def track_take_profit_order(self, position, order):
        self.log.log(True, "D", None, "-------------------------")
        self.log.log(True, "D", None, ":track_take_profit_order:")

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
            # self.log.log(True, "I", "position.side", side)

            # If we're LONG, then we need to place a profitable BUY order
            if side == "LONG":  # BUY / LONG
                take_profit_side = "SELL"
                dca_side = "BUY"
            # If we're SHORT, then we need to place a profitable SELL order
            elif side == "SHORT":  # SELL / SHORT
                take_profit_side = "BUY"
                dca_side = "SELL"
            self.log.log(True, "I", "    take_profit_side", take_profit_side)

            # TODO: Need to test if the average price changes based on more positions (contracts)
            #   This may need to be adjusted back to using the Position record vs the Order record
            #   if more contracts are bought

            # Now, get the ALL Future Orders from the DB so we have more accurate data
            take_profit_order = self.cb_adv_api.get_current_take_profit_order_from_db(
                order_status="OPEN", side=take_profit_side, bot_note="TAKE_PROFIT", get_all_orders=True)
            # self.log.log(True, "I", "  > take_profit_order exists 1", take_profit_order)

            # BUG: Need to fix duplicate Take Profit orders, creating work around for now

            # NOTE: If we have more than one Take Profit, keep one and cancel the rest

            if len(take_profit_order) > 1:
                # Loop through all of the take profit orders, except one (we keep that)
                for tp in range(0, len(take_profit_order) - 1):
                    loop_tp_order = take_profit_order[tp]
                    loop_tp_order_id = loop_tp_order.order_id
                    loop_tp_client_order_id = loop_tp_order.client_order_id
                    # self.log.log(True, "I", "    >>> tp", tp, loop_tp_order)
                    # self.log.log(True, "I", "    tp.order_id", loop_tp_order_id)

                    # Pass the order_id as a list. Can place multiple order ids if necessary, but not in this case
                    cancelled_order = self.cb_adv_api.cancel_order(order_ids=[loop_tp_order_id])
                    self.log.log(True, "I",
                                 "    Cancelled Extra Order", cancelled_order)
                    field_values = {
                        "bot_active": 0,
                        "order_status": "CANCELLED"
                    }
                    # Update order so we don't the system doesn't try to use it for future orders
                    updated_cancelled_order = self.cb_adv_api.update_order_fields(
                        client_order_id=loop_tp_client_order_id,
                        field_values=field_values)
                    self.log.log(True, "I",
                                 "    Updated Extra Cancelled Order", updated_cancelled_order)

            # Run this again to get only one take profit order
            take_profit_order = self.cb_adv_api.get_current_take_profit_order_from_db(
                order_status="OPEN", side=take_profit_side, bot_note="TAKE_PROFIT", get_all_orders=False)
            # self.log.log(True, "I",
            #                         "   > take_profit_order exists 1.5", take_profit_order)

            # Now see if we have a take profit order already open
            if take_profit_order is not None:
                # self.log.log(True, "I", "  > take_profit_order exists 2", take_profit_order)
                existing_take_profit_order = True
            else:
                existing_take_profit_order = False
                self.log.log(True, "W", "    No take_profit_order", take_profit_order)

            # NOTE: Find all the FILLED DCA orders to get the average price

            number_of_contracts = position.number_of_contracts
            # self.log.log(True, "I", "    Number Of Contracts", number_of_contracts)

            dca_avg_filled_price, dca_avg_filled_price_2, dca_count = self.cb_adv_api.get_dca_filled_orders_from_db(
                dca_side=dca_side)
            self.log.log(True, "I", "    DCA Count", dca_count)
            # self.log.log(True, "I", "    DCA Avg Filled Price", dca_avg_filled_price)
            # self.log.log(True, "I", "    DCA Avg dca_avg_filled_price_2 Price", dca_avg_filled_price_2)

            main_order_avg_filled_price = int(order.average_filled_price)
            # self.log.log(True, "I", "    MAIN Order Avg Filled Price", main_order_avg_filled_price)

            avg_filled_price = round((main_order_avg_filled_price + dca_avg_filled_price) / dca_count)
            # self.log.log(True, "I", "    ALL ORDERS Avg Filled Price", avg_filled_price)

            avg_filled_price_2 = round((main_order_avg_filled_price + dca_avg_filled_price_2) / number_of_contracts)
            # self.log.log(True, "I", "    ALL ORDERS Avg Filled Price 2", avg_filled_price_2)

            # take_profit_percentage = 0.01
            take_profit_percentage = float(config['take.profit.order']['take_profit_percentage'])
            tp_per_msg = f" Take Profit Percentage: {take_profit_percentage * 100}%"
            self.log.log(True, "I", None, tp_per_msg)

            # Calculate the take profit price (Long or Short)
            take_profit_offset_price = int(float(avg_filled_price) * take_profit_percentage)
            # self.log.log(True, "I", "     Take Profit Offset Price", take_profit_offset_price)

            # Calculate the take profit price (Long or Short)
            take_profit_offset_price_2 = int(float(avg_filled_price_2) * take_profit_percentage)
            # self.log.log(True, "I", "     Take Profit Offset Price 2", take_profit_offset_price_2)

            take_profit_price = ""

            # If we're LONG, then we need to place a profitable SELL order
            if side == "LONG":  # BUY / LONG
                take_profit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                    int(avg_filled_price) + take_profit_offset_price_2)
                self.log.log(True, "I", "    > SELL Short take_profit_price: $",
                             take_profit_price)

            # If we're SHORT, then we need to place a profitable BUY order
            elif side == "SHORT":  # SELL / SHORT
                take_profit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                    int(avg_filled_price) - take_profit_offset_price_2)
                self.log.log(True, "I", "    > BUY Long take_profit_price: $",
                             take_profit_price)

            order_type = "limit_limit_gtc"

            # If we don't have an existing take profit order, create one
            if existing_take_profit_order is False:
                self.log.log(True, "I", None,
                             "  >>> Create new take_profit_order")

                # Take Profit Order
                order_created = self.cb_adv_api.create_order(side=take_profit_side,
                                                             product_id=product_id,
                                                             size=number_of_contracts,
                                                             limit_price=take_profit_price,
                                                             leverage='',
                                                             order_type=order_type,
                                                             bot_note="TAKE_PROFIT")
                self.log.log(True, "I", None,
                             "   >>> TAKE_PROFIT order_created!")
                self.log.log(True, "I", "    >>> Order:", order_created)

            else:  # Otherwise, let's edit and update the order based on the market and position(s)
                self.log.log(True, "I", None,
                             "  >>> Check Existing Take Profit Order...")
                # pp(take_profit_order)
                tp_order_id = take_profit_order.order_id
                tp_client_order_id = take_profit_order.client_order_id
                # self.log.log(True, "I", "tp_order_id", tp_order_id)
                # self.log.log(True, "I", "tp_client_order_id", tp_client_order_id)

                # For limit GTC orders only
                size = take_profit_order.base_size
                # self.log.log(True, "I", "take_profit_order size", size)

                # See if we need to update the size based on the existing number of
                # contracts in the position
                if int(number_of_contracts) > int(size):
                    new_size = number_of_contracts
                    self.log.log(True, "W",
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
                self.log.log(True, "I",
                             "    Check Price Size Msg", check_price_size_msg)

                # Check to see if either price or size don't match
                if (int(limit_price) != int(take_profit_price)) is True or (int(base_size) != int(new_size)) is True:
                    self.log.log(True, "I", None,
                                 "   >>> Either the prices are off or the contract sizes are off")
                    self.log.log(True, "I", None,
                                 "   >>> Cancel the existing take profit or and place a new one!")

                    # NOTE: Cancel the existing take profit order, update it's db record,
                    #  then place a new take profit with the the updated price and size

                    if len(tp_order_id) > 0:
                        # Pass the order_id as a list. Can place multiple order ids if necessary, but not in this case
                        cancelled_order = self.cb_adv_api.cancel_order(order_ids=[tp_order_id])
                        self.log.log(True, "I",
                                     "    cancelled_order", cancelled_order)

                        field_values = {
                            "bot_active": 0,
                            "order_status": "CANCELLED"
                        }
                        # Update order so we don't the system doesn't try to use it for future orders
                        updated_cancelled_order = self.cb_adv_api.update_order_fields(
                            client_order_id=tp_client_order_id,
                            field_values=field_values)
                        self.log.log(True, "I",
                                     "    updated_cancelled_order", updated_cancelled_order)

                    self.log.log(True, "I", None,
                                 "   >>> Creating new order with updated PRICE or SIZE settings!")
                    # Take Profit Order
                    take_profit_order_created = self.cb_adv_api.create_order(side=take_profit_side,
                                                                             product_id=product_id,
                                                                             size=new_size,
                                                                             limit_price=take_profit_price,
                                                                             leverage='',
                                                                             order_type=order_type,
                                                                             bot_note="TAKE_PROFIT")
                    self.log.log(True, "I",
                                 "   >>> take_profit_order_created", take_profit_order_created)
                else:
                    self.log.log(True, "I", None,
                                 "   ...No changes with take profit order in PRICE or SIZE...")
        else:
            self.log.log(True, "W",
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
