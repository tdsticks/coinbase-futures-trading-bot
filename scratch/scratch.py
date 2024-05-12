#######################
#######################
#######################
# app.py
#######################
#######################
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
# List Orders
# future_product = cbapi.get_relevant_future_from_db()
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
# relevant_future_product = cbapi.get_relevant_future_from_db()
# print("relevant_future_product:", relevant_future_product)
#
# future_bid_ask_price = cbapi.get_current_bid_ask_prices(relevant_future_product.product_id)
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


# @scheduler.task('interval', id='do_job_5', seconds=10, misfire_grace_time=900)
# def check_for_contract_expires_job():
#     # print('\n:check_for_contract_expires_job:')
#     log.log(True, "D", None, msg1=":check_for_contract_expires_job:")
#
#     tm.check_for_contract_expires()

# @scheduler.task('interval', id='do_job_5', seconds=30, misfire_grace_time=900)
# def list_future_positions_job():
#     print('\n:list_future_positions_job:')
#     # Get Current Positions
#     future_positions = cbapi.list_future_positions()
#     # pp(future_positions)
#     cbapi.store_future_positions(future_positions)

# @scheduler.task('interval', id='do_job_6', seconds=150000, misfire_grace_time=900)
# def test_ladder_orders_job():
#     print('\n:test_ladder_orders_job:')
#
#     # Get this months current product
#     relevant_future_product = cbapi.get_relevant_future_from_db()
#     print(" relevant_future_product:", relevant_future_product.product_id)
#
#     # Get Current Bid Ask Prices
#     cur_future_bid_ask_price = cbapi.get_current_bid_ask_prices(
#         relevant_future_product.product_id)
#     cur_future_bid_price = cur_future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
#     cur_future_ask_price = cur_future_bid_ask_price['pricebooks'][0]['asks'][0]['price']
#     print(f" Prd: {relevant_future_product.product_id} - "
#           f"Current Futures: bid: ${cur_future_bid_price} "
#           f"ask: ${cur_future_ask_price}")
#
#     # side = "BUY"
#     side = "SELL"
#
#     tm.ladder_orders(side=side,
#                      product_id=relevant_future_product.product_id,
#                      bid_price=cur_future_bid_price,
#                      ask_price=cur_future_ask_price)

# @scheduler.task('interval', id='do_job_6', seconds=150000, misfire_grace_time=900)
# def test_create_order_job():
#     print('\n:test_create_order_job:')
#
#     # Get this months current product
#     relevant_future_product = cbapi.get_relevant_future_from_db()
#     print(" relevant_future_product:", relevant_future_product.product_id)
#
#     # Get Current Bid Ask Prices
#     cur_future_bid_ask_price = cbapi.get_current_bid_ask_prices(
#         relevant_future_product.product_id)
#     cur_future_bid_price = cur_future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
#     cur_future_ask_price = cur_future_bid_ask_price['pricebooks'][0]['asks'][0]['price']
#     print(f" Prd: {relevant_future_product.product_id} - "
#           f"Current Futures: bid: ${cur_future_bid_price} "
#           f"ask: ${cur_future_ask_price}")
#
#
#     two_percent_offset = int(float(cur_future_bid_price) * 0.02)
#     print(" two_percent_offset:", two_percent_offset)
#
#     # side = "BUY"
#     side = "SELL"
#
#     if side == "BUY":
#         # BUY / LONG
#         limit_price = cbapi.adjust_price_to_nearest_increment(
#             int(cur_future_bid_price) - two_percent_offset)
#         print(" Buy Long limit_price: $", limit_price)

#     elif side == "SELL":
#         # SELL / SHORT
#         limit_price = cbapi.adjust_price_to_nearest_increment(
#             int(cur_future_ask_price) + two_percent_offset)
#         print(" Sell Short limit_price: $", limit_price)
#
#     size = "1"
#     leverage = "3"
#
#     order_type = "market_market_ioc"
#     # order_type = "limit_limit_gtc"
#
#     # cbapi.create_order(side=side,
#     #                    product_id=relevant_future_product.product_id,
#     #                    size=size,
#     #                    limit_price=limit_price,
#     #                    leverage=leverage,
#     #                    order_type=order_type)


# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True

# @scheduler.task('interval', id='do_job_10', seconds=30, misfire_grace_time=900)
# def testing():
#     print('\n:testing:')

# @scheduler.task('interval', id='calc_signals', seconds=30, misfire_grace_time=900)
# def run_signal_calc():
#     log.log(True, "I", None, msg1="------------------------------")
#     log.log(True, "I", None, msg1=":run_signal_calc:")

# weekly_signals = tm.get_latest_weekly_signal()
# five_day_signals = tm.get_latest_five_day_signal()
# three_day_signals = tm.get_latest_three_day_signal()
# two_day_signals = tm.get_latest_two_day_signal()
# daily_signals = tm.get_latest_daily_signal()
# twelve_hour_signals = tm.get_latest_12_hour_signal()
# eight_hour_signals = tm.get_latest_8_hour_signal()
# six_hour_signals = tm.get_latest_6_hour_signal()
# four_hour_signals = tm.get_latest_4_hour_signal()
# three_hour_signals = tm.get_latest_3_hour_signal()
# two_hour_signals = tm.get_latest_2_hour_signal()
# one_hour_signals = tm.get_latest_1_hour_signal()
# thirty_min_signals = tm.get_latest_30_minute_signal()
# twenty_min_signals = tm.get_latest_20_minute_signal()
# fifteen_min_signals = tm.get_latest_15_minute_signal()
# ten_min_signals = tm.get_latest_10_minute_signal()
# five_min_signals = tm.get_latest_5_minute_signal()

# Group 1: 1W, 5D, 3D, 2D, 1D, 12H,
# Group 2: 8H, 6H, 4H, 3H, 2H, 1H
# Group 2: 30m, 20m, 15m 10m, 5m

# signal_dict = {
#     "group1": {
#         "weekly": weekly_signals,
#         "five_day": five_day_signals,
#         "three_day": three_day_signals,
#         "two_day": two_day_signals,
#         "daily": daily_signals,
#         "twelve_hr": twelve_hour_signals,
#     },
#     "group2": {
#         "eight_hr": eight_hour_signals,
#         "six_hr": six_hour_signals,
#         "four_hr": four_hour_signals,
#         "three_hr": three_hour_signals,
#         "two_hr": two_hour_signals,
#         "one_hour": one_hour_signals,
#     },
#     "group3": {
#         "thirty_min": thirty_min_signals,
#         "twenty_min": twenty_min_signals,
#         "fifteen_min": fifteen_min_signals,
#         "ten_min": ten_min_signals,
#         "five_min": five_min_signals
#     }
# }

# total_grp_dir_val, total_strength_trade = tm.calc_all_signals_score_for_dir_new(signal_dict)
# log.log(True, "I", "   >>> Total Direction Val & Strength",
#                    total_grp_dir_val, total_strength_trade)

# signal_processor = SignalProcessor(app, tm)
# signal_processor.run()




















#######################
#######################
#######################
# trade_manager.py
#######################
#######################
#######################

"""
    def compare_last_daily_to_todays_date(self):
        self.log.log(True, "I", None, ":compare_last_daily_to_todays_date:")

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
                self.log.log(True, "I", None, "Within 24 hours, proceed to place trade.")
                return True
            else:
                # print("More than 24 hours since the last signal, wait for the next one.")
                self.log.log(True, "W", None,
                             "More than 24 hours since the last signal, wait for the next one.")
        else:
            # print("No daily signal found.")
            self.log.log(True, "W", None,
                         "No daily signal found.")
"""

"""
def write_db_signal(self, data):
    self.log.log(True, "I", None, ":write_db_signal:")

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
            self.log.log(True, "I", "timestamp", timestamp)

            signal_spot_price = data['price'].replace(',', '')

            # Define the time window in which signals are considered potential duplicates
            time_window = timedelta(minutes=10)
            self.log.log(True, "I", "time_window", time_window)

            calc_time_window = AuroxSignal.timestamp.between(timestamp - time_window, timestamp + time_window)
            self.log.log(True, "I", "calc_time_window", calc_time_window)

            # Check for existing signal to prevent duplicates
            existing_signal = AuroxSignal.query.filter_by(
                # timestamp=timestamp,
                timestamp=calc_time_window,
                price=signal_spot_price,
                signal=data['signal'],
                trading_pair=data['trading_pair'],
                time_unit=data['timeUnit']
            ).first()

            if existing_signal is None:
                new_signal = AuroxSignal(
                    timestamp=timestamp,
                    price=signal_spot_price,
                    signal=data['signal'],
                    trading_pair=data['trading_pair'],
                    time_unit=data['timeUnit']
                )
                db.session.add(new_signal)
                db.session.flush()  # Flush to assign an ID to new_signal without committing transaction
                self.log.log(True, "I", "New signal stored", new_signal)
            else:
                self.log.log(True, "I", "Duplicate signal detected; not stored", existing_signal)
                return  # Skip further processing if it's a duplicate

            next_months_product_id, next_month = self.check_for_contract_expires()

            # Now, get the bid and ask prices for the current futures product
            relevant_future_product = self.cb_adv_api.get_relevant_future_from_db(month_override=next_month)
            self.log.log(True, "I", " relevant_future_product product_id",
                                    relevant_future_product.product_id)

            # Get the current bid and ask prices for the futures product related to this signal
            future_bid_ask_price = self.cb_adv_api.get_current_bid_ask_prices(relevant_future_product.product_id)
            future_bid_price = future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
            future_ask_price = future_bid_ask_price['pricebooks'][0]['asks'][0]['price']

            self.log.log(True, "I", "next_months_product_id", next_months_product_id)
            self.log.log(True, "I", "next_month", next_month)

            # Find the related futures product based on the current futures product
            # Assuming the current futures product maps directly to product_id in your CoinbaseFuture model
            if relevant_future_product:
                # Create a FuturePriceAtSignal record linking the new signal and the futures product
                new_future_price = FuturePriceAtSignal(
                    signal_spot_price=signal_spot_price,
                    future_bid_price=future_bid_price,
                    future_ask_price=future_ask_price,
                    signal_id=new_signal.id if new_signal else existing_signal.id,
                    future_id=relevant_future_product.id
                )
                db.session.add(new_future_price)
                self.log.log(True, "I", "Associated bid/ask prices stored for the signal")

            db.session.commit()

        except db_errors as e:
            self.log.log(True, "E", "Error fetching latest daily signal", str(e))
            db.session.rollback()
"""

# def get_future_position(self, product_id):
#     print(":get_future_position:")
#
#     get_futures_positions = self.client.get_futures_position(product_id=product_id)
#     pp(get_futures_positions)
#
#     return get_futures_positions

# def get_current_future_product_from_db(self, product_id):
#     # print(":get_current_future_product_from_db:")
#     self.log.log(True, "I", None, ":get_current_future_product_from_db:")
#
#     with self.flask_app.app_context():
#         # Check if the future product already exists in the database
#         future_product = CoinbaseFuture.query.filter_by(product_id=product_id).first()
#         # print("\nfound future_product:", future_product)
#
#     return future_product

# def check_for_contract_expires(self):
#     self.log.log(True, "D", None,
#                             ":check_for_contract_expires:")
#
#     # Get the futures contract from Coinbase API
#     list_future_products = self.cb_adv_api.list_products("FUTURE")
#
#     current_month = self.cb_adv_api.get_current_short_month_uppercase()
#     self.log.log(True, "I",
#                             "current_month",
#                             current_month)
#
#     self.cb_adv_api.store_btc_futures_products(list_future_products)
#
#     current_future_product = self.cb_adv_api.get_relevant_future_from_db()
#     self.log.log(True, "I",
#                             "current_future_product",
#                             current_future_product.product_id)
#
#     if current_future_product:
#         # Make sure contract_expiry is timezone-aware
#         contract_expiry = current_future_product.contract_expiry.replace(tzinfo=pytz.utc)
#         # print("Contract expiry:", contract_expiry)
#
#         # Current time in UTC
#         now = datetime.now(pytz.utc)
#         # print("Now:", now)
#
#         # Calculate time difference
#         time_diff = contract_expiry - now
#         # print("total_seconds:", time_diff.total_seconds())
#
#         days = time_diff.days
#         hours, remainder = divmod(time_diff.seconds, 3600)
#         minutes, seconds = divmod(remainder, 60)
#
#         # Check if the contract has expired
#         if time_diff.total_seconds() <= 0:
#             self.log.log(True, "W", None, "-----------------------------------")
#             self.log.log(True, "W", None, "Contract has expired, close trades.")
#             self.log.log(True, "W", None, ">>> Close out any positions!!!")
#             self.log.log(True, "W", None, "-----------------------------------")
#         elif days <= 2:
#             self.log.log(True, "W", None, "-----------------------------------")
#             self.log.log(True, "W", None, "Contract is close to expiring!")
#             self.log.log(True, "W", None, "Switch to next months contract")
#             self.log.log(True, "W", None, ">>> Close out any positions!!!")
#             self.log.log(True, "W", None, "-----------------------------------")
#             contract_msg = ("\n-------------------------"
#                             f"\nContract for:"
#                             f"\n  {current_future_product.product_id}"
#                             f"\n  Month: {current_month}"
#                             f"\n  expires in {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds."
#                             "\n-------------------------")
#             self.log.log(True, "W", None, contract_msg)
#         else:
#             contract_msg = ("\n-------------------------"
#                             f"\nContract for:"
#                             f"\n  {current_future_product.product_id}"
#                             f"\n  Month: {current_month}"
#                             f"\n  expires in {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds."
#                             "\n-------------------------")
#             self.log.log(True, "I", None, contract_msg)
#     else:
#         print(" No future product found for this month.")

"""
def check_trading_conditions(self):
    self.log.log(True, "D", None, ":check_trading_conditions:")

    # Update any cancelled orders in the database (in case we close things manually, etc.)
    self.cb_adv_api.update_cancelled_orders()

    #######################
    # Do we have an existing trades?
    #######################

    next_months_product_id, next_month = self.check_for_contract_expires()
    self.log.log(True, "I", "next_months_product_id", next_months_product_id)
    self.log.log(True, "I", "next_month", next_month)

    # Get Current Positions from API, we just need to acknowledge this position exists
    #  and get the position side
    # future_positions = self.cb_adv_api.list_future_positions()
    # pp(future_positions)

    future_positions = {'positions': None}

    if future_positions['positions']:
        # print(" >>> We have an active position(s)")
        self.log.log(True, "I", None, " >>> We have an active position(s)")

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
        self.log.log(True, "I", "cur_position_order", cur_position_order)

        # Clear and store the active future position
        self.cb_adv_api.store_future_positions(future_positions)

        # Get the position from the database
        # note: We should only get one if we're only trading one future (BTC)
        with (self.flask_app.app_context()):  # Push an application context
            try:
                # note: position doesn't have the all most accurate data we need, so
                #  we uses the order to help supplement what we need
                positions = FuturePosition.query.all()
                for position in positions:
                    self.tracking_current_position_profit_loss(position, cur_position_order, next_month)
                    self.track_take_profit_order(position, cur_position_order)

            except Exception as e:
                self.log.log(True, "E", "Unexpected error:", msg1=e)
    else:
        #######################
        # If not, then is it a good time to place a market order?
        # Let's pull the last weekly and daily signals, check and wait...
        #######################

        weekly_signals = self.get_latest_weekly_signal()
        daily_signals = self.get_latest_daily_signal()
        twelve_hour_signals = self.get_latest_12_hour_signal()
        eight_hour_signals = self.get_latest_8_hour_signal()
        four_hour_signals = self.get_latest_4_hour_signal()
        one_hour_signals = self.get_latest_1_hour_signal()
        fifteen_minute_signals = self.get_latest_15_minute_signal()

        weekly_signals_dt = None
        daily_signals_dt = None
        twelve_hour_signals_dt = None
        eight_hour_signals_dt = None
        four_hour_signals_dt = None
        one_hour_signals_dt = None
        fifteen_minute_signals_dt = None

        weekly_weight = 168
        daily_weight = 24
        twelve_hr_weight = 12
        eight_hr_weight = 8
        four_hr_weight = 4
        one_hour_weight = 1
        fifteen_min_weight = 0.25
        calc_score = 0

        if weekly_signals:
            print(f" Weekly: Signal:{weekly_signals.signal} | Date:{weekly_signals.timestamp} "
                  f"| Price:${weekly_signals.price}")
            weekly_signals_dt = weekly_signals.timestamp
            print(f"weekly_signals_dt: {weekly_signals_dt}")

            calc_score += self.calculate_signal_score(weekly_signals.signal, weekly_weight)

        if daily_signals:
            print(f" Daily: Signal:{daily_signals.signal} | Date:{daily_signals.timestamp} "
                  f"| Price:${daily_signals.price}")
            daily_signals_dt = daily_signals.timestamp
            print(f"daily_signals_dt: {daily_signals_dt}")

            calc_score += self.calculate_signal_score(daily_signals.signal, daily_weight)

        if twelve_hour_signals:
            print(f" 12 Hour: Signal:{twelve_hour_signals.signal} | Date:{twelve_hour_signals.timestamp} "
                  f"| Price:${twelve_hour_signals.price}")
            twelve_hour_signals_dt = twelve_hour_signals.timestamp
            print(f"twelve_hour_signals_dt: {twelve_hour_signals_dt}")

            calc_score += self.calculate_signal_score(twelve_hour_signals.signal, twelve_hr_weight)

        if eight_hour_signals:
            print(f" 8 Hour: Signal:{eight_hour_signals.signal} | Date:{eight_hour_signals.timestamp} "
                  f"| Price:${eight_hour_signals.price}")
            eight_hour_signals_dt = eight_hour_signals.timestamp
            print(f"eight_hour_signals_dt: {eight_hour_signals_dt}")

            calc_score += self.calculate_signal_score(eight_hour_signals.signal, eight_hr_weight)

        if four_hour_signals:
            print(f" 4 Hour: Signal:{four_hour_signals.signal} | Date:{four_hour_signals.timestamp} "
                  f"| Price:${four_hour_signals.price}")
            four_hour_signals_dt = four_hour_signals.timestamp
            print(f"four_hour_signals_dt: {four_hour_signals_dt}")

            calc_score += self.calculate_signal_score(four_hour_signals.signal, four_hr_weight)

        if one_hour_signals:
            print(f" 1 Hour: Signal:{one_hour_signals.signal} | Date:{one_hour_signals.timestamp} "
                  f"| Price:${one_hour_signals.price}")
            one_hour_signals_dt = one_hour_signals.timestamp
            print(f"one_hour_signals_dt: {one_hour_signals_dt}")

            calc_score += self.calculate_signal_score(one_hour_signals.signal, one_hour_weight)

        if fifteen_minute_signals:
            print(f" 15 Minute: Signal:{fifteen_minute_signals.signal} | Date:{fifteen_minute_signals.timestamp} "
                  f"| Price:${fifteen_minute_signals.price}")
            fifteen_minute_signals_dt = fifteen_minute_signals.timestamp
            print(f"fifteen_minute_signals_dt: {fifteen_minute_signals_dt}")

            calc_score += self.calculate_signal_score(fifteen_minute_signals.signal, fifteen_min_weight)

        print(f"Total calc_score: {calc_score}")

        position_trade_direction = self.decide_trade_direction(calc_score)
        print(f"position_trade_direction: {position_trade_direction}")

        # Show the Weekly and Daily Signal information
        # weekly_ts_formatted = weekly_signals_dt.strftime("%B %d, %Y, %I:%M %p")
        daily_ts_formatted = daily_signals_dt.strftime("%B %d, %Y, %I:%M %p")
        # twelve_ts_formatted = twelve_hour_signals_dt.strftime("%B %d, %Y, %I:%M %p")
        # eight_ts_formatted = eight_hour_signals_dt.strftime("%B %d, %Y, %I:%M %p")
        # four_hr_ts_formatted = four_hour_signals_dt.strftime("%B %d, %Y, %I:%M %p")
        # hourlu_ts_formatted = one_hour_signals_dt.strftime("%B %d, %Y, %I:%M %p")
        # fifteen_minute_ts_formatted = fifteen_minute_signals_dt.strftime("%B %d, %Y, %I:%M %p")

        # review Do we also look at the 4 Hour, 1 Hour, 15 min for a better min to buy? long or short

        # todo Create a scoring systems based on the signals and timeframes. If the score is
        #   high enough based on the market direction (long or short), then we may be safer
        #   to trade in a particular direction

        # FOR TESTING (NOT FOR PRODUCTION)
        # weekly_signals.signal = daily_signals.signal = "long"
        # weekly_signals.signal = daily_signals.signal = "short"

        # if weekly_signals.signal == daily_signals.signal:
        if position_trade_direction != "neutral":
            # print("\n>>> Weekly and Daily signals align, see if we should place a trade")
            self.log.log(True, "I", None,
                                    " >>> Weekly and Daily signals align, see if we should place a trade")

            now = datetime.now(pytz.utc)  # Current time in UTC
            # time_diff = now - daily_signals_dt  # Calculate time difference
            # time_diff = now - daily_ts_formatted  # Calculate time difference
            # days = time_diff.days  # Get the number of days directly

            # FOR TESTING (NOT FOR PRODUCTION)
            # days = 1

            # Calculate hours, minutes, seconds from the total seconds
            # total_seconds = time_diff.total_seconds()
            # hours = int(total_seconds // 3600)  # Total seconds divided by number of seconds in an hour
            # minutes = int((total_seconds % 3600) // 60)  # Remainder from hrs divided by number of secs in a min
            # seconds = int(total_seconds % 60)  # Remainder from minutes

            # Are we within 5 days from the Weekly and Daily Aurox signal?
            #   If so, then let's proceed with out trading
            # if days <= 5:
            # print(">>> We should place a trade!")
            # self.log.log(True, "I", None, ">>> We should place a trade!")

            weekly_signal_spot_price = 0
            weekly_future_bid_price = 0
            weekly_future_ask_price = 0
            weekly_future_avg_price = 0
            daily_signal_spot_price = 0
            daily_future_bid_price = 0
            daily_future_ask_price = 0
            daily_future_avg_price = 0

            for future_price in weekly_signals.future_prices:
                weekly_signal_spot_price = future_price.signal_spot_price
                weekly_future_bid_price = future_price.future_bid_price
                weekly_future_ask_price = future_price.future_ask_price
                weekly_future_avg_price = (weekly_future_bid_price + weekly_future_ask_price) / 2

            for future_price in daily_signals.future_prices:
                daily_signal_spot_price = future_price.signal_spot_price
                daily_future_bid_price = future_price.future_bid_price
                daily_future_ask_price = future_price.future_ask_price
                daily_future_avg_price = (daily_future_bid_price + daily_future_ask_price) / 2

            # Show the Weekly and Daily Signal information
            # weekly_msg = (f"Signal: {weekly_signals.signal} | "
            #               f"Date: {weekly_ts_formatted} | "
            #               f"Spot Price: ${weekly_signal_spot_price} | "
            #               f"Future Price: ${weekly_future_avg_price}")
            # self.log.log(True, "I", "WEEKLY", weekly_msg)
            #
            # daily_msg = (f"Signal: {daily_signals.signal} | "
            #              f"Date: {daily_ts_formatted} | "
            #              f"Spot Price: ${daily_signal_spot_price} | "
            #              f"Future Price: ${daily_future_avg_price}")
            # self.log.log(True, "I", "DAILY", daily_msg)

            #######################
            # Now lets check the Futures market (we should store in logging)
            #######################

            # Check to see if next months product id is populated
            if next_months_product_id is None:

                # Get this months current product
                relevant_future_product = self.cb_adv_api.get_relevant_future_from_db()
                self.log.log(True, "I", "relevant_future_product",
                                        relevant_future_product.product_id)

                product_id = relevant_future_product.product_id
            else:
                product_id = next_months_product_id

            bid_price, ask_price, avg_price = self.cb_adv_api.get_current_average_price(product_id=product_id)
            self.log.log(True, "I",
                                    "avg_price", avg_price)

            limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(avg_price)
            self.log.log(True, "I",
                                    "limit_price", limit_price)

            #  LONG = BUY
            #   SHORT = SELL
            trade_side = ""

            if position_trade_direction == "long":
                trade_side = "BUY"
            elif position_trade_direction == "short":
                trade_side = "SELL"

            # if daily_signals.signal == "long":
            #     trade_side = "BUY"
            # elif daily_signals.signal == "short":
            #     trade_side = "SELL"

            size = "1"
            leverage = "3"
            order_type = "limit_limit_gtc"
            order_msg = (f"    >>> Trade side:{trade_side} Order type:{order_type} "
                         f"Limit Price:{limit_price} Size:{size} Leverage:{leverage}")
            self.log.log(True, "I", None, order_msg)

            # If we place a limit order and it doesn't go through, we need to control
            #   this from placing more orders. Only one should be allowed until it goes through.
            #   We should cancel the order, then place again. We set a bot_note to track this

            current_open_position = self.cb_adv_api.get_current_take_profit_order_from_db(order_status="OPEN",
                                                                                          side=trade_side,
                                                                                          bot_note="MAIN")

            # If this loops back through and has not been bought or sold (a position),
            #   then cancel and try again at a better average bid/ask price.

            if current_open_position is not None:
                current_open_position_order_id = [current_open_position.order_id]
                print("MAIN current_open_position_order_id:", current_open_position_order_id)

                self.cb_adv_api.cancel_order(order_ids=current_open_position_order_id)

            # Get then close all open orders

            remaining_open_orders = self.cb_adv_api.list_orders(product_id=product_id,
                                                                order_status="OPEN")
            # print("remaining_open_orders:", remaining_open_orders)

            if 'orders' in remaining_open_orders:
                print("remaining_open_orders count:", len(remaining_open_orders['orders']))

                # order_ids = []
                # for order in remaining_open_orders['orders']:
                #     order_ids.append(order['order_id'])
                # print("remaining_open_orders order_ids:", order_ids)
                #
                # # Pass the order_id as a list. Can place multiple order ids if necessary, but not in this case
                # cancelled_order = self.cb_adv_api.cancel_order(order_ids=order_ids)
                # self.log.log(True, "I", "cancelled_order", cancelled_order)
                #
                # field_values = {
                #     "bot_active": 0,
                #     "order_status": "CANCELLED"
                # }
                #
                # for order in remaining_open_orders['orders']:
                #     # Update order so we don't the system doesn't try to use it for future orders
                #     updated_cancelled_order = self.cb_adv_api.update_order_fields(
                #         client_order_id=order.client_order_id,
                #         field_values=field_values)
                #     self.log.log(True, "I", "updated_cancelled_order", updated_cancelled_order)

            # Create a new MAIN order
            # order_created = self.cb_adv_api.create_order(side=trade_side,
            #                                              product_id=product_id,
            #                                              size=size,
            #                                              limit_price=limit_price,
            #                                              leverage=leverage,
            #                                              order_type=order_type,
            #                                              bot_note="MAIN")
            # print("MAIN order_created:", order_created)
            #
            # # Create the DCA ladder orders
            # self.ladder_orders(side=trade_side,
            #                    product_id=product_id,
            #                    bid_price=bid_price,
            #                    ask_price=ask_price)
            # else:
            #     self.log.log(True, "W", None,
            #                             "Too far of gab between the last daily and today")
            #     time_diff_msg = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
            #     self.log.log(True, "W", "Time difference", time_diff_msg)
        else:
            # self.log.log(True, "W", None,
            #                         "Weekly Signal and Daily Signal DO NOT ALIGN, let's wait...")
            self.log.log(True, "W", None,
                                    "Signal score is neutral, let's wait...")

            # weekly_msg = f"Weekly Signal: {weekly_signals.signal} | Date: {weekly_ts_formatted}"
            # daily_msg = f"Daily Signal: {daily_signals.signal} | Date: {daily_ts_formatted}"
            # self.log.log(True, "W", None, weekly_msg)
            # self.log.log(True, "W", None, daily_msg)
"""

"""
    @staticmethod
    def query_to_dataframe(query):
        # Convert a SQLAlchemy query to a DataFrame.
        result = query.all()
        return pd.read_sql(query.statement, query.session.bind)

    def calc_all_signals_score_for_direction_2(self, week_sig, day_sig, twelve_sig, eight_sig, four_sig, hour_sig, fifteen_sig):
        self.log.log(True, "D", None, "----------------------------")
        self.log.log(True, "D", None, ":calc_all_signals_score_for_direction_2:")

        # todo: Add the session queries to the webhook so we update out data.

        # Querying AuroxSignal data
        # query_aurox = session.query(AuroxSignal)
        # aurox_df = self.query_to_dataframe(query_aurox)

        # Convert price from string to float before any calculations
        # aurox_df['price'] = pd.to_numeric(aurox_df['price'], errors='coerce')

        # Querying FuturePriceAtSignal data
        # query_future_price = session.query(FuturePriceAtSignal)
        # future_df = self.query_to_dataframe(query_future_price)

        # Close session after the operations
        # session.close()

        # Merge on signal_id and id
        # combined_df = pd.merge(aurox_df, future_df, left_on='id', right_on='signal_id')

        # Calculate average future price and deviation
        # combined_df['average_future_price'] = (combined_df['future_bid_price'] + combined_df['future_ask_price']) / 2
        # combined_df['price_deviation'] = (abs(combined_df['price'] - combined_df['average_future_price']) /
        #                                   combined_df['price'])
        # Continue with your analysis
        # print(combined_df)

        # Base weights by time units (hours)
        # base_weights = {
        #     '1 Week': int(config['trade.conditions']['weekly_weight']),
        #     '1 Day': int(config['trade.conditions']['daily_weight']),
        #     '12 Hours': int(config['trade.conditions']['twelve_hr_weight']),
        #     '8 Hours': int(config['trade.conditions']['eight_hr_weight']),
        #     '4 Hours': int(config['trade.conditions']['four_hr_weight']),
        #     '1 Hour': int(config['trade.conditions']['one_hour_weight']),
        #     '15 Minutes': float(config['trade.conditions']['fifteen_min_weight'])
        # }

        # max_score = (168 + 24 + 12 + 8 + 4 + 1 + 0.25) * 1  # All 'long'
        # min_score = (168 + 24 + 12 + 8 + 4 + 1 + 0.25) * -1  # All 'short'
        # print("LONG max_score:", max_score)
        # print("SHORT min_score:", min_score)

        # Calculate weighted scores
        # combined_df['weight'] = combined_df['time_unit'].map(base_weights)
        # combined_df['adjusted_weight'] = combined_df['weight'] * (1 + combined_df['price_deviation'])
        # combined_df['direction_score'] = combined_df['signal'].apply(lambda x: 1 if x == 'long' else -1)
        # combined_df['weighted_score'] = combined_df['adjusted_weight'] * combined_df['direction_score']

        # Aggregate to find overall direction
        # overall_score = combined_df['weighted_score'].sum()
        # print("Overall Score:", overall_score)

        # market_direction = 'long' if overall_score > 0 else 'short'
        # market_direction = ''

        # Sample data setup
        # data = {
        #     "timestamp": ["2024-04-01 02:55:21", "2024-05-02 00:04:34", "2024-05-01 00:02:14", "2024-05-01 00:02:19",
        #                   "2024-05-02 06:02:35", "2024-05-02 15:02:01", "2024-05-01 20:34:27"],
        #     "price": [69662.72, 58307.6, 62037.6, 61245, 57463.2, 58583, 61094],
        #     "signal": ["short", "long", "short", "short", "long", "long", "short"],
        #     "time_unit": ["1 Week", "4 Hours", "1 Day", "12 Hours", "1 Hour", "15 Minutes", "8 Hours"],
        #     "future_bid_price": [66295, 61760, 61145, 61120, 58305, 59590, 63247],
        #     "future_ask_price": [66295, 61785, 61170, 61150, 58330, 59615, 63247]
        # }

        # df = pd.DataFrame(data)

        # Define weights
        # weights = {
        #     "1 Week": 0.25, "1 Day": 0.20, "12 Hours": 0.15, "8 Hours": 0.10,
        #     "4 Hours": 0.10, "1 Hour": 0.10, "15 Minutes": 0.10
        # }

        # Calculate average future price and deviations
        # df['average_future_price'] = (df['future_bid_price'] + df['future_ask_price']) / 2
        # df['deviation'] = abs(df['price'] - df['average_future_price']) / df['price']
        # df['weight'] = df['time_unit'].map(weights) * (1 + df['deviation'])
        # df['direction_score'] = df['signal'].map({'long': 1, 'short': -1})
        # df['weighted_score'] = df['weight'] * df['direction_score']
        # print(" >>> average_future_price:", df['average_future_price'])
        # print(" >>> deviation:", df['deviation'])
        # print(" >>> weight:", df['weight'])
        # print(" >>> direction_score:", df['direction_score'])
        # print(" >>> weighted_score:", df['weighted_score'])
        #
        # # Calculate final signal direction
        # total_score = df['weighted_score'].sum()
        # print(" >>> total_score:", total_score)
        #
        # # Determine market direction
        # market_direction = "long" if total_score > 0 else "short"
        # print(" >>> Market Direction:", market_direction)

"""


"""
   def calc_all_signals_score_for_direction(self, week_sig, day_sig, twelve_sig, eight_sig, four_sig, hour_sig, fifteen_sig):
        self.log.log(True, "D", None, "----------------------------")
        self.log.log(True, "D", None, ":calc_all_signals_score_for_direction:")

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
            # self.log.log(True, "D", None, msg)

            p_calc_score += self.calculate_signal_score(signal_record.signal, weight)
            return p_calc_score, ts_formatted

        if week_sig:
            (calculated_score, weekly_ts_formatted) = display_signal_and_calc_signal_score(week_sig,
                                                                                           weekly_weight,
                                                                                           calculated_score)
            # self.log.log(True, "I","   >>> 1W Score", calculated_score)
        if day_sig:
            (calculated_score, daily_ts_formatted) = display_signal_and_calc_signal_score(day_sig,
                                                                                          daily_weight,
                                                                                          calculated_score)
            # self.log.log(True, "I", "   >>> 1D Score", calculated_score)
        if twelve_sig:
            (calculated_score, twelve_hour_ts_formatted) = display_signal_and_calc_signal_score(twelve_sig,
                                                                                                twelve_hr_weight,
                                                                                                calculated_score)
            # self.log.log(True, "I", "   >>> 12H Score", calculated_score)
        if eight_sig:
            (calculated_score, eight_hour_ts_formatted) = display_signal_and_calc_signal_score(eight_sig,
                                                                                               eight_hr_weight,
                                                                                               calculated_score)
            # self.log.log(True, "I", "   >>> 8H Score", calculated_score)
        if four_sig:
            (calculated_score, four_hour_ts_formatted) = display_signal_and_calc_signal_score(four_sig,
                                                                                              four_hr_weight,
                                                                                              calculated_score)
            # self.log.log(True, "I", "   >>> 4H Score", calculated_score)
        if hour_sig:
            (calculated_score, one_hour_ts_formatted) = display_signal_and_calc_signal_score(hour_sig,
                                                                                             one_hour_weight,
                                                                                             calculated_score)
            # self.log.log(True, "I", "   >>> 1H Score", calculated_score)
        if fifteen_sig:
            (calculated_score, fifteen_min_ts_formatted) = display_signal_and_calc_signal_score(fifteen_sig,
                                                                                                fifteen_min_weight,
                                                                                                calculated_score)
            # self.log.log(True, "I", "   >>> 15m Score", calculated_score)

        timestamp_obj = {
            "weekly_ts_fmt": weekly_ts_formatted,
            "daily_ts_fmt": daily_ts_formatted,
            "twelve_hr_ts_fmt": twelve_hour_ts_formatted,
            "eight_hr_ts_fmt": eight_hour_ts_formatted,
            "four_hr_ts_fmt": four_hour_ts_formatted,
            "one_hr_ts_fmt": one_hour_ts_formatted,
            "fifteen_min_ts_fmt": fifteen_min_ts_formatted,
        }

        # self.log.log(True, "I",
        #                         "   >>> Total Trading Score", calculated_score)

        signal_calc_trade_direction = self.decide_trade_direction(calculated_score)
        # self.log.log(True, "I",
        #                         "   >>> Position Trade Direction",
        #                         signal_calc_trade_direction)

        return signal_calc_trade_direction, calculated_score, timestamp_obj

"""

# weekly_weight = int(config['trade.conditions']['weekly_weight'])
# five_day_weight = int(config['trade.conditions']['five_day_weight'])
# three_day_weight = int(config['trade.conditions']['three_day_weight'])
# two_day_weight = int(config['trade.conditions']['two_day_weight'])
# daily_weight = int(config['trade.conditions']['daily_weight'])
# twelve_hr_weight = int(config['trade.conditions']['twelve_hr_weight'])
# eight_hr_weight = int(config['trade.conditions']['eight_hr_weight'])
# six_hr_weight = int(config['trade.conditions']['six_hr_weight'])
# four_hr_weight = int(config['trade.conditions']['four_hr_weight'])
# three_hr_weight = int(config['trade.conditions']['three_hr_weight'])
# two_hr_weight = int(config['trade.conditions']['two_hr_weight'])
# one_hour_weight = int(config['trade.conditions']['one_hour_weight'])
# thirty_min_weight = float(config['trade.conditions']['thirty_min_weight'])
# twenty_min_weight = float(config['trade.conditions']['twenty_min_weight'])
# fifteen_min_weight = float(config['trade.conditions']['fifteen_min_weight'])
# ten_min_weight = float(config['trade.conditions']['ten_min_weight'])
# five_min_weight = float(config['trade.conditions']['five_min_weight'])

"""
    def calc_all_signals_score_for_dir_experiment(self, week_sig, day_sig, twelve_sig, eight_sig, four_sig, hour_sig,
                                                  fifteen_sig):
        self.log.log(True, "D", None, "----------------------------")
        self.log.log(True, "D", None, ":calc_all_signals_score_for_direction_2:")

        calculated_score = 0

        weekly_price = float(week_sig.price)
        daily_price = float(day_sig.price)
        twelve_hr_price = float(twelve_sig.price)
        eight_hr_price = float(eight_sig.price)
        four_hr_price = float(four_sig.price)
        one_hr_price = float(hour_sig.price)
        fifteen_min_price = float(fifteen_sig.price)

        weekly_weight = int(config['trade.conditions']['weekly_weight'])
        daily_weight = int(config['trade.conditions']['daily_weight'])
        ten_day_weight = daily_weight * 10
        five_day_weight = daily_weight * 5
        three_day_weight = daily_weight * 3
        two_day_weight = daily_weight * 2
        twelve_hr_weight = int(config['trade.conditions']['twelve_hr_weight'])
        eight_hr_weight = int(config['trade.conditions']['eight_hr_weight'])
        six_hr_weight = 6
        four_hr_weight = int(config['trade.conditions']['four_hr_weight'])
        three_hr_weight = 3
        two_hr_weight = 2
        one_hr_weight = int(config['trade.conditions']['one_hour_weight'])
        half_hr_weight = 0.5
        fifteen_min_weight = float(config['trade.conditions']['fifteen_min_weight'])
        # print(" weekly_weight:", weekly_weight)
        # print(" ten_day_weight:", ten_day_weight)
        # print(" five_day_weight:", five_day_weight)
        # print(" three_day_weight:", three_day_weight)
        # print(" two_day_weight:", two_day_weight)
        # print(" daily_weight:", daily_weight)
        # print(" twelve_hr_weight:", twelve_hr_weight)
        # print(" eight_hr_weight:", eight_hr_weight)
        # print(" six_hr_weight:", six_hr_weight)
        # print(" four_hr_weight:", four_hr_weight)
        # print(" three_hr_weight:", three_hr_weight)
        # print(" two_hr_weight:", two_hr_weight)
        # print(" one_hr_weight:", one_hr_weight)
        # print(" half_hr_weight:", half_hr_weight)
        # print(" fifteen_min_weight:", fifteen_min_weight)

        # Calculate Total Maximum and Minimum Scores:
        max_score = (weekly_weight + ten_day_weight + five_day_weight + three_day_weight
                     + two_day_weight + daily_weight + twelve_hr_weight + eight_hr_weight
                     + six_hr_weight + four_hr_weight + three_hr_weight + two_hr_weight
                     + one_hr_weight + half_hr_weight + fifteen_min_weight)
        min_score = (- weekly_weight - ten_day_weight - five_day_weight - three_day_weight
                     - two_day_weight - daily_weight - twelve_hr_weight - eight_hr_weight
                     - six_hr_weight - four_hr_weight - three_hr_weight - two_hr_weight
                     - one_hr_weight - half_hr_weight - fifteen_min_weight)

        # print(" max_score:", max_score)
        # print(" min_score:", min_score)

        def signal_direction(signal):
            # 1 = long, -1 = short
            return 1 if signal == 'long' else -1

        weekly_weight_dir = week_sig.signal
        ten_day_weight_dir = 'short'
        five_day_weight_dir = 'short'
        three_day_weight_dir = 'short'
        two_day_weight_dir = 'short'
        daily_weight_dir = day_sig.signal
        twelve_hr_weight_dir = twelve_sig.signal
        eight_hr_weight_dir = eight_sig.signal
        six_hr_weight_dir = 'long'
        four_hr_weight_dir = four_sig.signal
        three_hr_weight_dir = 'short'
        two_hr_weight_dir = 'short'
        one_hr_weight_dir = hour_sig.signal
        half_hr_weight_dir = 'short'
        fifteen_min_weight_dir = fifteen_sig.signal
        # print("weekly_weight_dir:", weekly_weight_dir)
        # print("ten_day_weight_dir:", ten_day_weight_dir)
        # print("five_day_weight_dir:", five_day_weight_dir)
        # print("three_day_weight_dir:", three_day_weight_dir)
        # print("two_day_weight_dir:", two_day_weight_dir)
        # print("daily_weight_dir:", daily_weight_dir)
        # print("twelve_hr_weight_dir:", twelve_hr_weight_dir)
        # print("eight_hr_weight_dir:", eight_hr_weight_dir)
        # print("six_hr_weight_dir:", six_hr_weight_dir)
        # print("four_hr_weight_dir:", four_hr_weight_dir)
        # print("three_hr_weight_dir:", three_hr_weight_dir)
        # print("two_hr_weight_dir:", two_hr_weight_dir)
        # print("one_hr_weight_dir:", one_hr_weight_dir)
        # print("half_hr_weight_dir:", half_hr_weight_dir)
        # print("fifteen_min_weight_dir:", fifteen_min_weight_dir)

        weekly_weight_dir = weekly_weight * signal_direction(week_sig.signal)
        ten_day_weight_dir = ten_day_weight * signal_direction('short')
        five_day_weight_dir = five_day_weight * signal_direction('short')
        three_day_weight_dir = three_day_weight * signal_direction('short')
        two_day_weight_dir = two_day_weight * signal_direction('short')
        daily_weight_dir = daily_weight * signal_direction(day_sig.signal)
        twelve_hr_weight_dir = twelve_hr_weight * signal_direction(twelve_sig.signal)
        eight_hr_weight_dir = eight_hr_weight * signal_direction(eight_sig.signal)
        six_hr_weight_dir = six_hr_weight * signal_direction('long')
        four_hr_weight_dir = four_hr_weight * signal_direction(four_sig.signal)
        three_hr_weight_dir = three_hr_weight * signal_direction('short')
        two_hr_weight_dir = two_hr_weight * signal_direction('short')
        one_hr_weight_dir = one_hr_weight * signal_direction(hour_sig.signal)
        half_hr_weight_dir = half_hr_weight * signal_direction('short')
        fifteen_min_weight_dir = float(fifteen_min_weight * signal_direction(fifteen_sig.signal))
        # print(" weekly_weight_dir:", weekly_weight_dir)
        # print(" ten_day_weight_dir:", ten_day_weight_dir)
        # print(" five_day_weight_dir:", five_day_weight_dir)
        # print(" three_day_weight_dir:", three_day_weight_dir)
        # print(" two_day_weight_dir:", two_day_weight_dir)
        # print(" daily_weight_dir:", daily_weight_dir)
        # print(" twelve_hr_weight_dir:", twelve_hr_weight_dir)
        # print(" eight_hr_weight_dir:", eight_hr_weight_dir)
        # print(" six_hr_weight_dir:", six_hr_weight_dir)
        # print(" four_hr_weight_dir:", four_hr_weight_dir)
        # print(" three_hr_weight_dir:", three_hr_weight_dir)
        # print(" two_hr_weight_dir:", two_hr_weight_dir)
        # print(" one_hr_weight_dir:", one_hr_weight_dir)
        # print(" half_hr_weight_dir:", half_hr_weight_dir)
        # print(" fifteen_min_weight_dir:", fifteen_min_weight_dir)

        calculated_score += weekly_weight_dir
        calculated_score += ten_day_weight_dir
        calculated_score += five_day_weight_dir
        calculated_score += three_day_weight_dir
        calculated_score += two_day_weight_dir
        calculated_score += daily_weight_dir
        calculated_score += twelve_hr_weight_dir
        calculated_score += eight_hr_weight_dir
        calculated_score += six_hr_weight_dir
        calculated_score += four_hr_weight_dir
        calculated_score += three_hr_weight_dir
        calculated_score += two_hr_weight_dir
        calculated_score += one_hr_weight_dir
        calculated_score += half_hr_weight_dir
        calculated_score += fifteen_min_weight_dir

        # TODO:
        #  How far back was the signal in time?
        #   How far the price was away?
        #   Signal direction long (+1) or short (-1)
        #   Signal weight (hours)

        def signal_futures_price_avg_price(signal):
            future_avg_price = 0
            for future_price_data in signal.future_prices:
                signal_future_bid_price = future_price_data.future_bid_price
                signal_future_ask_price = future_price_data.future_ask_price
                future_avg_price = (signal_future_bid_price + signal_future_ask_price) / 2
            return future_avg_price

        weekly_avg_fut_price = float(signal_futures_price_avg_price(week_sig))
        daily_avg_fut_price = float(signal_futures_price_avg_price(day_sig))
        twelve_avg_fut_price = float(signal_futures_price_avg_price(twelve_sig))
        eight_avg_fut_price = float(signal_futures_price_avg_price(eight_sig))
        four_avg_fut_price = float(signal_futures_price_avg_price(four_sig))
        one_avg_fut_price = float(signal_futures_price_avg_price(hour_sig))
        fifteen_fut_avg_price = float(signal_futures_price_avg_price(fifteen_sig))

        # print(" weekly_avg_fut_price:", weekly_avg_fut_price)
        # print(" daily_avg_fut_price:", daily_avg_fut_price)
        # print(" twelve_avg_fut_price:", twelve_avg_fut_price)
        # print(" eight_avg_fut_price:", eight_avg_fut_price)
        # print(" four_avg_fut_price:", four_avg_fut_price)
        # print(" one_avg_fut_price:", one_avg_fut_price)
        # print(" fifteen_avg_fut_price:", fifteen_fut_avg_price)

        def convert_time(timestamp):
            signals_dt = timestamp
            return signals_dt.strftime("%B %d, %Y, %I:%M %p")

        timestamp_obj = {
            "weekly_ts_fmt": convert_time(week_sig.timestamp),
            "daily_ts_fmt": convert_time(day_sig.timestamp),
            "twelve_hr_ts_fmt": convert_time(eight_sig.timestamp),
            "eight_hr_ts_fmt": convert_time(four_sig.timestamp),
            "four_hr_ts_fmt": convert_time(week_sig.timestamp),
            "one_hr_ts_fmt": convert_time(hour_sig.timestamp),
            "fifteen_min_ts_fmt": convert_time(fifteen_sig.timestamp)
        }

        def get_signal_time_diff(signal):
            print("\n time_unit:", signal.time_unit)
            # print(" timestamp:", signal.timestamp)

            # Define the EST timezone
            # est = pytz.timezone('America/New_York')

            # Convert the timestamp from UTC to EST
            # est_timestamp = signal.timestamp.astimezone(est)
            # print("est_timestamp:", est_timestamp)
            utc_timestamp = signal.timestamp.astimezone(pytz.utc)
            print("     utc_timestamp:", utc_timestamp)

            # Get the current datetime
            now = datetime.now(pytz.utc)
            # Get the current datetime in EST
            # now = datetime.now(pytz.utc).astimezone(est)
            print("     now:", now)

            # Calculate the difference from today
            # time_diff = now - signal.timestamp
            # time_diff = now - est_timestamp
            time_diff = now - utc_timestamp
            print("     time_diff:", time_diff)

            # Get total seconds from the timedelta
            # total_seconds = time_diff.total_seconds()
            # print("     total_seconds:", total_seconds)

            # seconds = time_diff.seconds
            # print(" seconds:", seconds)
            #
            # minutes = seconds / 60
            # print(" minutes:", minutes)
            #
            # hours = minutes / 60
            # print(" hours:", hours)
            #
            # days = hours / 24
            # print(" days:", days)

            # Simplify the display by checking for negative values
            # days = time_diff.days
            # if days < 0:
            #     days = 0
            # hours, remainder = divmod(time_diff.seconds, 3600)
            # minutes, seconds = divmod(remainder, 60)
            # return f"{days}d {hours}h {minutes}m {seconds}s"

        # weekly_diff = get_signal_time_diff(week_sig)
        # daily_diff = get_signal_time_diff(day_sig)
        # twelve_hr_diff = get_signal_time_diff(twelve_sig)
        # eight_hr_diff = get_signal_time_diff(eight_sig)
        # four_hr_diff = get_signal_time_diff(four_sig)
        # one_hr_diff = get_signal_time_diff(hour_sig)
        # fifteen_min_diff = get_signal_time_diff(fifteen_sig)
        # print(" weekly_diff:", weekly_diff)
        # print(" daily_diff:", daily_diff)
        # print(" twelve_hr_diff:", twelve_hr_diff)
        # print(" eight_hr_diff:", eight_hr_diff)
        # print(" four_hr_diff:", four_hr_diff)
        # print(" one_hr_diff:", one_hr_diff)
        # print(" fifteen_min_diff:", fifteen_min_diff)

        # self.log.log(True, "I",
        #                         "   >>> Total Trading Score", calculated_score)

        signal_calc_trade_direction = self.decide_trade_direction(calculated_score)
        # self.log.log(True, "I",
        #                         "   >>> Position Trade Direction",
        #                         signal_calc_trade_direction)

        return signal_calc_trade_direction, calculated_score, timestamp_obj

"""

"""

    def decide_trade_direction_new(self, calc_score, long_threshold_str, short_threshold_str):
        # self.log.log(True, "D", None, ":decide_trade_direction_new:")

        direction = 'neutral'
        dir_value = 0

        # Define thresholds for long and short decisions
        long_threshold = float(config['trade.conditions'][long_threshold_str])
        short_threshold = float(config['trade.conditions'][short_threshold_str])

        # decide_msg = f"Long: {long_threshold} Short: {short_threshold}"
        # self.log.log(True, "I", "   > Trading Thresholds", decide_msg)
        # self.log.log(True, "I", "   >    Calc Score", calc_score)

        if calc_score >= long_threshold:
            # self.log.log(True, "I",
            #                         "   >>> Strong bullish sentiment detected with a score of",
            #                         calc_score, "Going long.")
            direction = 'long'
            dir_value = 1
        elif calc_score <= short_threshold:
            # self.log.log(True, "I",
            #                         "   >>> Strong bearish sentiment detected with a score of",
            #                         calc_score, "Going short.")
            direction = 'short'
            dir_value = -1
        elif long_threshold > calc_score > short_threshold:
            # self.log.log(True, "I",
            #                         "   >>> Neutral sentiment detected with a score of",
            #                         calc_score, "Holding off.")
            direction = 'neutral'
            dir_value = 0

        return direction, dir_value

    def decide_direction_strength(self, p_total_grp_dir_val):
        # self.log.log(True, "D", None, ":decide_direction_strength:")

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

        # self.log.log(True, "I","   >>> Group Direction Value:", p_total_grp_dir_val)
        return trade_value
    
    
   def calc_all_signals_score_for_dir_new(self, signals_dict):
        self.log.log(True, "D", None, "----------------------------")
        self.log.log(True, "D", None, ":calc_all_signals_score_for_dir_new:")

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
                # self.log.log(True, "I", "   > Group 1 Signals", msg)

        # Loop through all of group 2 (middle timeframes) and calculate the signal weight together
        for time_frame, signal in signals_dict["group2"].items():
            if signal:
                signal_weight = float(config['trade.conditions'][f'{time_frame}_weight'])
                grp2_calc_score += self.calculate_signal_score(signal.signal, signal_weight)
                grp2_max += signal_weight
                signal_dir = 1 if signal.signal == 'long' else -1
                # msg = f" {time_frame} - Signal: {signal.signal} Weight: {signal_weight * signal_dir}"
                # self.log.log(True, "I", "   > Group 2 Signals", msg)

        # Loop through all of group 3 (lower timeframes) and calculate the signal weight together
        for time_frame, signal in signals_dict["group3"].items():
            if signal:
                signal_weight = float(config['trade.conditions'][f'{time_frame}_weight'])
                grp3_calc_score += self.calculate_signal_score(signal.signal, signal_weight)
                grp3_calc_score = round(grp3_calc_score, 3)
                grp3_max += signal_weight
                signal_dir = 1 if signal.signal == 'long' else -1
                # msg = f" {time_frame} - Signal: {signal.signal} Weight: {signal_weight * signal_dir}"
                # self.log.log(True, "I", "   > Group 3 Signals", msg)

        # Log out the signal weights min and max, plus calculated score
        grp1_msg = f"Max: {grp1_max} | Score {grp1_calc_score} | Min: {-grp1_max}"
        self.log.log(True, "I", "   > Group 1", grp1_msg)

        grp2_msg = f"Max: {grp2_max} | Score {grp2_calc_score} | Min: {-grp2_max}"
        self.log.log(True, "I", "   > Group 2", grp2_msg)

        grp3_msg = f"Max: {grp3_max} | Score {grp3_calc_score} | Min: {-grp3_max}"
        self.log.log(True, "I", "   > Group 3", grp3_msg)

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
        # self.log.log(True, "I", "   > Group 1 Direction Val",
        #                         grp1_direction, grp1_dir_val)
        # self.log.log(True, "I", "   > Group 2 Direction Val",
        #                         grp2_direction, grp2_dir_val)
        # self.log.log(True, "I", "   > Group 3 Direction Val",
        #                         grp3_direction, grp3_dir_val)

        # TODO: we're using the 1, -1, 0 for each group, but the method is designed for total value

        grp1_strength_trade_val = self.decide_direction_strength(grp1_dir_val)
        self.log.log(True, "I", "   >>> Group 1 (HTF) Strength Trade Value",
                     grp1_strength_trade_val, grp1_dir_val)

        grp2_strength_trade_val = self.decide_direction_strength(grp2_dir_val)
        self.log.log(True, "I", "   >>> Group 2 (MTF) Strength Trade Value",
                     grp2_strength_trade_val, grp2_dir_val)

        grp3_strength_trade_val = self.decide_direction_strength(grp3_dir_val)
        self.log.log(True, "I", "   >>> Group 3 (LTF) Strength Trade Value",
                     grp3_strength_trade_val, grp3_dir_val)

        total_grp_dir_value = grp1_dir_val + grp2_dir_val + grp3_dir_val
        # self.log.log(True, "I", "   >>> Total Group Direction Value", total_grp_dir_value)

        total_strength_trade_val = self.decide_direction_strength(total_grp_dir_value)
        # self.log.log(True, "I", "   >>> Total Strength Trade Value", total_strength_trade_val)

        return total_grp_dir_value, total_strength_trade_val

"""

"""
    @staticmethod
    def calculate_signal_score(signal: str, score: float):
        # self.log.log(True, "D", None, ":calculate_signal_score:")
        calc_score = 0
        # long = BUY
        if signal == "long":
            calc_score += score
        # short = SELL
        elif signal == "short":
            calc_score -= score
        return calc_score

    def decide_trade_direction(self, calc_score):
        # self.log.log(True, "D", None, ":decide_trade_direction:")

        # Define thresholds for long and short decisions
        # long_threshold = 100
        # short_threshold = -100
        long_threshold = int(config['trade.conditions']['trade_direction_long_threshold'])
        short_threshold = int(config['trade.conditions']['trade_direction_short_threshold'])

        if calc_score >= long_threshold:
            self.log.log(True, "I",
                         "   >>> Strong bullish sentiment detected with a score of",
                         calc_score, "Going long.")
            return 'long'
        elif calc_score <= short_threshold:
            self.log.log(True, "I",
                         "   >>> Strong bearish sentiment detected with a score of",
                         calc_score, "Going short.")
            return 'short'
        elif long_threshold > calc_score > short_threshold:
            self.log.log(True, "I",
                         "   >>> Neutral sentiment detected with a score of",
                         calc_score, "Holding off.")
            return 'neutral'

    def calc_all_signals_score_for_direction(self, week_sig, day_sig, twelve_sig, eight_sig, four_sig,
                                             hour_sig, fifteen_sig):
        self.log.log(True, "D", None, "----------------------------")
        self.log.log(True, "D", None, ":calc_all_signals_score_for_direction:")

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
            # self.log.log(True, "D", None, msg)

            p_calc_score += self.calculate_signal_score(signal_record.signal, weight)
            return p_calc_score, ts_formatted

        if week_sig:
            (calculated_score, weekly_ts_formatted) = display_signal_and_calc_signal_score(week_sig,
                                                                                           weekly_weight,
                                                                                           calculated_score)
            # self.log.log(True, "I","   >>> 1W Score", calculated_score)
        if day_sig:
            (calculated_score, daily_ts_formatted) = display_signal_and_calc_signal_score(day_sig,
                                                                                          daily_weight,
                                                                                          calculated_score)
            # self.log.log(True, "I", "   >>> 1D Score", calculated_score)
        if twelve_sig:
            (calculated_score, twelve_hour_ts_formatted) = display_signal_and_calc_signal_score(twelve_sig,
                                                                                                twelve_hr_weight,
                                                                                                calculated_score)
            # self.log.log(True, "I", "   >>> 12H Score", calculated_score)
        if eight_sig:
            (calculated_score, eight_hour_ts_formatted) = display_signal_and_calc_signal_score(eight_sig,
                                                                                               eight_hr_weight,
                                                                                               calculated_score)
            # self.log.log(True, "I", "   >>> 8H Score", calculated_score)
        if four_sig:
            (calculated_score, four_hour_ts_formatted) = display_signal_and_calc_signal_score(four_sig,
                                                                                              four_hr_weight,
                                                                                              calculated_score)
            # self.log.log(True, "I", "   >>> 4H Score", calculated_score)
        if hour_sig:
            (calculated_score, one_hour_ts_formatted) = display_signal_and_calc_signal_score(hour_sig,
                                                                                             one_hour_weight,
                                                                                             calculated_score)
            # self.log.log(True, "I", "   >>> 1H Score", calculated_score)
        if fifteen_sig:
            (calculated_score, fifteen_min_ts_formatted) = display_signal_and_calc_signal_score(fifteen_sig,
                                                                                                fifteen_min_weight,
                                                                                                calculated_score)
            # self.log.log(True, "I", "   >>> 15m Score", calculated_score)

        timestamp_obj = {
            "weekly_ts_fmt": weekly_ts_formatted,
            "daily_ts_fmt": daily_ts_formatted,
            "twelve_hr_ts_fmt": twelve_hour_ts_formatted,
            "eight_hr_ts_fmt": eight_hour_ts_formatted,
            "four_hr_ts_fmt": four_hour_ts_formatted,
            "one_hr_ts_fmt": one_hour_ts_formatted,
            "fifteen_min_ts_fmt": fifteen_min_ts_formatted,
        }

        # self.log.log(True, "I",
        #                         "   >>> Total Trading Score", calculated_score)

        signal_calc_trade_direction = self.decide_trade_direction(calculated_score)
        # self.log.log(True, "I",
        #                         "   >>> Position Trade Direction",
        #                         signal_calc_trade_direction)

        return signal_calc_trade_direction, calculated_score, timestamp_obj


    # weekly_signals = self.signal_processor.get_latest_weekly_signal()
    # daily_signals = self.signal_processor.get_latest_daily_signal()
    # twelve_hour_signals = self.signal_processor.get_latest_twelve_hr_signal()
    # eight_hour_signals = self.signal_processor.get_latest_eight_hr_signal()
    # four_hour_signals = self.signal_processor.get_latest_four_hr_signal()
    # one_hour_signals = self.signal_processor.get_latest_one_hour_signal()
    fifteen_min_signals = self.signal_processor.get_latest_fifteen_min_signal()

    # signal_calc_trade_direction, signal_score, ts_obj = self.calc_all_signals_score_for_direction(weekly_signals,
    #                                                                                               daily_signals,
    #                                                                                               twelve_hour_signals,
    #                                                                                               eight_hour_signals,
    #                                                                                               four_hour_signals,
    #                                                                                               one_hour_signals,
    #                                                                                               fifteen_min_signals)
"""