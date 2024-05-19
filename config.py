import os


class Config:
    # DB Settings
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask DEBUG Mode
    DEBUG = os.getenv('DEBUG', False)

    # Coinbase API KEY and SECRET
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')
    # UUID = os.getenv('UUID')

    # EMAIL Settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEBUG = False
    USE_EMAIL = True  # Email Enabled

    #
    # NOTE: Only change these if you know what you're doing!
    #

    # Scheduler (task) job settings
    #   Adjust the timing of each APScheduler job (in seconds)
    #       Just be sure not to make things run too fast
    #       as there are API rate limitations
    ENABLE_BALANCE_SUMMARY = True
    ENABLE_COINBASE_FUTURES_PRODUCTS = True
    ENABLE_TRADING_CONDITIONS = True
    ENABLE_LIST_AND_STORE_FUTURE_ORDERS = True

    # Schedule Timers
    #   Time is measured in seconds (60 seconds = 1 min, etc)
    BALANCE_SUMMARY_TIME = 125
    COINBASE_FUTURES_PRODUCTS_TIME = 600
    TRADING_CONDITIONS_TIME = 40  # This is the main job that opens and checks trading
    FUTURE_ORDERS_TIME = 45  # Get the future orders and store in the DB

    # Threaded Sleep timers
    CANDLES_SLEEP = 60  # How often do we get the candles for our product

    # Dashboard template (html) Timer
    UPDATE_PROFIT_LOSS_TIME = 10000  # in ms 1000 = 1 second

    ###############################
    # Trading and order creation controls
    ###############################
    ENABLE_ORDER_CREATION = True  # Enable order creation (FOR ALL ORDERS!!!)
    ENABLE_MAIN_ORDER_CREATION = False  # Enable the main (first) order
    ENABLE_TAKE_PROFIT_CREATION = True  # Enable take profit order creation
    # ENABLE_TRAILING_TAKE_PROFIT = True  # Enable trailing take profit feature

    # Do we want to Dollar-Cost Average (DCA) ladder orders?
    ENABLE_LADDER_CREATION = True

    # This is the difference percentage in price from the current average price to the
    #   last 15 minute signal price. It's 1 percent by default.
    # Adjust this if you may, the lower the percentage, the safer, but less likely
    #   the trade window will be open. Higher means we're getting further from the last
    #   15 min signal and could increase risk and decrease profit on the trade.
    PERCENTAGE_DIFF_LIMIT = 1

    # First (MAIN) order settings
    #   Typically size should start as 1,
    #       increase if you want to start with larger trades
    CONTRACT_SIZE = 1
    LEVERAGE = 3

    # Take profit settings
    #   At what percentage do we want to place the take profit order?
    TAKE_PROFIT_PERCENTAGE = 0.01  # Take Profit Order = 1%
    # TAKE_PROFIT_PERCENTAGE = 0.005  # Take Profit Order = 0.5%

    INITIAL_TAKE_PROFIT = 0.005  # 0.5%
    TRAILING_THRESHOLD = 0.005  # Start trailing after reaching 0.5%
    TRAILING_OFFSET = 0.002  # 0.2% below the highest or above lowest price

    # NOTE: ONLY SET THIS TO MANUALLY OVERRIDE THE TAKE PROFIT PRICE
    #   I'm still seeing issues with Coinbase's avg_entry_price from the positions
    #   API data, so sometime we may need to override the take profit price
    #   DON'T LEAVE THIS ON AS THE NEXT TRADE WILL BE DIFFERENT
    # TAKE_PROFIT_MANUAL_OVERRIDE_PRICE = "62380"
    TAKE_PROFIT_MANUAL_OVERRIDE_PRICE = False  # Needs to be a price as string

    ###############################
    # Trade conditions
    #   Define scoring thresholds based on normalizing the weighted timeframe
    #       values (in hours) from all the Aurox signals we're collecting to
    #       evaluate high, mid-level and lower timeframes strength values
    ###############################

    # Signal weight as defined by hours and grouping
    # Group 1
    WEEKLY_WEIGHT = 168
    FIVE_DAY_WEIGHT = 120
    THREE_DAY_WEIGHT = 75
    TWO_DAY_WEIGHT = 48
    DAILY_WEIGHT = 24
    TWELVE_HR_WEIGHT = 12
    # Group 2
    EIGHT_HR_WEIGHT = 8
    SIX_HR_WEIGHT = 6
    FOUR_HR_WEIGHT = 4
    THREE_HR_WEIGHT = 3
    TWO_HR_WEIGHT = 2
    ONE_HOUR_WEIGHT = 1
    # Group 3
    THIRTY_MIN_WEIGHT = 0.500
    TWENTY_MIN_WEIGHT = 0.333
    FIFTEEN_MIN_WEIGHT = 0.25
    TEN_MIN_WEIGHT = 0.167
    FIVE_MIN_WEIGHT = 0.083

    # Define scoring thresholds based on normalizing the weighted timeframe
    #   values (in hours) from all the Aurox signals we're collecting to
    #   evaluate high, mid-level and lower timeframes strength values
    STRONG_SIGNAL_WEIGHT = 0.5
    MODERATE_SIGNAL_WEIGHT = 0.2
    NEUTRAL_SIGNAL_WEIGHT = 0

    # DCA ladder trade settings
    # These are the ladder orders to help protect us from a trade going
    #   negative on us – safety trades or DCA (Dollar-Cost-Averaging) if you would.
    #   Adjust them if you wish, just be careful if you spread too far and don't
    #   increase your contract size.
    # NOTE: You'll need a lot of funds for this. With BTC, you may need $5000-$6000
    #  or more in your account for all 10 orders!

    # How many DCA order do we want to use? (you need to have funds to back up all the orders!)
    LADDER_QUANTITY = 15  # 15 Max unless you add more.

    # 0.005 = 0.5%, 0.01 = 1%, 0.1 = 10%, etc.
    # DCA_TRADE_PERCENTAGES = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.06, 0.08, 0.1]
    DCA_TRADE_PERCENTAGES: [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11,
                            0.12, 0.13, 0.14, 0.15]

    # Size of the contracts to purchase per DCA trade
    #   You can set all of these to 1, however your Take Profit will be further
    #   away due to DCA with your ladder orders.
    # NOTE: 2 contacts is double and 3 is triple the amount of a purchase!
    # DCA_CONTRACTS = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2]  # 14 contracts
    DCA_CONTRACTS: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # 15 contracts

    # Contract switching period
    #   This set the days left for the current future contract
    #       to have the bot switch to next months contract before it expires
    GRACE_DAYS = 3  # Increase for a large safety period

    # Logging configurations
    LOG_FILENAME = 'flask_app.log'
    TIME_ROTATION_WHEN = 'H'
    INTERVAL = 4
    BACKUP_COUNT = 180


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
