from datetime import datetime
import pytz
import time


class TrailingTakeProfit:
    def __init__(self, app):
        """
        Initialize the TrailingTakeProfit class with configuration settings.

        :param app: The application instance containing configuration and trade manager.
        """
        self.log = app.custom_log.log
        self.log(True, "D", None, ":Initializing TrailingTakeProfit:")
        self.app = app
        self.tm = app.trade_manager
        self.cbapi = app.cb_adv_api

        self.initial_take_profit = app.config['INITIAL_TAKE_PROFIT']
        self.trailing_threshold = app.config['TRAILING_THRESHOLD']
        self.trailing_offset = app.config['TRAILING_OFFSET']
        self.avg_entry_price = None
        self.highest_price = None  # For long positions
        self.lowest_price = None  # For short positions
        self.trailing_tp_active = False

    def set_entry_price(self, avg_entry_price, take_profit_side):
        """
        Set the entry price and initialize highest or lowest price based on the side.

        :param avg_entry_price: Average entry price of the position.
        :param take_profit_side: Side of the take profit order ("SELL" for long, "BUY" for short).
        """
        if not avg_entry_price and not take_profit_side:
            # print(f" > websocket, waiting for avg entry price...{avg_entry_price}")
            return
        # print(":set_entry_price:")
        # print(" avg_entry_price:", avg_entry_price)
        # print(" take_profit_side:", take_profit_side)
        # print(" initial_take_profit:", self.initial_take_profit)
        self.avg_entry_price = avg_entry_price
        # print(" avg_entry_price:", self.avg_entry_price)

        if take_profit_side == "SELL":
            self.highest_price = int(round(avg_entry_price * (1 + self.initial_take_profit)))
            self.lowest_price = None
        elif take_profit_side == "BUY":
            self.lowest_price = int(round(avg_entry_price * (1 - self.initial_take_profit)))
            self.highest_price = None
        # print(" highest_price:", self.highest_price)
        # print(" lowest_price:", self.lowest_price)

    def update_price(self, current_price, take_profit_side):
        """
        Update the current price and check if trailing take profit should be activated.

        :param current_price: The current market price.
        :param take_profit_side: Side of the take profit order ("SELL" for long, "BUY" for short).
        """
        if not self.avg_entry_price and not take_profit_side:
            return
        print(":update_price:")
        # print(" trailing_tp_active 1:", self.trailing_tp_active)
        print(" current_price:", current_price)
        print(" take_profit_side:", take_profit_side)
        print(" highest_price:", self.highest_price)
        print(" lowest_price:", self.lowest_price)

        # Update highest/lowest price
        if take_profit_side == "SELL":
            if current_price > self.highest_price:
                self.highest_price = current_price
        elif take_profit_side == "BUY":
            if current_price < self.lowest_price:
                self.lowest_price = current_price

        # Check if we should activate trailing take profit
        if take_profit_side == "SELL":
            if current_price >= self.avg_entry_price * (1 + self.trailing_threshold):
                self.trailing_tp_active = True
                print(
                    f"{take_profit_side} CP: {current_price} >= "
                    f"TTP: {self.avg_entry_price * (1 + self.trailing_threshold)}"
                    f"TTP Active: {self.trailing_tp_active}"
                )
            else:
                self.trailing_tp_active = True
                print(
                    f"{take_profit_side} CP: {current_price} < "
                    f"TTP: {self.avg_entry_price * (1 + self.trailing_threshold)}"
                    f"TTP Active: {self.trailing_tp_active}"
                )
        elif take_profit_side == "BUY":
            self.trailing_tp_active = True
            if current_price <= self.avg_entry_price * (1 - self.trailing_threshold):
                print(
                    f"{take_profit_side} CP: {current_price} <= "
                    f"TTP: {self.avg_entry_price * (1 + self.trailing_threshold)}"
                    f"TTP Active: {self.trailing_tp_active}"
                )
            else:
                self.trailing_tp_active = False
                print(
                    f"{take_profit_side} CP: {current_price} > "
                    f"TTP: {self.avg_entry_price * (1 + self.trailing_threshold)}"
                    f"TTP Active: {self.trailing_tp_active}"
                )
        # print(" trailing_tp_active 2:", self.trailing_tp_active)

        # If trailing take profit is active, calculate the new trailing TP price
        if self.trailing_tp_active:
            trailing_tp_price = 0
            if take_profit_side == "SELL":
                trailing_tp_price = self.highest_price * (1 - self.trailing_offset)
            elif take_profit_side == "BUY":
                trailing_tp_price = self.lowest_price * (1 + self.trailing_offset)
            print(f"    Trailing Take Profit Price: {trailing_tp_price}")
            # self.log(True, "I", "Trailing Take Profit Price", trailing_tp_price)
            # Place or update take profit order logic here

    def run_trailing_take_profit(self):
        """
        Run the trailing take profit logic continuously.
        """
        print(":run_trailing_take_profit:")

        product_id = "BIT-31MAY24-CDE"

        while True:
            # Check if the market is open or not
            now = datetime.now(pytz.utc)

            if self.tm.is_trading_time(now):
                bid_ask = self.cbapi.get_current_bid_ask_prices(product_id)
                bid_price = bid_ask['pricebooks'][0]['bids'][0]['price']
                ask_price = bid_ask['pricebooks'][0]['asks'][0]['price']
                avg_bid_ask = int((int(bid_price) + int(ask_price)) / 2)
                # print("avg_bid_ask:", avg_bid_ask)
                # self.log(True, "I", None, cur_prices_msg)

                self.set_entry_price(self.tm.avg_filled_price, self.tm.take_profit_side)
                self.update_price(avg_bid_ask, self.tm.take_profit_side)

            time.sleep(5)  # Sleep for 2 seconds


# from coinbase.websocket import (WSClient, WSClientConnectionClosedException,
#                                 WSClientException)
# import json

    # def process_message(self, msg):
    #     json_msg = json.loads(msg)
    #     if 'events' in json_msg:
    #         for event in json_msg['events']:
    #             print("event:", event)
    #             if 'tickers' in event:
    #                 for ticker in event['tickers']:
    #                     print("ticker:", ticker)
    #                     price = float(ticker['price'])
    #                     print(f"    > Ticker Price: {price}")
    #
    #                     # TODO: Need to factor in Longs and Shorts
    #
    #                     self.set_entry_price(self.tm.avg_filled_price,
    #                                          self.tm.take_profit_side)
    #                     self.update_price(price, self.tm.take_profit_side)
    #
    # def run_cb_wsclient(self):
    #     print(":run_cb_wsclient:")
    #
    # channel_names = [
    #     "level2",
    #     "user",
    #     "ticker",
    #     "ticker_batch",
    #     "status",
    #     "market_trades",
    #     "candles"
    # ]
    #     # product_id = "BTC-USD"
    #     product_id = "BIT-31MAY24-CDE"
    #
    #     # client = WSClient(on_message=self.process_message, timeout=5, retry=True, max_size=65536)
    #     client = WSClient(api_key=self.app.config['API_KEY'],
    #                       api_secret=self.app.config['API_SECRET'],
    #                       on_message=self.process_message,
    #                       timeout=5, retry=True, max_size=65536)
    #     print(" client:", client)
    #     try:
    #         client.open()
    #         print(" client open:")
    #         client.user(product_ids=[product_id])
    #         # client.level2(product_ids=[product_id])
    #         # client.market_trades(product_ids=[product_id])
    #         # client.ticker(product_ids=[product_id])
    #         # client.ticker_batch(product_ids=[product_id])
    #         print(" client user:")
    #         # print(" client level2:")
    #         # print(" client market_trades:")
    #         # print(" client ticker:")
    #         # print(" client ticker_batch:")
    #         client.run_forever_with_exception_check()
    #         print(" client run_forever_with_exception_check:")
    #         # client.sleep_with_exception_check(sleep=1)
    #     except WSClientConnectionClosedException as e:
    #         print(" Web Socket: Connection closed! Retry attempts exhausted.", e)
    #     except WSClientException as e:
    #         print(" Web Socket: Error encountered!", e)
    #     finally:
    #         client.user_unsubscribe(product_ids=[product_id])
    #         # client.level2_unsubscribe(product_ids=[product_id])
    #         # client.market_trades_unsubscribe(product_ids=[product_id])
    #         # client.ticker_unsubscribe(product_ids=[product_id])
    #         # client.ticker_batch_unsubscribe(product_ids=[product_id])
    #         print(" client level2_unsubscribe:")
    #         # print(" client level2_unsubscribe:")
    #         # print(" client market_trades_unsubscribe:")
    #         # print(" client ticker_unsubscribe:")
    #         # print(" client ticker_batch_unsubscribe:")
    #         client.close()
    #         print(" client close:")
