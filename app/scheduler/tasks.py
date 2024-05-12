from flask_apscheduler import APScheduler
from datetime import datetime
import pytz

#######################
# AP Scheduler
#######################

# initialize scheduler
scheduler = APScheduler()


def setup_scheduler(app):
    print(":setup_scheduler:")

    app.logger.info("Setting up scheduler...")

    disable_balance_summary = app.config['DISABLE_BALANCE_SUMMARY']
    disable_coinbase_futures_products = app.config['DISABLE_COINBASE_FUTURES_PRODUCTS']
    disable_trading_conditions = app.config['DISABLE_TRADING_CONDITIONS']
    disable_list_and_store_future_orders = app.config['DISABLE_LIST_AND_STORE_FUTURE_ORDERS']

    balance_summary_time = app.config['BALANCE_SUMMARY_TIME']
    coinbase_futures_products_time = app.config['COINBASE_FUTURES_PRODUCTS_TIME']
    trading_conditions_time = app.config['TRADING_CONDITIONS_TIME']
    future_orders_time = app.config['FUTURE_ORDERS_TIME']

    """
    @scheduler.task('interval', id='balance_summary', seconds=balance_summary_time, misfire_grace_time=900)
    def get_balance_summary_job():
        app.logger.log(True, "D", None, ":get_balance_summary_job:")

        now = datetime.now(pytz.utc)
        # print("Is trading time?", tm.is_trading_time(now))

        # Check if the market is open or not
        if tm.is_trading_time(now):
            # Balance Summary get and store
            futures_balance = cbapi.get_balance_summary()
            # pp(futures_balance)

            cbapi.store_futures_balance_summary(futures_balance)

    # Runs every 6 hours
    @scheduler.task('interval', id='products', seconds=coinbase_futures_products_time, misfire_grace_time=900)
    def get_coinbase_futures_products_job():
        log.log(True, "D", None, msg1=":get_coinbase_futures_products_job:")

        now = datetime.now(pytz.utc)
        # print("Is trading time?", tm.is_trading_time(now))

        # Check if the market is open or not
        if tm.is_trading_time(now):
            list_future_products = cbapi.list_products("FUTURE")
            # pp(list_future_products)
            cbapi.store_btc_futures_products(list_future_products)


    @scheduler.task('interval', id='trading', seconds=trading_conditions_time, misfire_grace_time=900)
    def check_trading_conditions_job():
        log.log(True, "I", None, msg1="------------------------------")
        log.log(True, "I", None, msg1=":check_trading_conditions_job:")

        # NOTE: This is the main trading method with additional methods
        #   to check profit and loss, plus DCA and close out trades

        now = datetime.now(pytz.utc)

        # Check if the market is open or not
        if tm.is_trading_time(now):
            tm.check_trading_conditions()


    @scheduler.task('interval', id='orders', seconds=future_orders_time, misfire_grace_time=900)
    def list_and_store_future_orders_job():
        log.log(True, "I", None, msg1="------------------------------")
        log.log(True, "D", None, msg1=":list_and_store_future_orders_job:")

        # Check if the market is open or not
        now = datetime.now(pytz.utc)

        # BUG: Was getting an error from this order_status: UNKNOWN_ORDER_STATUS

        all_order_status = ["OPEN", "FILLED", "CANCELLED", "EXPIRED", "FAILED"]

        # all_order_status = ["OPEN"]

        def run_all_list_orders(statuses, month, product_id):
            log.log(True, "D", None, None)
            month_msg = f"Month: {month}"
            product_id_msg = f"Product: {product_id}"
            log.log(True, "D", month_msg, product_id_msg)
            for status in statuses:
                orders = cbapi.list_orders(product_id=product_id, order_status=status)
                status_msg = f" {status}"
                log.log(True, "D", status_msg, "Cnt", len(orders['orders']))

                # if status == "FAILED":
                #     log.log(True, "D", status_msg, "Failed Orders",
                #                        orders['orders'])

                if len(orders['orders']) > 0:
                    cbapi.store_or_update_orders_from_api(orders)

        if tm.is_trading_time(now):
            curr_month = cbapi.get_current_short_month_uppercase()
            next_month = cbapi.get_next_short_month_uppercase()
            # log.log(True, "I","next_month", next_month)

            current_future_product = cbapi.get_relevant_future_from_db()
            next_months_future_product = cbapi.get_relevant_future_from_db(month_override=next_month)
            curr_product_id = current_future_product.product_id
            next_product_id = next_months_future_product.product_id

            run_all_list_orders(all_order_status, curr_month, curr_product_id)
            run_all_list_orders(all_order_status, next_month, next_product_id)

            # List Orders
            # ORDER TYPES:
            # [OPEN, FILLED, CANCELLED, EXPIRED, FAILED, UNKNOWN_ORDER_STATUS]
            # all_orders = cbapi.list_orders(product_id=future_product.product_id, order_status=None)
            ## print("all_orders count:", len(all_orders['orders']))
            # log.log(True, msg1="all_orders:", msg2=len(all_orders['orders']))
            #
            # if len(all_orders['orders']) > 0:
            #     cbapi.store_or_update_orders_from_api(all_orders)
    """

    # @scheduler.task('interval', id='do_job_6', seconds=15000, misfire_grace_time=900)
    # def manual_ladder_orders_job():
    #     print('\n:test_ladder_orders_job:')
    #
    #     next_months_product_id, next_month = tm.check_for_contract_expires()
    #     print("next_months_product_id:", next_months_product_id)
    #     print("next_month:", next_month)
    #
    #     # Get this months current product
    #     relevant_future_product = cbapi.get_relevant_future_from_db(month_override=next_month)
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
    #     print(" side:", side)
    #
    #     # How many ladder orders?
    #     # ladder_order_qty = 8
    #     ladder_order_qty = int(config['dca.ladder.trade_percentages']['ladder_quantity'])
    #
    #     # Override the starting entry price
    #     manual_price = '58945'
    #
    #     tm.ladder_orders(quantity=ladder_order_qty, side=side,
    #                      product_id=relevant_future_product.product_id,
    #                      bid_price=cur_future_bid_price,
    #                      ask_price=cur_future_ask_price,
    #                      manual_price=manual_price)

    # @scheduler.task('interval', id='future_positions', seconds=10, misfire_grace_time=900)
    # def get_current_position_job():
    #     log.log(True, "I", None, msg1="------------------------------")
    #     log.log(True, "I", None, msg1=":get_current_position_job:")
    #
    #     future_contract = cbapi.get_relevant_future_from_db()
    #
    #     # Get Current Positions
    #     future_positions = cbapi.get_future_position(future_contract.product_id)
    #     pp(future_positions)

    # scheduler.init_app(app)
    # scheduler.start()
    #
    # # Check if we've disabled any of the schedule jobs from the bot_config.ini file
    # if disable_balance_summary == 'True':
    #     log.log(True, "I", " !!! Pausing Schedule Job", msg1="balance_summary")
    #     scheduler.pause_job('balance_summary')
    # if disable_coinbase_futures_products == 'True':
    #     log.log(True, "I", " !!! Pausing Schedule Job", msg1="products")
    #     scheduler.pause_job('products')
    # if disable_trading_conditions == 'True':
    #     log.log(True, "I", " !!! Pausing Schedule Job", msg1="trading")
    #     scheduler.pause_job('trading')
    # if disable_list_and_store_future_orders == 'True':
    #     log.log(True, "I", " !!! Pausing Schedule Job", msg1="orders")
    #     scheduler.pause_job('orders')