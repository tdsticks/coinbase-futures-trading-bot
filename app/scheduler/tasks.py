from flask_apscheduler import APScheduler
from datetime import datetime
import pytz
from pprint import pprint as pp
import time

#######################
# AP Scheduler
#######################

# initialize scheduler
scheduler = APScheduler()


def setup_scheduler(app):
    # print(":setup_scheduler:")
    app.custom_log.log(True, "D", None, "Setting up scheduler...")

    enable_balance_summary = app.config['ENABLE_BALANCE_SUMMARY']
    enable_coinbase_futures_products = app.config['ENABLE_COINBASE_FUTURES_PRODUCTS']
    enable_trading_conditions = app.config['ENABLE_TRADING_CONDITIONS']
    enable_list_and_store_future_orders = app.config['ENABLE_LIST_AND_STORE_FUTURE_ORDERS']

    balance_summary_time = app.config['BALANCE_SUMMARY_TIME']
    coinbase_futures_products_time = app.config['COINBASE_FUTURES_PRODUCTS_TIME']
    trading_conditions_time = app.config['TRADING_CONDITIONS_TIME']
    future_orders_time = app.config['FUTURE_ORDERS_TIME']

    @scheduler.task('interval', id='balance_summary', seconds=balance_summary_time, misfire_grace_time=900)
    def get_balance_summary_job():
        app.custom_log.log(True, "D", None, ":get_balance_summary_job:")

        now = datetime.now(pytz.utc)
        # print("Is trading time?", app.trade_manager.is_trading_time(now))

        with app.app_context():
            # Check if the market is open or not
            if app.trade_manager.is_trading_time(now):
                # Balance Summary get and store
                futures_balance = app.cb_adv_api.get_balance_summary()
                # pp(futures_balance)

                app.cb_adv_api.store_futures_balance_summary(futures_balance)

    # Runs every 6 hours
    @scheduler.task('interval', id='products', seconds=coinbase_futures_products_time, misfire_grace_time=900)
    def get_coinbase_futures_products_job():
        app.custom_log.log(True, "D", None, msg1=":get_coinbase_futures_products_job:")

        now = datetime.now(pytz.utc)
        # print("Is trading time?",  app.trade_manager.is_trading_time(now))

        with app.app_context():
            # Check if the market is open or not
            if app.trade_manager.is_trading_time(now):
                list_future_products = app.cb_adv_api.list_products("FUTURE")
                # pp(list_future_products)
                app.cb_adv_api.store_btc_futures_products(list_future_products)

    @scheduler.task('interval', id='trading', seconds=trading_conditions_time, misfire_grace_time=900)
    def check_trading_conditions_job():
        app.custom_log.log(True, "I", None, msg1="------------------------------")
        app.custom_log.log(True, "I", None, msg1=":check_trading_conditions_job:")

        # NOTE: This is the main trading method with additional methods
        #   to check profit and loss, plus DCA and close out trades

        now = datetime.now(pytz.utc)

        with app.app_context():
            # Check if the market is open or not
            if app.trade_manager.is_trading_time(now):
                app.trade_manager.check_trading_conditions()

    @scheduler.task('interval', id='orders', seconds=future_orders_time, misfire_grace_time=900)
    def list_and_store_future_orders_job():
        app.custom_log.log(True, "I", None, msg1="------------------------------")
        app.custom_log.log(True, "D", None, msg1=":list_and_store_future_orders_job:")

        # Check if the market is open or not
        now = datetime.now(pytz.utc)

        # BUG: Was getting an error from this order_status: UNKNOWN_ORDER_STATUS

        all_order_status = ["OPEN", "FILLED", "CANCELLED", "EXPIRED", "FAILED"]
        # all_order_status = ["OPEN"]

        def run_all_list_orders(statuses, month, product_id):
            app.custom_log.log(True, "D", None, None)
            month_msg = f"Month: {month}"
            product_id_msg = f"Product: {product_id}"
            app.custom_log.log(True, "D", month_msg, product_id_msg)
            for status in statuses:
                # Need to delay the API call due to running too many at a time
                time.sleep(1)
                orders = app.cb_adv_api.list_orders(product_id=product_id, order_status=status)
                status_msg = f" {status}"
                app.custom_log.log(True, "D", status_msg, "Cnt", len(orders['orders']))

                # if status == "FAILED":
                #     app.custom_log.log(True, "D", status_msg, "Failed Orders",
                #                        orders['orders'])

                if len(orders['orders']) > 0:
                    app.cb_adv_api.store_or_update_orders_from_api(orders)

        if app.trade_manager.is_trading_time(now):
            with app.app_context():
                curr_month = app.cb_adv_api.get_current_short_month_uppercase()
                next_month = app.cb_adv_api.get_next_short_month_uppercase()
                # app.custom_log.log(True, "I","next_month", next_month)

                current_future_product = app.cb_adv_api.get_relevant_future_from_db()
                next_months_future_product = app.cb_adv_api.get_relevant_future_from_db(month_override=next_month)
                curr_product_id = current_future_product.product_id
                next_product_id = next_months_future_product.product_id

                run_all_list_orders(all_order_status, curr_month, curr_product_id)
                # run_all_list_orders(all_order_status, next_month, next_product_id)

                # List Orders
                # ORDER TYPES:
                # [OPEN, FILLED, CANCELLED, EXPIRED, FAILED, UNKNOWN_ORDER_STATUS]
                # all_orders = app.cb_adv_api.list_orders(product_id=future_product.product_id, order_status=None)
                ## print("all_orders count:", len(all_orders['orders']))
                # app.custom_log.log(True, msg1="all_orders:", msg2=len(all_orders['orders']))
                #
                # if len(all_orders['orders']) > 0:
                #     app.cb_adv_api.store_or_update_orders_from_api(all_orders)

    # @scheduler.task('interval', id='do_job_6', seconds=15, misfire_grace_time=900)
    # def manual_ladder_orders_job():
    #     print('\n:manual_ladder_orders_job:')
    #
    #     next_months_product_id, next_month = app.cb_adv_api.check_for_contract_expires()
    #     # print("next_months_product_id:", next_months_product_id)
    #     # print("next_month:", next_month)
    #
    #     # Get this months current product
    #     relevant_future_product = app.cb_adv_api.get_relevant_future_from_db(month_override=next_month)
    #     # print(" relevant_future_product:", relevant_future_product.product_id)
    #
    #     # side = "BUY"
    #     side = "SELL"
    #     # print(" side:", side)
    #
    #     # Also, create the DCA ladder orders
    #     app.trade_manager.create_ladder_trades(trade_side=side,
    #                                            product_id=relevant_future_product.product_id)

    scheduler.init_app(app)
    scheduler.start()

    # Check if we've disabled any of the schedule jobs from the bot_config.ini file
    if not enable_balance_summary:
        app.custom_log.log(True, "I", " !!! Pausing Schedule Job", msg1="balance_summary")
        scheduler.pause_job('balance_summary')
    if not enable_coinbase_futures_products:
        app.custom_log.log(True, "I", " !!! Pausing Schedule Job", msg1="products")
        scheduler.pause_job('products')
    if not enable_trading_conditions:
        app.custom_log.log(True, "I", " !!! Pausing Schedule Job", msg1="trading")
        scheduler.pause_job('trading')
    if not enable_list_and_store_future_orders:
        app.custom_log.log(True, "I", " !!! Pausing Schedule Job", msg1="orders")
        scheduler.pause_job('orders')
