from coinbase.websocket import (WSClient, WSClientConnectionClosedException,
                                WSClientException)
import json
import time


class TrailingTakeProfit:
    def __init__(self, app):
        self.log = app.custom_log.log
        self.log(True, "D", None, ":Initializing TrailingTakeProfit:")
        self.app = app
        self.trade_manager = app.trade_manager

        self.initial_take_profit = app.config['INITIAL_TAKE_PROFIT']
        self.trailing_threshold = app.config['TRAILING_THRESHOLD']
        self.trailing_offset = app.config['TRAILING_OFFSET']
        self.entry_price = None
        self.highest_price = None
        self.trailing_tp_active = False

        # channel_names = [
        #     "level2",
        #     "user",
        #     "ticker",
        #     "ticker_batch",
        #     "status",
        #     "market_trades",
        #     "candles"
        # ]

    def process_message(self, msg):
        json_msg = json.loads(msg)
        if 'events' in json_msg:
            for event in json_msg['events']:
                # print("event:", event)
                if 'tickers' in event:
                    for ticker in event['tickers']:
                        # print("ticker:", ticker)
                        price = float(ticker['price'])
                        print(f"Ticker Price: {price}")

                        # TODO: Need to factor in Longs and Shorts

                        self.set_entry_price(self.trade_manager.avg_filled_price)
                        self.update_price(price)

    def set_entry_price(self, avg_entry_price):
        if not avg_entry_price:
            print("websocket, waiting for entry price...")
            return
        print("avg_entry_price:", avg_entry_price)
        print("initial_take_profit:", self.initial_take_profit)
        self.entry_price = avg_entry_price
        self.highest_price = avg_entry_price * (1 + self.initial_take_profit)
        print("entry_price:", self.entry_price)
        print("highest_price:", self.highest_price)

    def update_price(self, current_price):
        if not self.entry_price:
            return

        print("trailing_tp_active 1:", self.trailing_tp_active)

        # Update highest price if the current price is higher
        if current_price > self.highest_price:
            self.highest_price = current_price

        # Check if we should activate trailing take profit
        if current_price >= self.entry_price * (1 + self.trailing_threshold):
            self.trailing_tp_active = True
        print("trailing_tp_active 2:", self.trailing_tp_active)

        if self.trailing_tp_active:
            trailing_tp_price = self.highest_price * (1 - self.trailing_offset)
            print(f"Trailing Take Profit Price: {trailing_tp_price}")
            # Place or update take profit order logic here

    def run_cb_wsclient(self):
        print(":run_cb_wsclient:")

        # client = WSClient(on_message=self.process_message, timeout=5, retry=True, max_size=65536)
        client = WSClient(api_key=self.app.config['API_KEY'],
                          api_secret=self.app.config['API_SECRET'],
                          on_message=self.process_message,
                          timeout=5, retry=True, max_size=65536)
        try:
            client.open()
            # client.ticker(product_ids=["BTC-USD"])
            client.ticker_batch(product_ids=["BTC-USD"])
            client.run_forever_with_exception_check()
            # client.sleep_with_exception_check(sleep=1)
        except WSClientConnectionClosedException as e:
            print("Web Socket: Connection closed! Retry attempts exhausted.", e)
        except WSClientException as e:
            print("Web Socket: Error encountered!", e)
        finally:
            # client.ticker_unsubscribe(product_ids=["BTC-USD"])
            client.ticker_batch_unsubscribe(product_ids=["BTC-USD"])
            client.close()
