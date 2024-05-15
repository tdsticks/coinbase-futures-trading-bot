from app import create_app
from config import DevelopmentConfig
import threading

app = create_app(DevelopmentConfig)

# def run_websocket():
#     symbol = "BTC-USD"  # Replace with your trading symbol
#     asyncio.get_event_loop().run_until_complete(subscribe_to_ticker(symbol))
#
# # Start WebSocket in a separate thread
# websocket_thread = threading.Thread(target=run_websocket)
# websocket_thread.start()

if __name__ == '__main__':

    # Note: On PythonAnywhere or other production environments,
    # you might not need to run the app like this.
    app.run(use_reloader=False, debug=app.config['DEBUG'], port=5000)
