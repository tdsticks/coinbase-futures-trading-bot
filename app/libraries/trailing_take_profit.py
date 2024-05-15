import asyncio
import websockets
import json


class TrailingTakeProfit:
    def __init__(self, app):
        self.log = app.custom_log.log
        self.log(True, "D", None, ":Initializing TrailingTakeProfit:")
        self.app = app

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

    @staticmethod
    async def unsubscribe_to_ticker(channel: str, product_id: str):
        print(f"Unsubscribing from {channel}...")
        uri = "wss://advanced-trade-ws.coinbase.com"
        async with websockets.connect(uri) as websocket:
            subscribe_message = {
                "type": "unsubscribe",
                # "product_ids": ["BIT-31MAY24-CDE"],
                "product_ids": [product_id],
                "channel": channel,
            }
            await websocket.send(json.dumps(subscribe_message))

    # WebSocket subscription logic
    async def subscribe_to_ticker(self, channel: str, product_id: str):
        print(f"Subscribing to Ticker {channel}...")

        uri = "wss://advanced-trade-ws.coinbase.com"
        async with websockets.connect(uri) as websocket:
            subscribe_message = {
                "type": "subscribe",
                # "product_ids": ["BIT-31MAY24-CDE"],
                "product_ids": [product_id],
                "channel": channel,
                # "jwt": "your_jwt_here"
            }
            await websocket.send(json.dumps(subscribe_message))
            async for message in websocket:
                self.process_message(json.loads(message))

    def process_message(self, message):
        if 'events' in message:
            for event in message['events']:
                # print("event", event)
                if 'type' in event:
                    if event['type'] == 'update':
                        if 'tickers' in event:
                            # print("event tickers", event['tickers'])
                            price = float(event['tickers'][0]['price'])
                            print(f"Ticker Price: {price}")
                            # self.update_price(price)

    def set_entry_price(self, price):
        self.entry_price = price
        self.highest_price = price * (1 + self.initial_take_profit)

    def update_price(self, price):
        if not self.entry_price:
            return

        # Update highest price if the current price is higher
        if price > self.highest_price:
            self.highest_price = price

        # Check if we should activate trailing take profit
        if price >= self.entry_price * (1 + self.trailing_threshold):
            self.trailing_tp_active = True

        if self.trailing_tp_active:
            trailing_tp_price = self.highest_price * (1 - self.trailing_offset)
            print(f"Trailing Take Profit Price: {trailing_tp_price}")
            # Place or update take profit order logic here

    # def update_trailing_take_profit(self, price):
    #     self.update_price(price)

    def run_websocket(self):
        product_ids = "BTC-USD"
        channel = 'ticker_batch'

        # Unsubscribe first
        # asyncio.run(self.unsubscribe_to_ticker(channel, product_ids))

        # Then subscribe
        # asyncio.run(self.subscribe_to_ticker(channel, product_ids))
