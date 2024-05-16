from datetime import time
import pytz
from dotenv import load_dotenv

# Models
from app.models.futures import FuturePosition

load_dotenv()


class TradeManager:

    def __init__(self, app):
        # print(":Initializing TradeManager:")
        self.log = app.custom_log.log
        self.log(True, "D", None, ":Initializing TradeManager:")

        self.app = app
        self.email_mgr = app.email_manager
        self.cb_adv_api = app.cb_adv_api
        self.signal_processor = app.signal_processor
        self.avg_filled_price = None  # Set this for trailing take profit
        self.take_profit_side = ""  # Set this for trailing take profit

    def ladder_orders(self, side: str, product_id: str, bid_price, ask_price,
                      quantity: int = 5, manual_price: str = ''):
        self.log(True, "D", None, "||||||||||||||||||||||||")
        self.log(True, "D", None, ":ladder_orders:")

        # Prevent more than 10
        # if quantity > 10:
        #     quantity = 10

        # NOTE: This is part of our strategy in placing DCA limit orders if the trade goes against us,
        #   even though both the Weekly and Daily signals are in our favor. This not only helps
        #   cover the volatility of the market and all the effects it, it also can help be more profitable
        #   if we're carefully. We also need to adjust the closing Long or Short order we'll place to
        #   help with risk management and taking profit.

        # size = "1"
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
        # self.log(True, "I", "cur_future_price", cur_future_price)

        # dca_note_list = ['DCA1', 'DCA2', 'DCA3', 'DCA4', 'DCA5']
        dca_note_list = ["DCA" + str(x) for x in range(1, quantity + 1)]
        # self.log(True, "I", "    dca_note_list", dca_note_list)

        # Generate the DCA percentages list dynamically based on 'quantity'
        # dca_per_offset_list = [0.01, 0.02, 0.03, 0.04, 0.05]
        dca_per_offset_list = [
            # float(config['dca.ladder.trade_percentages'][f'dca_trade_{i + 1}_per'])
            self.app.config['DCA_TRADE_PERCENTAGES'][i]
            for i in range(quantity)
        ]
        # self.log(True, "I", "    dca_per_offset_list",
        #              dca_per_offset_list)

        dca_contract_size_list = [
            # str(config['dca.ladder.trade_percentages'][f'dca_trade_{i + 1}_contracts'])
            self.app.config['DCA_CONTRACTS'][i]
            for i in range(quantity)
        ]

        # self.log(True, "I", "    dca_contract_size_list",
        #              dca_contract_size_list)

        def create_dca_orders():
            for i, note in enumerate(dca_note_list):
                if i <= quantity - 1:
                    dcg_limit_price = ""
                    dca_trade_per_offset = int(float(cur_future_price) * dca_per_offset_list[i])
                    # self.log(True, "D",
                    #              "   DCA Trade Per Offset",
                    #              dca_trade_per_offset)

                    # Calculate the DCA orders (Long or Short)
                    if side == "BUY":  # BUY / LONG
                        dcg_limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                            int(cur_future_price) - dca_trade_per_offset)
                        self.log(True, "D",
                                 "   > Buy Long dcg_limit_price: $",
                                 dcg_limit_price)

                    elif side == "SELL":  # SELL / SHORT
                        dcg_limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                            int(cur_future_price) + dca_trade_per_offset)
                        self.log(True, "D",
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
                    self.log(True, "D", "DCA order_created!", dca_order_created)

        create_dca_orders()

    def is_trading_time(self, current_time):
        self.log(True, "I", None, "---> Checking for open market...")
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
            self.log(True, "I", None, " >>> Futures market is OPEN! <<<")
            return True
        elif is_sunday_after_6pm or is_friday_before_5pm:
            self.log(True, "I", None, " >>> Futures market is OPEN! <<<")
            return True
        self.log(True, "W", None, " >>> Futures market is CLOSED. <<<")
        return False

    def check_trading_conditions(self):
        self.log(True, "D", None, "--------------------------")
        self.log(True, "D", None, ":check_trading_conditions:")

        # Update any cancelled orders in the database (in case we close things manually, etc.)
        self.cb_adv_api.update_cancelled_orders()

        #######################
        # Do we have an existing trades?
        #######################

        next_months_product_id, next_month = self.cb_adv_api.check_for_contract_expires()

        if next_months_product_id:
            self.log(True, "I", "Next Months Product ID", next_months_product_id)
            self.log(True, "I", "Next Month", next_month)

        # Get Current Positions from API, we just need to acknowledge this position exists
        #  and get the position side
        future_positions = self.cb_adv_api.list_future_positions()
        # print("Future Positions:")
        # pp(future_positions)

        # Get our 5 min and 15 min signals for matching against later
        five_min_signals = self.signal_processor.get_latest_five_min_signal()
        fifteen_min_signals = self.signal_processor.get_latest_fifteen_min_signal()
        thirty_min_signals = self.signal_processor.get_latest_thirty_min_signal()

        # Get our signal data (trading condition, direction and signal groups)
        trading_permitted, trade_direction, groups = self.signal_processor.run()
        self.log(True, "I", " >>> Trade Permitted", trading_permitted)
        self.log(True, "I", " >>> Trade Direction", trade_direction)

        enable_main_order_creation = self.app.config['ENABLE_MAIN_ORDER_CREATION']
        self.log(True, "I", " >>> MAIN Order Creation Enabled", enable_main_order_creation)

        # Make sure we have a future position
        if len(future_positions['positions']) > 0:
            self.log(True, "I", None, "  >>> ACTIVE TRADING POSITION FOUND <<<")

            position_side = future_positions['positions'][0]['side']
            # print("position_side:", position_side)

            # Clear and store the active future position
            self.cb_adv_api.store_future_positions(future_positions)

            side = ""
            if position_side == "LONG":
                side = "BUY"
            elif position_side == "SHORT":
                side = "SELL"

            # Now, get the MAIN Order(s) from the DB so we have more accurate data
            main_position_orders = self.cb_adv_api.get_current_take_profit_order_from_db(
                order_status="FILLED", side=side, bot_note="MAIN", get_all_orders=True)
            # self.log(True, "I", "Main Position Orders", main_position_orders)

            amount_of_main_orders = len(main_position_orders)
            # self.log(True, "I", "Amount of MAIN Orders", amount_of_main_orders)

            # Check to see if we have multiple main orders
            if amount_of_main_orders > 0:
                self.log(True, "I", "Amount of MAIN Orders > 0", amount_of_main_orders)
                # Assign the first order of the array to be the main order to work with
                main_position_order = main_position_orders[0]
            else:
                main_position_order = main_position_orders
            # self.log(True, "I", "Main Position Order", main_position_order)

            main_base_size = 0
            main_avg_filled_price = 0

            # If we have multiple main orders by accident, let's consolidate values
            #   for calculating later
            for pos_order in main_position_orders:
                # Make sure the order was settled before adding
                if int(pos_order.settled) == 1:
                    # base_size = pos_order.base_size
                    main_base_size += int(pos_order.filled_size)
                    main_avg_filled_price += int(pos_order.average_filled_price)

            main_total_filled_price = main_avg_filled_price

            # Average out all the MAIN order filled price and base size
            #   Set these to strings for later use
            main_avg_filled_price = str(int(main_avg_filled_price / amount_of_main_orders))
            main_base_size = str(main_base_size)
            # self.log(True, "I", "MAIN Total Filled Price Total", main_total_filled_price)
            # self.log(True, "I", "MAIN Average Filled Price Total", main_avg_filled_price)
            # self.log(True, "I", "MAIN Amount of Base Size Total", main_base_size)

            # Now, reassign the main order the updated values for calculating later
            main_position_order.total_filled_price = main_total_filled_price
            main_position_order.average_filled_price = main_avg_filled_price
            main_position_order.base_size = main_base_size

            # Make sure we have a FILLED order from our position
            if main_position_order:
                # Get the position from the database
                # NOTE: We should only get one if we're only trading one future (BTC)
                with (self.app.app_context()):  # Push an application context
                    try:
                        # NOTE: position doesn't have the all most accurate data we need, so
                        #  we uses the order to help supplement what we need
                        positions = FuturePosition.query.all()
                        # self.log(True, "I", "positions", positions)
                        for position in positions:
                            # If we have both a MAIN order and active position
                            #   then run the profit loss and take profit methods
                            self.tracking_current_position_profit_loss(position, main_position_order, next_month)
                            self.track_take_profit_order(position, main_position_order)

                    except Exception as e:
                        self.log(True, "E", "Unexpected error:", msg1=e)
            else:
                self.log(True, "W",
                         "    >>> NO Main Position Order Found", main_position_order)
        else:
            self.log(True, "I", None, " >>> No Open Position")
            if trading_permitted:
                self.log(True, "I", None, " >>> Trading permitted, "
                                          "check if its a good market to place a trade")

                # NOTE: Check to cancel any OPEN orders and cancel them

                future_contract = self.cb_adv_api.get_relevant_future_from_db()

                # If we don't have an open position, then let's clean up any OPEN orders
                #   to start fresh
                remaining_open_orders = self.cb_adv_api.list_orders(product_id=future_contract.product_id,
                                                                    order_status="OPEN")

                # Loop through all the OPEN orders to close them out
                #   If we're trying to place our first order (MAIN), this
                #   should cancel it out and reattempt to place it further down the code
                #   and not place extra MAIN orders
                if 'orders' in remaining_open_orders:

                    order_ids = []
                    client_order_ids = []

                    if len(remaining_open_orders['orders']) > 0:
                        self.log(True, "I",
                                 "Remaining Open Orders Count",
                                 len(remaining_open_orders['orders']))

                        for order in remaining_open_orders['orders']:
                            order_ids.append(order['order_id'])
                            client_order_ids.append(order['client_order_id'])

                        # Pass the order_id as a list. Can place multiple order ids if necessary,
                        #   but not in this case
                        cancelled_order = self.cb_adv_api.cancel_order(order_ids=order_ids)
                        self.log(True, "I", "    > cancelled_order", cancelled_order)

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
                            self.log(True, "I", "    > updated_cancelled_order", updated_cancelled_order)

                        # Now, update an other Future Order records setting bot_active = 0
                        self.cb_adv_api.update_bot_active_orders()
                    else:
                        self.log(True, "I", " No Remaining Open Orders")

                #
                # If our overall position trade direction isn't neutral, then proceed
                #
                if trade_direction != "neutral":
                    self.log(True, "I", None, "-----------------------------------")
                    if trade_direction == 'long':
                        self.log(True, "I", None,
                                 " >>> Signals are strong bullish, "
                                 f"see if we should place a trade using the {fifteen_min_signals.time_unit} "
                                 f"& {thirty_min_signals.time_unit} min signals")
                    else:
                        self.log(True, "I", None,
                                 " >>> Signals are strong bearish, "
                                 f"see if we should place a trade using the {fifteen_min_signals.time_unit} "
                                 f"& {thirty_min_signals.time_unit} min signals")

                    # NOTE: Next, let's look at the 5 and 15 minute and how close to the
                    #  last signal and price of the 15 min when we should place a limit order.
                    #  How far in price are we away from the last signal?
                    #  Is 15 Minute signal side the same as the trade_direction side?

                    # five_min_trade_signal = five_min_signals.signal
                    fifteen_min_trade_signal = fifteen_min_signals.signal
                    thirty_min_signals = thirty_min_signals.signal
                    # self.log(True, "I", None, f" >>> {five_min_trade_signal.time_unit} Signal Direction",
                    #        five_min_trade_signal)
                    self.log(True, "I", None, f" >>> {fifteen_min_trade_signal.time_unit} Signal Direction",
                             fifteen_min_trade_signal)
                    self.log(True, "I", None, f" >>> {thirty_min_signals.time_unit} Signal Direction",
                             thirty_min_signals)
                    self.log(True, "I", None, " >>> Trade Signal Direction", trade_direction)

                    # Does the 15 Min and 30 Min match the overall signal trade direction of the Aurox signals?
                    if fifteen_min_trade_signal == trade_direction and thirty_min_signals == trade_direction:
                        self.log(True, "I", None,
                                 "   >>> YES, the 15 Min & 30 Min matches the overall trade direction")

                        # Check to see if next months product id is populated
                        if next_months_product_id is None:
                            # Get this months current product
                            relevant_future_product = self.cb_adv_api.get_relevant_future_from_db()
                            self.log(True, "I", "    Relevant Future Product",
                                     relevant_future_product.product_id)
                            product_id = relevant_future_product.product_id
                        else:
                            product_id = next_months_product_id

                        # Get the current Bid, Ask and Average price in the market
                        bid_price, ask_price, avg_price = (
                            self.cb_adv_api.get_current_average_price(product_id=product_id))
                        self.log(True, "I",
                                 "   bid ask avg_price", avg_price)

                        # Get the limit price for placing an order (needs to be a string and
                        #   rounded to the nearest 0 or 5
                        limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(avg_price)
                        self.log(True, "I",
                                 "   Current Limit Price", limit_price)

                        # Get the 15 min values
                        fifteen_min_future_avg_price = 0
                        for future_price in fifteen_min_signals.future_prices:
                            future_bid_price = future_price.future_bid_price
                            future_ask_price = future_price.future_ask_price
                            fifteen_min_future_avg_price = round((future_bid_price + future_ask_price) / 2)
                        self.log(True, "I",
                                 "   Fifteen Min Future Avg Price",
                                 fifteen_min_future_avg_price)

                        ############################
                        # Next, we want to check the price differences between the last 15 min signal and
                        #   the current price. We want to be sure we're with in a 1% range of opening our
                        #   first order and be as close as possible to the entire trading strategy to
                        #   maximize profits and minimize risk (loss of profits)
                        ############################

                        # Set a limit value is here (1 = 1%)
                        # percentage_diff_limit = 1
                        percentage_diff_limit = self.app.config['PERCENTAGE_DIFF_LIMIT']
                        percentage_diff = 10  # Just setting a high default number to check against

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

                        per_diff_msg = (f"   >>> Checking! Signal Direction {trade_direction} "
                                        f" Per Diff {percentage_diff}% < {percentage_diff_limit}% Limit")
                        self.log(True, "I", None, per_diff_msg)

                        # NOTE: Make sure the price difference from the 15 Min signal and current price
                        #   aren't too far off or beyond 1%, so we try to be safe and get more profit

                        if percentage_diff < percentage_diff_limit:
                            good_per_diff_msg = (f"   >>> Proceeding! current price diff of "
                                                 f"{check_signal_and_current_price_diff} "
                                                 f"which is {percentage_diff}%")
                            self.log(True, "W", None, good_per_diff_msg)

                            # size = "1"
                            size = self.app.config['CONTRACT_SIZE']
                            # leverage = "3"
                            leverage = self.app.config['LEVERAGE']
                            order_type = "limit_limit_gtc"
                            order_msg = (f"    >>> Trade side:{trade_side} Order type:{order_type} "
                                         f"Limit Price:{limit_price} Size:{size} Leverage:{leverage}")
                            self.log(True, "I", None, order_msg)

                            # When placing a new MAIN order, this doesn't guarantee the order will be
                            #   filled, just placed. We attempt to get the average bid and ask, but
                            #   we don't necessarily want to place a market order (usually a bad price)
                            if enable_main_order_creation:
                                # Create a new MAIN order
                                order_created = self.cb_adv_api.create_order(side=trade_side,
                                                                             product_id=product_id,
                                                                             size=size,
                                                                             limit_price=limit_price,
                                                                             leverage=leverage,
                                                                             order_type=order_type,
                                                                             bot_note="MAIN")
                                self.log(True, "I", "MAIN order_created", order_created)

                                if order_created:
                                    email_body = (f"New Order Placed!"
                                                  f"\nTrade side:{trade_side}"
                                                  f"\nOrder type:{order_type} "
                                                  f"\nLimit Price:{limit_price}"
                                                  f"\nSize:{size}"
                                                  f"\nLeverage:{leverage}")
                                    self.email_mgr.send_email(subject="New Order Placed!",
                                                              body=email_body)
                            else:
                                self.log(True, "W", " >>> MAIN Order Creation Disabled", enable_main_order_creation)

                        else:
                            bad_per_diff_msg = (f"   >>> Holding off, current price diff of "
                                                f"{check_signal_and_current_price_diff} "
                                                f"which is {percentage_diff}%")
                            self.log(True, "W", None, bad_per_diff_msg)
                    else:
                        self.log(True, "W", None,
                                 "   >>> NO, the 5 Min and 15 Min does not match the overall trade direction")
                        # five_min_pos_trade_dir_msg = (f"     >>> 5 Min Signal: {five_min_trade_signal} "
                        #                               f"!= Signal Trade Direction: {trade_direction}")
                        fifteen_min_pos_trade_dir_msg = (f"     >>>  {fifteen_min_signals.time_unit} "
                                                         f"Signal: {fifteen_min_trade_signal} "
                                                         f"!= Signal Trade Direction: {trade_direction}")
                        thirty_min_pos_trade_dir_msg = (f"     >>> {thirty_min_signals.time_unit} "
                                                        f"Signal: {thirty_min_signals} "
                                                        f"!= Signal Trade Direction: {trade_direction}")
                        # self.log(True, "W", None,
                        #          five_min_pos_trade_dir_msg)
                        self.log(True, "W", None,
                                 fifteen_min_pos_trade_dir_msg)
                        self.log(True, "W", None,
                                 thirty_min_pos_trade_dir_msg)
                else:
                    self.log(True, "W", None,
                             "\nSignal score is neutral, let's wait...", )
                    for group in groups:
                        self.log(True, "I", None, "   >>> ", group)
                        self.log(True, "I", None, "       > Direction", groups[group]['direction'])
                        self.log(True, "I", None, "       > Strength", groups[group]['strength'])
                        self.log(True, "I", None, "       > Score", groups[group]['score'])
                        self.log(True, "I", None, "       > Normalized Score",
                                 groups[group]['normalized_score'], "\n")
                        self.log(True, "I", None, "\n")
            else:
                self.log(True, "W", None,
                         "\nTrading isn't permitted based on the "
                         "score and direction, let's wait...", )

    def calc_avg_filled_price(self, order, dca_side):
        # self.log(True, "D", None, ":Calc Avg Filled Price:")

        dca_total_filled_price, dca_total_base_size = self.cb_adv_api.get_dca_filled_orders_from_db(
            dca_side=dca_side)
        # self.log(True, "I", "    DCA Total Filled Price", dca_total_filled_price)
        # self.log(True, "I", "    DCA Total Base Size", dca_total_base_size)

        # Get the MAIN order total filled price
        main_order_total_filled_price = order.total_filled_price
        # self.log(True, "I", "    MAIN Order Total Filled Price", main_order_total_filled_price)

        # Get the MAIN order base size(s)
        main_order_base_size = int(order.base_size)
        # self.log(True, "I", "    MAIN Order Base Size", main_order_base_size)

        # Add up all of the total order base sizes
        main_and_dca_base_size = main_order_base_size + dca_total_base_size
        # self.log(True, "I", "    TOTAL - MAIN and DCA Base Size", main_and_dca_base_size)

        # Now take to total filled prices from the MAIN order(s) and add to all or any
        #   DCA total filled prices, then divide by the total number of base sizes (contracts)
        avg_filled_price = round((main_order_total_filled_price + dca_total_filled_price) / main_and_dca_base_size)
        self.log(True, "I", "    TOTAL - ORDERS Avg Filled Price", avg_filled_price)

        return avg_filled_price

    def create_ladder_trades(self, trade_side, product_id):
        self.log(True, "D", None, "--------------------------")
        self.log(True, "D", None, ":create_ladder_trades:")

        # TODO: Need to check the database first to see if we already have
        #  active DCA orders, then add more if necessary. Say we start
        #  with 8 and need to go up to 10 due to a trade going negative further

        enable_ladder_creation = self.app.config['ENABLE_LADDER_CREATION']
        self.log(True, "I", "    enable_ladder_creation", enable_ladder_creation)

        do_dca_orders_exist = False

        quantity = self.app.config['LADDER_QUANTITY']
        self.log(True, "I", "    quantity", quantity)

        dca_note_list = ["DCA" + str(x) for x in range(1, quantity + 1)]
        # self.log(True, "I", "    dca_note_list", dca_note_list)

        dca_orders_dict = {}

        # Check to see if the orders exist before creating new ones, if so, either
        #   we skip those orders or pass an updated list / value to the DCA order to create
        for i, note in enumerate(dca_note_list):
            if i <= quantity - 1:
                dca_open_order = self.cb_adv_api.get_current_take_profit_order_from_db(
                    order_status="OPEN",
                    side=trade_side,
                    bot_note=note,
                    get_all_orders=False)
                # self.log(True, "I", "    dca_open_order", dca_open_order)

                # If orders exist, then we need to skip if we're to create more
                if dca_open_order:
                    do_dca_orders_exist = True
                    # self.log(True, "I", f"dca_open_order: {note}", i+1, dca_open_order)
                    dca_orders_dict[note] = dca_open_order

        # Check to see if ladder creation is true along with
        #   if we don't have any existing DCA orders
        if enable_ladder_creation and not do_dca_orders_exist:
            self.log(True, "I", "   >>> DCA Ladder Creation = True and no DCA orders exist!")
            bid_price, ask_price, avg_price = (
                self.cb_adv_api.get_current_average_price(product_id=product_id))
            self.log(True, "I", "   bid ask avg_price", avg_price)
            #
            #     # How many ladder orders?
            #     # ladder_order_qty = 10
            #     ladder_order_qty = self.app.config['LADDER_QUANTITY']
            #
            #     # Create the DCA ladder orders
            #     self.ladder_orders(quantity=ladder_order_qty,
            #                        side=trade_side,
            #                        product_id=product_id,
            #                        bid_price=bid_price,
            #                        ask_price=ask_price)
        else:
            self.log(True, "W", "   !!! DCA Ladder Creation = False or DCA orders exist!")
            self.log(True, "W", "   !!! Existing DCA Orders", dca_orders_dict)

    def tracking_current_position_profit_loss(self, position, order, next_month):
        self.log(True, "D", None, "---------------------------------------")
        self.log(True, "D", None, ":tracking_current_position_profit_loss:")

        # print(" position:", position)
        # print(" order:", order)

        # Only run if we have ongoing positions
        if position and order:
            # self.log(True, "I", "  Profit / Loss: Order:", order)
            # self.log(True, "I", "  Profit / Loss: Order Avg Filled Price:", order.average_filled_price)

            product_id = position.product_id
            dca_side = ''
            side = position.side
            # self.log(True, "I", "  position.product_id:", product_id)
            # self.log(True, "I", "  position.side:", side)

            # If we're LONG, then we need to place a profitable BUY order
            if side == "LONG":  # BUY / LONG
                dca_side = "BUY"
            # If we're SHORT, then we need to place a profitable SELL order
            elif side == "SHORT":  # SELL / SHORT
                dca_side = "SELL"

            # print("next_month:", next_month)
            # self.log(True, "I", "  next_month:", next_month)

            relevant_future_product = self.cb_adv_api.get_relevant_future_from_db(month_override=next_month)
            # self.log(True, "I", "  relevant_future_product:", relevant_future_product)

            product_contract_size = relevant_future_product.contract_size
            # self.log(True, "I", "  product_contract_size:", product_contract_size)

            # Find all the FILLED DCA orders to get the average price + the MAIN order
            avg_filled_price = self.calc_avg_filled_price(order=order, dca_side=dca_side)
            # self.log(True, "I", "    Average Filled Price", avg_filled_price)

            # Assign for the Trailing Take Profit Class
            self.avg_filled_price = float(avg_filled_price)

            # Get the current price from the Future Position
            current_price = round(int(position.current_price), 2)
            # self.log(True, "I", "    Current Price", current_price)

            number_of_contracts = position.number_of_contracts
            # self.log(True, "I", "    Number of Contracts", number_of_contracts)

            # Calculate total cost and current value per contract
            total_initial_cost = avg_filled_price * number_of_contracts * product_contract_size
            total_current_value = current_price * number_of_contracts * product_contract_size
            # self.log(True, "I", "  Total Initial Cost", total_initial_cost)
            # self.log(True, "I", "  Total Current Value", total_current_value)

            # Calculate profit or loss for all contracts
            # NOTE: We need to factor in what side of the market: long or short
            calc_profit_or_loss = 0
            if position.side.lower() == 'long':  # Assuming 'buy' denotes a long position
                calc_profit_or_loss = round(total_current_value - total_initial_cost, 4)
            elif position.side.lower() == 'short':  # Assuming 'sell' denotes a short position
                calc_profit_or_loss = round(total_initial_cost - total_current_value, 4)
            # self.log(True, "I", "  calc_profit_or_loss", calc_profit_or_loss)

            if total_initial_cost != 0:  # Prevent division by zero
                calc_percentage = round((calc_profit_or_loss / total_initial_cost) * 100, 4)
            else:
                calc_percentage = 0
            # self.log(True, "I", "  calc_percentage:", calc_percentage)

            self.log(True, "I", None, ">>>>>>>>>>>>>>>>>>>>>>>>>>>")
            self.log(True, "I", None, ">>> Profit / Loss <<<")
            self.log(True, "I", "Product Id", product_id)
            self.log(True, "I", "Position Side", side)
            self.log(True, "I", "Avg Entry Price $", avg_filled_price)
            self.log(True, "I", "Current Price $", current_price)
            self.log(True, "I", "# of Contracts", number_of_contracts)
            if calc_percentage >= 1:
                self.log(True, "I", "Take profit at 1% or higher %", calc_percentage)
                self.log(True, "I", "Good Profit $", calc_profit_or_loss)
            elif 2 > calc_percentage >= 0.5:
                self.log(True, "I", "Ready to take profit %", calc_percentage)
                self.log(True, "I", "Profit $", calc_profit_or_loss)
            elif 0.5 >= calc_percentage >= 0:
                self.log(True, "I", "Neutral %", calc_percentage)
                self.log(True, "I", "Not enough profit $", calc_profit_or_loss)
            elif calc_percentage < 0:
                self.log(True, "I", "Trade negative %", calc_percentage)
                self.log(True, "I", "No profit, loss of $", calc_profit_or_loss)
            self.log(True, "I", None, ">>>>>>>>>>>>>>>>>>>>>>>>>>>")
        else:
            self.log(True, "W",
                     "    No open positions | orders", position, order)

    def track_take_profit_order(self, position, order):
        self.log(True, "D", None, "-------------------------")
        self.log(True, "D", None, ":Track Take Profit Order:")

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
            number_of_contracts = position.number_of_contracts
            take_profit_price = ""
            order_type = "limit_limit_gtc"

            enable_take_profit = self.app.config['ENABLE_TAKE_PROFIT_CREATION']
            self.log(True, "I", "   Enable Take Profit Order", enable_take_profit)

            # take_profit_percentage = 0.01
            take_profit_percentage = self.app.config['TAKE_PROFIT_PERCENTAGE']
            tp_per_msg = f" Take Profit Percentage: {take_profit_percentage * 100}%"
            self.log(True, "I", None, tp_per_msg)

            # self.log(True, "I", " position.product_id:", product_id)
            # self.log(True, "I", " position.side", side)
            # self.log(True, "I", " Number Of Contracts", number_of_contracts)

            # If we're LONG, then we need to place a profitable BUY order
            if side == "LONG":  # BUY / LONG
                take_profit_side = "SELL"
                dca_side = "BUY"
            # If we're SHORT, then we need to place a profitable SELL order
            elif side == "SHORT":  # SELL / SHORT
                take_profit_side = "BUY"
                dca_side = "SELL"
            self.log(True, "I", "    take_profit_side", take_profit_side)

            # Set this to help direct the trailing take profit
            self.take_profit_side = take_profit_side

            # TODO: Need to test if the average price changes based on more positions (contracts)
            #   This may need to be adjusted back to using the Position record vs the Order record
            #   if more contracts are bought

            # Now, get the ALL Future Orders from the DB so we have more accurate data
            take_profit_order = self.cb_adv_api.get_current_take_profit_order_from_db(
                order_status="OPEN", side=take_profit_side, bot_note="TAKE_PROFIT", get_all_orders=True)
            # self.log(True, "I", "  > take_profit_order exists 1", take_profit_order)

            # BUG: Need to fix duplicate Take Profit orders, creating work around for now

            # NOTE: If we have more than one Take Profit, keep one and cancel the rest

            if len(take_profit_order) > 1:
                # Loop through all of the take profit orders, except one (we keep that)
                for tp in range(0, len(take_profit_order) - 1):
                    loop_tp_order = take_profit_order[tp]
                    loop_tp_order_id = loop_tp_order.order_id
                    loop_tp_client_order_id = loop_tp_order.client_order_id
                    # self.log(True, "I", "    >>> tp", tp, loop_tp_order)
                    # self.log(True, "I", "    tp.order_id", loop_tp_order_id)

                    # Pass the order_id as a list. Can place multiple order ids if necessary, but not in this case
                    cancelled_order = self.cb_adv_api.cancel_order(order_ids=[loop_tp_order_id])
                    self.log(True, "I", "   Cancelled Extra Order", cancelled_order)
                    field_values = {
                        "bot_active": 0,
                        "order_status": "CANCELLED"
                    }
                    # Update order so we don't the system doesn't try to use it for future orders
                    updated_cancelled_order = self.cb_adv_api.update_order_fields(
                        client_order_id=loop_tp_client_order_id,
                        field_values=field_values)
                    self.log(True, "I", "   Updated Extra Cancelled Order", updated_cancelled_order)

            # Run this again to get only one take profit order
            take_profit_order = self.cb_adv_api.get_current_take_profit_order_from_db(
                order_status="OPEN", side=take_profit_side, bot_note="TAKE_PROFIT", get_all_orders=False)
            # self.log(True, "I", "   > take_profit_order exists 1.5", take_profit_order)

            # Now see if we have a take profit order already open
            if take_profit_order is not None:
                # self.log(True, "I", "  > take_profit_order exists 2", take_profit_order)
                existing_take_profit_order = True
            else:
                existing_take_profit_order = False
                self.log(True, "W", "    No take_profit_order", take_profit_order)

            # Find all the FILLED DCA orders to get the average price + the MAIN order
            avg_filled_price = self.calc_avg_filled_price(order=order, dca_side=dca_side)

            # Assign for the Trailing Take Profit Class
            self.avg_filled_price = float(avg_filled_price)
            self.log(True, "W", "    avg_filled_price", self.avg_filled_price)

            # Calculate the take profit price (Long or Short)
            take_profit_offset_price = int(float(avg_filled_price) * take_profit_percentage)
            # self.log(True, "I", "     Take Profit Offset Price", take_profit_offset_price)

            # If we're LONG, then we need to place a profitable SELL order
            if side == "LONG":  # BUY / LONG
                take_profit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                    int(avg_filled_price) + take_profit_offset_price)
                self.log(True, "I", "    > SELL Short take_profit_price: $",
                         take_profit_price)

            # If we're SHORT, then we need to place a profitable BUY order
            elif side == "SHORT":  # SELL / SHORT
                take_profit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                    int(avg_filled_price) - take_profit_offset_price)
                self.log(True, "I", "    > BUY Long take_profit_price: $",
                         take_profit_price)

            # If we don't have an existing take profit order, create one
            if existing_take_profit_order is False:
                self.log(True, "I", None,
                         "  >>> Create new take_profit_order")

                if enable_take_profit:
                    # Take Profit Order
                    order_created = self.cb_adv_api.create_order(side=take_profit_side,
                                                                 product_id=product_id,
                                                                 size=number_of_contracts,
                                                                 limit_price=take_profit_price,
                                                                 leverage='',
                                                                 order_type=order_type,
                                                                 bot_note="TAKE_PROFIT")
                    self.log(True, "I", None,
                             "   >>> TAKE_PROFIT order_created!")
                    self.log(True, "I", "    >>> Order:", order_created)
                else:
                    self.log(True, "W", "    Take Profit Order Disabled", enable_take_profit)

                # TODO: Need to add way to check for existing ladder orders
                #   before allowing them to be created

                # Also, create the DCA ladder orders
                self.create_ladder_trades(trade_side=side, product_id=product_id)

            else:  # Otherwise, let's edit and update the order based on the market and position(s)
                self.log(True, "I", None,
                         "  >>> Check Existing Take Profit Order...")
                # pp(take_profit_order)

                base_size = take_profit_order.base_size
                limit_price = take_profit_order.limit_price
                tp_order_id = take_profit_order.order_id
                tp_client_order_id = take_profit_order.client_order_id
                # self.log(True, "I", "tp_order_id", tp_order_id)
                # self.log(True, "I", "tp_client_order_id", tp_client_order_id)

                # For limit GTC orders only
                size = take_profit_order.base_size
                # self.log(True, "I", "take_profit_order size", size)

                # See if we need to update the size based on the existing number of
                # contracts in the position
                if int(number_of_contracts) > int(size):
                    new_size = number_of_contracts
                    self.log(True, "W",
                             "    take_profit_order new_size", new_size)
                else:
                    new_size = size
                # print(" take_profit_order new_size:", new_size)

                # WARNING: FOR TESTING, DO NOT LEAVE ON
                if self.app.config['TAKE_PROFIT_MANUAL_OVERRIDE_PRICE']:
                    take_profit_price = self.app.config['TAKE_PROFIT_MANUAL_OVERRIDE_PRICE']
                # new_size = str(2)

                # REVIEW: Since the edit_order API call isn't working (and I've reached out to support),
                #  I'll just cancel the order and place a new one. This shouldn't run that often for
                #  the DCA take profit orders, however, I do want to solve this for trailing take profit

                # NOTE: In order to update the order, we need to get it first, then check the values against
                #   if we have an updates contact "size" or "price" based on the DCA orders, if not
                #   then we can skip this

                check_price_size_msg = f" {int(limit_price)} != {int(take_profit_price)} or {base_size} != {new_size}"
                self.log(True, "I",
                         "    Check Price Size Msg", check_price_size_msg)

                # Check to see if either price or size don't match
                if (int(limit_price) != int(take_profit_price)) is True or (int(base_size) != int(new_size)) is True:
                    self.log(True, "I", None,
                             "   >>> Either the prices are off or the contract sizes are off")
                    self.log(True, "I", None,
                             "   >>> Cancel the existing take profit or and place a new one!")

                    # NOTE: Cancel the existing take profit order, update it's db record,
                    #  then place a new take profit with the the updated price and size

                    if len(tp_order_id) > 0:
                        # Pass the order_id as a list. Can place multiple order ids if necessary, but not in this case
                        cancelled_order = self.cb_adv_api.cancel_order(order_ids=[tp_order_id])
                        self.log(True, "I",
                                 "    cancelled_order", cancelled_order)

                        field_values = {
                            "bot_active": 0,
                            "order_status": "CANCELLED"
                        }
                        # Update order so we don't the system doesn't try to use it for future orders
                        updated_cancelled_order = self.cb_adv_api.update_order_fields(
                            client_order_id=tp_client_order_id,
                            field_values=field_values)
                        self.log(True, "I",
                                 "    updated_cancelled_order", updated_cancelled_order)

                    self.log(True, "I", None,
                             "   >>> Creating new order with updated PRICE or SIZE settings!")

                    if enable_take_profit:
                        # Take Profit Order
                        take_profit_order_created = self.cb_adv_api.create_order(side=take_profit_side,
                                                                                 product_id=product_id,
                                                                                 size=new_size,
                                                                                 limit_price=take_profit_price,
                                                                                 leverage='',
                                                                                 order_type=order_type,
                                                                                 bot_note="TAKE_PROFIT")
                        self.log(True, "I",
                                 "   >>> take_profit_order_created", take_profit_order_created)
                else:
                    self.log(True, "I", None,
                             "   ...No changes with take profit order in PRICE or SIZE...")
        else:
            self.log(True, "W",
                     "    No open positions | orders", position, order)


if __name__ == "__main__":
    print(__name__)
