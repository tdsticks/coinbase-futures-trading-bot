from coinbase.websocket import (WSClient, WSClientConnectionClosedException,
                                WSClientException)
from datetime import datetime
import time
import pytz
import json


class ListOrdersWebsocket:
    def __init__(self, app):
        """
        Initialize the ListOrdersWebsocket class with configuration settings.

        :param app: The application instance containing configuration and trade manager.
        """
        self.log = app.custom_log.log
        self.log(True, "D", None, ":Initializing ListOrdersWebsocket:")
        self.app = app
        self.tm = app.trade_manager
        self.cbapi = app.cb_adv_api

    @staticmethod
    def process_message(msg):
        json_msg = json.loads(msg)
        if 'events' in json_msg:
            for event in json_msg['events']:
                print("event:", event)
                # if 'orders' in event:
                    # for order in event['orders']:
                    #     print(" order:", order)

    def run_websocket(self):
        print(":run_websocket:")

        # product_id = "BTC-USD"
        product_id = "BIT-31MAY24-CDE"

        while True:
            print("while True")

            # client = WSClient(on_message=self.process_message, timeout=5, retry=True, max_size=65536)
            client = WSClient(api_key=self.app.config['API_KEY'],
                              api_secret=self.app.config['API_SECRET'],
                              on_message=self.process_message,
                              timeout=5, retry=True, verbose=True,
                              max_size=65536)
            print(" client:", client)

            # Check if the market is open or not
            now = datetime.now(pytz.utc)

            if self.tm.is_trading_time(now):
                try:
                    print("Opening client...")
                    client.open()
                    print(" client open:")
                    client.subscribe(product_ids=[product_id], channels=["user", "heartbeats"])
                    # client.subscribe(product_ids=[product_id], channels=["user"])
                    # client.user(product_ids=[product_id])
                    # print(" client user:")
                    client.run_forever_with_exception_check()
                    print(" client run_forever_with_exception_check:")
                    # client.sleep_with_exception_check(sleep=5)
                except WSClientConnectionClosedException as e:
                    print(" Web Socket: Connection closed! Retry attempts exhausted.", e)
                except WSClientException as e:
                    print(" Web Socket: Error encountered!", e)
                except Exception as e:
                    print(" Unexpected error:", e)
                finally:
                    try:
                        # client.user_unsubscribe(product_ids=[product_id])
                        client.unsubscribe(product_ids=[product_id], channels=["user", "heartbeats"])
                        # client.unsubscribe(product_ids=[product_id], channels=["user"])
                        print(" client user_unsubscribe:")
                    except Exception as e:
                        print(" Error during unsubscribe:", e)
                    try:
                        client.close()
                        print(" client close:")
                    except Exception as e:
                        print(" Error during close:", e)

                seconds = 5
                print(f"sleep for {seconds}")
                time.sleep(seconds)  # Sleep for 5 seconds
