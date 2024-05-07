import configparser
import configparser
import os
from datetime import datetime, time

import logs
import pytz
from dotenv import load_dotenv

from coinbase_api import CoinbaseAdvAPI
from db import db, db_errors, joinedload
from models.futures import (FuturePosition)
from models.signals import AuroxSignal, FuturePriceAtSignal
from signals_processor import SignalProcessor

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
UUID = os.getenv('UUID')

config = configparser.ConfigParser()
config.read('bot_config.ini')
config.sections()


class TradeManager:

    def __init__(self, flask_app):
        # print(":Initializing TradeManager:")
        self.flask_app = flask_app
        self.log = logs.Log(flask_app)  # Send to Log or Console or both
        self.cb_adv_api = CoinbaseAdvAPI(flask_app)

        self.signal_processor = SignalProcessor(flask_app, self.cb_adv_api)

        self.log.log(True, "D", None, ":Initializing TradeManager:")

    def get_latest_weekly_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_weekly_signal:")

        with self.flask_app.app_context():
            # Query the latest weekly signal including related future price data
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '1 Week') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_five_day_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_five_day_signal:")

        with self.flask_app.app_context():

            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '5 Days') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_three_day_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_three_day_signal:")

        with self.flask_app.app_context():

            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '3 Days') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_two_day_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_two_day_signal:")

        with self.flask_app.app_context():

            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '2 Days') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_daily_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_daily_signal:")

        with self.flask_app.app_context():

            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '1 Day') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_12_hour_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_12_hourly_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '12 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_8_hour_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_8_hourly_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '8 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_6_hour_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_6_hour_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '6 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_4_hour_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_4_hourly_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '4 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_3_hour_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_3_hour_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '3 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_2_hour_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_2_hour_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '2 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_1_hour_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_1_hour_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '1 Hour') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_30_minute_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_30_minute_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '30 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_20_minute_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_20_minute_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '20 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_15_minute_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_15_minute_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '15 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_10_minute_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_10_minute_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '10 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_5_minute_signal(self):
        # self.log.log(True, "D", None,
        #                         ":get_latest_5_minute_signal:")

        with self.flask_app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '5 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

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

    def check_for_contract_expires(self):
        self.log.log(True, "D", None,
                     ":NEW_check_for_contract_expires:")

        # NOTE: Futures markets are open for trading from Sunday 6 PM to
        #  Friday 5 PM ET (excluding observed holidays),
        #  with a 1-hour break each day from 5 PM – 6 PM ET

        # Get the futures contract from Coinbase API
        list_future_products = self.cb_adv_api.list_products("FUTURE")
        self.cb_adv_api.store_btc_futures_products(list_future_products)

        # Get the current month's contract
        current_future_product = self.cb_adv_api.get_relevant_future_from_db()
        self.log.log(True, "I",
                     "   Current Future Product",
                     current_future_product.product_id)

        current_month = self.cb_adv_api.get_current_short_month_uppercase()
        self.log.log(True, "I",
                     "   Current Month", current_month)

        next_month = self.cb_adv_api.get_next_short_month_uppercase()
        self.log.log(True, "I",
                     "   Next Month", next_month)

        if current_future_product:
            contract_expiry = current_future_product.contract_expiry.replace(tzinfo=pytz.utc)
            now = datetime.now(pytz.utc)
            time_diff = contract_expiry - now

            days, seconds = time_diff.days, time_diff.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60

            # contract_grace_days = 3
            contract_grace_days = int(config['end.of.contract.switch.period']['grace_days'])

            # FOR TESTING ONLY
            # days = 10

            # Check if the contract has expired
            if time_diff.total_seconds() <= 0:
                self.log.log(True, "W", None, "-----------------------------------")
                self.log.log(True, "W", None, ">>> Contract has expired!")
                self.log.log(True, "W", None, ">>> Close out any positions!!!")
                self.log.log(True, "W", None, "-----------------------------------")
                self.log.log(True, "I", None, "Switching to next month's contract.")

                # Identify and switch to the next contract
                next_month_product, next_month = self.find_next_month_contract(list_future_products, next_month)

                if next_month_product:
                    self.log.log(True, "I",
                                 "   > next_month_product.product_id",
                                 next_month_product['product_id'])
                    return next_month_product['product_id'], next_month
            elif days <= contract_grace_days:
                # If the contract expires in less than or equal to 3 days
                contract_msg = (f"  > Contract {current_future_product.product_id} is close to expiring"
                                f" in {days} days, {hours} hours, and {minutes} minutes.")
                self.log.log(True, "I", None, contract_msg)
                self.log.log(True, "I", None, "  > Switching to next month's contract.")

                # Identify and switch to the next contract
                next_month_product, next_month = self.find_next_month_contract(list_future_products, next_month)

                if next_month_product:
                    self.log.log(True, "I",
                                 "   > next_month_product.product_id",
                                 next_month_product['product_id'])
                    return next_month_product['product_id'], next_month
            else:
                contract_msg = (f"  Current contract {current_future_product.product_id} is safe to trade. "
                                f"It expires in {days} days, {hours} hours, and {minutes} minutes.")
                self.log.log(True, "I", None, contract_msg)
                return None, None
        else:
            self.log.log(True, "I", None, "  !!! No current future product found")
            return None, None

    @staticmethod
    def find_next_month_contract(future_products, next_month):
        """Identify the next month's future contract based on the current product."""
        # print("future_products:")
        next_contact = None
        for fp in future_products['products']:
            f_products_contract_root_unit = fp['future_product_details']['contract_root_unit']

            # Limit to only BTC contacts
            if f_products_contract_root_unit == "BTC":
                display_name = fp['display_name']

                # Filter down to the next month futures contract
                if next_month in display_name:
                    next_contact = fp
        return next_contact, next_month

    def ladder_orders(self, side: str, product_id: str, bid_price, ask_price,
                      quantity: int = 5, manual_price: str = ''):
        self.log.log(True, "D", None, "||||||||||||||||||||||||")
        self.log.log(True, "D", None, ":ladder_orders:")

        # Prevent more than 10
        if quantity > 10:
            quantity = 10

        # NOTE: This is part of our strategy in placing DCA limit orders if the trade goes against us,
        #   even though both the Weekly and Daily signals are in our favor. This not only helps
        #   cover the volatility of the market and all the effects it, it also can help be more profitable
        #   if we're carefully. We also need to adjust the closing Long or Short order we'll place to
        #   help with risk management and taking profit.

        size = "1"
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
        self.log.log(True, "I", "cur_future_price", cur_future_price)

        # dca_note_list = ['DCA1', 'DCA2', 'DCA3', 'DCA4', 'DCA5']
        dca_note_list = ["DCA" + str(x) for x in range(1, quantity + 1)]
        self.log.log(True, "I", "    dca_note_list",
                     dca_note_list)

        # Generate the DCA percentages list dynamically based on 'quantity'
        # dca_per_offset_list = [0.01, 0.02, 0.03, 0.04, 0.05]
        dca_per_offset_list = [
            float(config['dca.ladder.trade_percentages'][f'dca_trade_{i + 1}_per'])
            for i in range(quantity)
        ]
        self.log.log(True, "I", "    dca_per_offset_list",
                     dca_per_offset_list)

        dca_contract_size_list = [
            str(config['dca.ladder.trade_percentages'][f'dca_trade_{i + 1}_contracts'])
            for i in range(quantity)
        ]
        self.log.log(True, "I", "    dca_contract_size_list",
                     dca_contract_size_list)

        def create_dca_orders():
            for i, note in enumerate(dca_note_list):
                if i <= quantity - 1:
                    dcg_limit_price = ""
                    dca_trade_per_offset = int(float(cur_future_price) * dca_per_offset_list[i])
                    self.log.log(True, "D",
                                 "   DCA Trade Per Offset",
                                 dca_trade_per_offset)

                    # Calculate the DCA orders (Long or Short)
                    if side == "BUY":  # BUY / LONG
                        dcg_limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                            int(cur_future_price) - dca_trade_per_offset)
                        self.log.log(True, "D",
                                     "   > Buy Long dcg_limit_price: $",
                                     dcg_limit_price)

                    elif side == "SELL":  # SELL / SHORT
                        dcg_limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                            int(cur_future_price) + dca_trade_per_offset)
                        self.log.log(True, "D",
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
                    self.log.log(True, "D", "DCA order_created!", dca_order_created)

        create_dca_orders()

    def is_trading_time(self, current_time):
        self.log.log(True, "I", None, "---> Checking for open market...")
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
            self.log.log(True, "I", None, " >>> Futures market is OPEN! <<<")
            return True
        elif is_sunday_after_6pm or is_friday_before_5pm:
            self.log.log(True, "I", None, " >>> Futures market is OPEN! <<<")
            return True
        self.log.log(True, "W", None, " >>> Futures market is CLOSED. <<<")
        return False

    def check_trading_conditions(self):
        self.log.log(True, "D", None, "--------------------------")
        self.log.log(True, "D", None, ":check_trading_conditions:")

        # Update any cancelled orders in the database (in case we close things manually, etc.)
        self.cb_adv_api.update_cancelled_orders()

        #######################
        # Do we have an existing trades?
        #######################

        next_months_product_id, next_month = self.check_for_contract_expires()
        if next_months_product_id:
            self.log.log(True, "I", "Next Months Product ID", next_months_product_id)
            self.log.log(True, "I", "Next Month", next_month)

        # Get Current Positions from API, we just need to acknowledge this position exists
        #  and get the position side
        future_positions = self.cb_adv_api.list_future_positions()
        # print("Future Positions:")
        # pp(future_positions)

        weekly_signals = self.get_latest_weekly_signal()
        daily_signals = self.get_latest_daily_signal()
        twelve_hour_signals = self.get_latest_12_hour_signal()
        eight_hour_signals = self.get_latest_8_hour_signal()
        four_hour_signals = self.get_latest_4_hour_signal()
        one_hour_signals = self.get_latest_1_hour_signal()
        fifteen_min_signals = self.get_latest_15_minute_signal()

        signal_calc_trade_direction, signal_score, ts_obj = self.calc_all_signals_score_for_direction(weekly_signals,
                                                                                                      daily_signals,
                                                                                                      twelve_hour_signals,
                                                                                                      eight_hour_signals,
                                                                                                      four_hour_signals,
                                                                                                      one_hour_signals,
                                                                                                      fifteen_min_signals)

        trade_worthy = self.signal_processor.run()
        self.log.log(True, "I", " >>> Trade Worthy?", trade_worthy)

        # weekly_ts_formatted = ts_obj['weekly_ts_fmt']
        # daily_ts_formatted = ts_obj['daily_ts_fmt']
        # twelve_hour_ts_formatted = ts_obj['twelve_hr_ts_fmt']
        # eight_hour_ts_formatted = ts_obj['eight_hr_ts_fmt']
        # four_hour_ts_formatted = ts_obj['four_hr_ts_fmt']
        # one_hour_ts_formatted = ts_obj['one_hr_ts_fmt']
        # fifteen_min_ts_formatted = ts_obj['fifteen_min_ts_fmt']

        # Make sure we have a future position
        if len(future_positions['positions']) > 0:
            self.log.log(True, "I", None, "  >>> We have an ACTIVE position(s) <<<")

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
            # self.log.log(True, "I", "Cur Position Order", cur_position_order)

            # Clear and store the active future position
            self.cb_adv_api.store_future_positions(future_positions)

            # Make sure we have a FILLED order from our position
            if cur_position_order:
                # Get the position from the database
                # NOTE: We should only get one if we're only trading one future (BTC)
                with (self.flask_app.app_context()):  # Push an application context
                    try:
                        # NOTE: position doesn't have the all most accurate data we need, so
                        #  we uses the order to help supplement what we need
                        positions = FuturePosition.query.all()
                        # self.log.log(True, "I", "positions", positions)
                        for position in positions:
                            self.tracking_current_position_profit_loss(position, cur_position_order, next_month)
                            self.track_take_profit_order(position, cur_position_order)

                    except Exception as e:
                        self.log.log(True, "E", "Unexpected error:", msg1=e)
            else:
                self.log.log(True, "W",
                             "    >>> NO Current Position Order Found", cur_position_order)
        else:
            self.log.log(True, "I", None, " >>> No Open Position")
            self.log.log(True, "I", None,
                         " >>> Check if its a good market to place a trade")

            # NOTE: Check to cancel any OPEN orders

            future_contract = self.cb_adv_api.get_relevant_future_from_db()
            remaining_open_orders = self.cb_adv_api.list_orders(product_id=future_contract.product_id,
                                                                order_status="OPEN")
            if 'orders' in remaining_open_orders:
                self.log.log(True, "D",
                             "remaining_open_orders count",
                             len(remaining_open_orders['orders']))
                order_ids = []
                client_order_ids = []
                for order in remaining_open_orders['orders']:
                    order_ids.append(order['order_id'])
                    client_order_ids.append(order['client_order_id'])

                # Pass the order_id as a list. Can place multiple order ids if necessary,
                #   but not in this case
                cancelled_order = self.cb_adv_api.cancel_order(order_ids=order_ids)
                self.log.log(True, "I", "    > cancelled_order", cancelled_order)

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
                    self.log.log(True, "I", "    > updated_cancelled_order", updated_cancelled_order)

                # Now, update an other Future Order records setting bot_active = 0
                self.cb_adv_api.update_bot_active_orders()

            #
            # If our overall position trade direction isn't neutral, then proceed
            #
            if signal_calc_trade_direction != "neutral":
                self.log.log(True, "I", None,
                             "-----------------------------------")
                self.log.log(True, "I", None,
                             " >>> Signals are strong either bullish or bearish, "
                             "see if we should place a trade")

                # NOTE: Next, let's look at the fifteen minute and how close to the
                #  last signal and price of when we should place a limit order.
                #  How are in price are we away from the last signal?
                #  What is a good price threshold?
                #  Is 15 Minute signal side the same as the signal_calc_trade_direction side?

                fifteen_min_trade_signal = fifteen_min_signals.signal

                # NOTE: Does the 15 Min match the overall signal trade direction of the Aurox signals?

                if fifteen_min_trade_signal == signal_calc_trade_direction:
                    self.log.log(True, "I", None,
                                 "   >>> YES, the 15 Min matches the overall trade direction")

                    # Check to see if next months product id is populated
                    if next_months_product_id is None:
                        # Get this months current product
                        relevant_future_product = self.cb_adv_api.get_relevant_future_from_db()
                        self.log.log(True, "I", "    Relevant Future Product",
                                     relevant_future_product.product_id)
                        product_id = relevant_future_product.product_id
                    else:
                        product_id = next_months_product_id

                    bid_price, ask_price, avg_price = self.cb_adv_api.get_current_average_price(product_id=product_id)
                    self.log.log(True, "I",
                                 "   bid ask avg_price", avg_price)

                    limit_price = self.cb_adv_api.adjust_price_to_nearest_increment(avg_price)
                    self.log.log(True, "I",
                                 "   Current Limit Price", limit_price)

                    fifteen_min_future_avg_price = 0
                    for future_price in fifteen_min_signals.future_prices:
                        future_bid_price = future_price.future_bid_price
                        future_ask_price = future_price.future_ask_price
                        fifteen_min_future_avg_price = round((future_bid_price + future_ask_price) / 2)
                    self.log.log(True, "I",
                                 "   Fifteen Min Future Avg Price",
                                 fifteen_min_future_avg_price)

                    # Just setting a high default number to check again
                    percentage_diff = 10

                    # The signal price should be lower than current price (price rising)
                    check_signal_and_current_price_diff = 0
                    if signal_calc_trade_direction == 'long':
                        check_signal_and_current_price_diff = int(limit_price) - int(fifteen_min_future_avg_price)
                        percentage_diff = round((check_signal_and_current_price_diff
                                                 / int(fifteen_min_future_avg_price)) * 100, 2)

                    elif signal_calc_trade_direction == 'short':
                        check_signal_and_current_price_diff = int(fifteen_min_future_avg_price) - int(limit_price)
                        percentage_diff = round((check_signal_and_current_price_diff
                                                 / int(fifteen_min_future_avg_price)) * 100, 2)

                    # NOTE: Make sure the price difference from the 15 Min signal and current price
                    #   isn't too far off or beyond 1%, so we try to be safe and get more profit

                    # Set a limit value is here (1 = 1%)
                    # percentage_diff_limit = 1
                    percentage_diff_limit = float(config['trade.conditions']['percentage_diff_limit'])
                    per_diff_msg = (f"   >>> Checking! Signal Direction "
                                    f"{signal_calc_trade_direction} "
                                    f" Per Diff {percentage_diff}% < {percentage_diff_limit}% Limit")
                    self.log.log(True, "I", None, per_diff_msg)

                    if percentage_diff < percentage_diff_limit:
                        good_per_diff_msg = (f"   >>> Proceeding! current price diff of "
                                             f"{check_signal_and_current_price_diff} "
                                             f"which is {percentage_diff}%")
                        self.log.log(True, "W", None, good_per_diff_msg)

                        trade_side = ""

                        # LONG = BUY
                        # SHORT = SELL
                        if signal_calc_trade_direction == "long":
                            trade_side = "BUY"
                        elif signal_calc_trade_direction == "short":
                            trade_side = "SELL"

                        size = "1"
                        leverage = "3"
                        order_type = "limit_limit_gtc"
                        order_msg = (f"    >>> Trade side:{trade_side} Order type:{order_type} "
                                     f"Limit Price:{limit_price} Size:{size} Leverage:{leverage}")
                        self.log.log(True, "I", None, order_msg)

                        # Create a new MAIN order
                        order_created = self.cb_adv_api.create_order(side=trade_side,
                                                                     product_id=product_id,
                                                                     size=size,
                                                                     limit_price=limit_price,
                                                                     leverage=leverage,
                                                                     order_type=order_type,
                                                                     bot_note="MAIN")
                        print("MAIN order_created:", order_created)

                        # TODO: Need to see if the MAIN order is filled first before placing ladder orders

                        # How many ladder orders? (10 max)
                        # ladder_order_qty = 8
                        ladder_order_qty = int(config['dca.ladder.trade_percentages']['ladder_quantity'])

                        # Create the DCA ladder orders
                        self.ladder_orders(quantity=ladder_order_qty,
                                           side=trade_side,
                                           product_id=product_id,
                                           bid_price=bid_price,
                                           ask_price=ask_price)
                    else:
                        bad_per_diff_msg = (f"   >>> Holding off, current price diff of "
                                            f"{check_signal_and_current_price_diff} "
                                            f"which is {percentage_diff}%")
                        self.log.log(True, "W", None, bad_per_diff_msg)
                else:
                    self.log.log(True, "W", None,
                                 "   >>> NO, the 15 Min does not match the overall trade direction")
                    fifteen_min_pos_trade_dir_msg = (f"     >>> 15 Min Signal: {fifteen_min_trade_signal} "
                                                     f"!= Signal Trade Direction: {signal_calc_trade_direction}")
                    self.log.log(True, "W", None,
                                 fifteen_min_pos_trade_dir_msg)
            else:
                self.log.log(True, "W", None,
                             "Signal score is neutral, let's wait... Score:", signal_score)

                # weekly_msg = f"Weekly Signal: {weekly_signals.signal} | Date: {weekly_ts_formatted}"
                # daily_msg = f"Daily Signal: {daily_signals.signal} | Date: {daily_ts_formatted}"
                # twelve_msg = f"12 Hr Signal: {twelve_hour_signals.signal} | Date: {twelve_hour_ts_formatted}"
                # eight_msg = f"8 Hr Signal: {eight_hour_signals.signal} | Date: {eight_hour_ts_formatted}"
                # four_msg = f"4 Hr Signal: {four_hour_signals.signal} | Date: {four_hour_ts_formatted}"
                # hour_msg = f"1 Hr Signal: {one_hour_signals.signal} | Date: {one_hour_ts_formatted}"
                # fifteen_msg = f"15 Min Signal: {fifteen_min_signals.signal} | Date: {fifteen_min_ts_formatted}"
                # self.log.log(True, "W", None, weekly_msg)
                # self.log.log(True, "W", None, daily_msg)
                # self.log.log(True, "W", None, twelve_msg)
                # self.log.log(True, "W", None, eight_msg)
                # self.log.log(True, "W", None, four_msg)
                # self.log.log(True, "W", None, hour_msg)
                # self.log.log(True, "W", None, fifteen_msg)

    def tracking_current_position_profit_loss(self, position, order, next_month):
        self.log.log(True, "D", None, "---------------------------------------")
        self.log.log(True, "D", None, ":tracking_current_position_profit_loss:")

        # print(" position:", position)
        # print(" order:", order)

        # Only run if we have ongoing positions
        if position:
            product_id = position.product_id
            self.log.log(True, "I", "  position.product_id:", product_id)

            side = position.side
            self.log.log(True, "I", "  position.side:", side)

            # print("next_month:", next_month)
            # self.log.log(True, "I", "  next_month:", next_month)

            relevant_future_product = self.cb_adv_api.get_relevant_future_from_db(month_override=next_month)
            product_contract_size = relevant_future_product.contract_size
            # self.log.log(True, "I", "  product_contract_size:", product_contract_size)

            if order is not None:
                # print("  Profit / Loss: order", order)
                # print("  Profit / Loss: order.average_filled_price", order.average_filled_price)

                dca_side = ''

                # If we're LONG, then we need to place a profitable BUY order
                if side == "LONG":  # BUY / LONG
                    dca_side = "BUY"
                # If we're SHORT, then we need to place a profitable SELL order
                elif side == "SHORT":  # SELL / SHORT
                    dca_side = "SELL"

                dca_avg_filled_price, dca_avg_filled_price_2, dca_count = self.cb_adv_api.get_dca_filled_orders_from_db(
                    dca_side=dca_side)
                self.log.log(True, "I", "    dca_count", dca_count)
                self.log.log(True, "I", "    dca_avg_filled_price", dca_avg_filled_price)

                # Get the average filled price from the Future Order
                avg_filled_price = round((int(order.average_filled_price) + dca_avg_filled_price) / dca_count)
                self.log.log(True, "I", "    avg_filled_price", avg_filled_price)

                # Get the current price from the Future Position
                current_price = round(int(position.current_price), 2)
                # self.log.log(True, "I", "    current_price", current_price)

                number_of_contracts = position.number_of_contracts
                # self.log.log(True, "I", "    number_of_contracts", number_of_contracts)

                # Calculate total cost and current value per contract
                total_initial_cost = avg_filled_price * number_of_contracts * product_contract_size
                total_current_value = current_price * number_of_contracts * product_contract_size
                # self.log.log(True, "I", "  total_initial_cost", total_initial_cost)
                # self.log.log(True, "I", "  total_current_value", total_current_value)

                # Calculate profit or loss for all contracts
                # NOTE: We need to factor in what side of the market: long or short
                calc_profit_or_loss = 0
                if position.side.lower() == 'long':  # Assuming 'buy' denotes a long position
                    calc_profit_or_loss = round(total_current_value - total_initial_cost, 4)
                elif position.side.lower() == 'short':  # Assuming 'sell' denotes a short position
                    calc_profit_or_loss = round(total_initial_cost - total_current_value, 4)
                # self.log.log(True, "I", "  calc_profit_or_loss", calc_profit_or_loss)

                if total_initial_cost != 0:  # Prevent division by zero
                    calc_percentage = round((calc_profit_or_loss / total_initial_cost) * 100, 4)
                else:
                    calc_percentage = 0
                self.log.log(True, "I", "  calc_percentage:", calc_percentage)

                # print("Contract Expires on", future_position['position']['expiration_time'])
                # print(" Contract Expires on", position.expiration_time)

                self.log.log(True, "I", None, ">>>>>>>>>>>>>>>>>>>>>>>>>>>")
                self.log.log(True, "I", None, ">>> Profit / Loss <<<")
                self.log.log(True, "I", "Product Id", product_id)
                self.log.log(True, "I", "Position Side", side)
                self.log.log(True, "I", "Avg Entry Price $", avg_filled_price)
                self.log.log(True, "I", "Current Price $", current_price)
                self.log.log(True, "I", "# of Contracts", number_of_contracts)
                if calc_percentage >= 2:
                    self.log.log(True, "I", "Take profit at 2% or higher %", calc_percentage)
                    self.log.log(True, "I", "Good Profit $", calc_profit_or_loss)
                elif 2 > calc_percentage > 0.5:
                    self.log.log(True, "I", "Not ready to take profit %", calc_percentage)
                    self.log.log(True, "I", "Ok Profit $", calc_profit_or_loss)
                elif 0.5 >= calc_percentage >= 0:
                    self.log.log(True, "I", "Neutral %", calc_percentage)
                    self.log.log(True, "I", "Not enough profit $", calc_profit_or_loss)
                elif calc_percentage < 0:
                    self.log.log(True, "I", "Trade negative %", calc_percentage)
                    self.log.log(True, "I", "No profit, loss of $", calc_profit_or_loss)
                self.log.log(True, "I", None, ">>>>>>>>>>>>>>>>>>>>>>>>>>>")
            else:
                self.log.log(True, "W", "No open order", order)
        else:
            self.log.log(True, "W", "No open positions", position)

    def track_take_profit_order(self, position, order):
        self.log.log(True, "D", None, "-------------------------")
        self.log.log(True, "D", None, ":track_take_profit_order:")

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
            # self.log.log(True, "I", "position.side", side)

            # If we're LONG, then we need to place a profitable BUY order
            if side == "LONG":  # BUY / LONG
                take_profit_side = "SELL"
                dca_side = "BUY"
            # If we're SHORT, then we need to place a profitable SELL order
            elif side == "SHORT":  # SELL / SHORT
                take_profit_side = "BUY"
                dca_side = "SELL"
            self.log.log(True, "I", "    take_profit_side", take_profit_side)

            # TODO: Need to test if the average price changes based on more positions (contracts)
            #   This may need to be adjusted back to using the Position record vs the Order record
            #   if more contracts are bought

            # Now, get the ALL Future Orders from the DB so we have more accurate data
            take_profit_order = self.cb_adv_api.get_current_take_profit_order_from_db(
                order_status="OPEN", side=take_profit_side, bot_note="TAKE_PROFIT", get_all_orders=True)
            # self.log.log(True, "I", "  > take_profit_order exists 1", take_profit_order)

            # BUG: Need to fix duplicate Take Profit orders, creating work around for now

            # NOTE: If we have more than one Take Profit, keep one and cancel the rest

            if len(take_profit_order) > 1:
                # Loop through all of the take profit orders, except one (we keep that)
                for tp in range(0, len(take_profit_order) - 1):
                    loop_tp_order = take_profit_order[tp]
                    loop_tp_order_id = loop_tp_order.order_id
                    loop_tp_client_order_id = loop_tp_order.client_order_id
                    # self.log.log(True, "I", "    >>> tp", tp, loop_tp_order)
                    # self.log.log(True, "I", "    tp.order_id", loop_tp_order_id)

                    # Pass the order_id as a list. Can place multiple order ids if necessary, but not in this case
                    cancelled_order = self.cb_adv_api.cancel_order(order_ids=[loop_tp_order_id])
                    self.log.log(True, "I",
                                 "    Cancelled Extra Order", cancelled_order)
                    field_values = {
                        "bot_active": 0,
                        "order_status": "CANCELLED"
                    }
                    # Update order so we don't the system doesn't try to use it for future orders
                    updated_cancelled_order = self.cb_adv_api.update_order_fields(
                        client_order_id=loop_tp_client_order_id,
                        field_values=field_values)
                    self.log.log(True, "I",
                                 "    Updated Extra Cancelled Order", updated_cancelled_order)

            # Run this again to get only one take profit order
            take_profit_order = self.cb_adv_api.get_current_take_profit_order_from_db(
                order_status="OPEN", side=take_profit_side, bot_note="TAKE_PROFIT", get_all_orders=False)
            # self.log.log(True, "I",
            #                         "   > take_profit_order exists 1.5", take_profit_order)

            # Now see if we have a take profit order already open
            if take_profit_order is not None:
                # self.log.log(True, "I", "  > take_profit_order exists 2", take_profit_order)
                existing_take_profit_order = True
            else:
                existing_take_profit_order = False
                self.log.log(True, "W", "    No take_profit_order", take_profit_order)

            # NOTE: Find all the FILLED DCA orders to get the average price

            number_of_contracts = position.number_of_contracts
            # self.log.log(True, "I", "    Number Of Contracts", number_of_contracts)

            dca_avg_filled_price, dca_avg_filled_price_2, dca_count = self.cb_adv_api.get_dca_filled_orders_from_db(
                dca_side=dca_side)
            self.log.log(True, "I", "    DCA Count", dca_count)
            # self.log.log(True, "I", "    DCA Avg Filled Price", dca_avg_filled_price)
            # self.log.log(True, "I", "    DCA Avg dca_avg_filled_price_2 Price", dca_avg_filled_price_2)

            main_order_avg_filled_price = int(order.average_filled_price)
            # self.log.log(True, "I", "    MAIN Order Avg Filled Price", main_order_avg_filled_price)

            avg_filled_price = round((main_order_avg_filled_price + dca_avg_filled_price) / dca_count)
            # self.log.log(True, "I", "    ALL ORDERS Avg Filled Price", avg_filled_price)

            avg_filled_price_2 = round((main_order_avg_filled_price + dca_avg_filled_price_2) / number_of_contracts)
            # self.log.log(True, "I", "    ALL ORDERS Avg Filled Price 2", avg_filled_price_2)

            # take_profit_percentage = 0.01
            take_profit_percentage = float(config['take.profit.order']['take_profit_percentage'])
            tp_per_msg = f" Take Profit Percentage: {take_profit_percentage * 100}%"
            self.log.log(True, "I", None, tp_per_msg)

            # Calculate the take profit price (Long or Short)
            take_profit_offset_price = int(float(avg_filled_price) * take_profit_percentage)
            # self.log.log(True, "I", "     Take Profit Offset Price", take_profit_offset_price)

            # Calculate the take profit price (Long or Short)
            take_profit_offset_price_2 = int(float(avg_filled_price_2) * take_profit_percentage)
            # self.log.log(True, "I", "     Take Profit Offset Price 2", take_profit_offset_price_2)

            take_profit_price = ""

            # If we're LONG, then we need to place a profitable SELL order
            if side == "LONG":  # BUY / LONG
                take_profit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                    int(avg_filled_price) + take_profit_offset_price_2)
                self.log.log(True, "I", "    > SELL Short take_profit_price: $",
                             take_profit_price)

            # If we're SHORT, then we need to place a profitable BUY order
            elif side == "SHORT":  # SELL / SHORT
                take_profit_price = self.cb_adv_api.adjust_price_to_nearest_increment(
                    int(avg_filled_price) - take_profit_offset_price_2)
                self.log.log(True, "I", "    > BUY Long take_profit_price: $",
                             take_profit_price)

            order_type = "limit_limit_gtc"

            # If we don't have an existing take profit order, create one
            if existing_take_profit_order is False:
                self.log.log(True, "I", None,
                             "  >>> Create new take_profit_order")

                # Take Profit Order
                order_created = self.cb_adv_api.create_order(side=take_profit_side,
                                                             product_id=product_id,
                                                             size=number_of_contracts,
                                                             limit_price=take_profit_price,
                                                             leverage='',
                                                             order_type=order_type,
                                                             bot_note="TAKE_PROFIT")
                self.log.log(True, "I", None,
                             "   >>> TAKE_PROFIT order_created!")
                self.log.log(True, "I", "    >>> Order:", order_created)

            else:  # Otherwise, let's edit and update the order based on the market and position(s)
                self.log.log(True, "I", None,
                             "  >>> Check Existing Take Profit Order...")
                # pp(take_profit_order)
                tp_order_id = take_profit_order.order_id
                tp_client_order_id = take_profit_order.client_order_id
                # self.log.log(True, "I", "tp_order_id", tp_order_id)
                # self.log.log(True, "I", "tp_client_order_id", tp_client_order_id)

                # For limit GTC orders only
                size = take_profit_order.base_size
                # self.log.log(True, "I", "take_profit_order size", size)

                # See if we need to update the size based on the existing number of
                # contracts in the position
                if int(number_of_contracts) > int(size):
                    new_size = number_of_contracts
                    self.log.log(True, "W",
                                 "    take_profit_order new_size", new_size)
                else:
                    new_size = size
                # print(" take_profit_order new_size:", new_size)

                # FOR TESTING
                # take_profit_price = "62230"
                # new_size = str(2)

                # REVIEW: Since the edit_order API call isn't working (and I've reached out to support),
                #  I'll just cancel the order and place a new one. This shouldn't run that often for
                #  the DCA take profit orders, however, I do want to solve this for trailing take profit

                # NOTE: In order to update the order, we need to get it first, then check the values against
                #   if we have an updates contact "size" or "price" based on the DCA orders, if not
                #   then we can skip this

                base_size = take_profit_order.base_size
                limit_price = take_profit_order.limit_price

                check_price_size_msg = f" {int(limit_price)} != {int(take_profit_price)} or {base_size} != {new_size}"
                self.log.log(True, "I",
                             "    Check Price Size Msg", check_price_size_msg)

                # Check to see if either price or size don't match
                if (int(limit_price) != int(take_profit_price)) is True or (int(base_size) != int(new_size)) is True:
                    self.log.log(True, "I", None,
                                 "   >>> Either the prices are off or the contract sizes are off")
                    self.log.log(True, "I", None,
                                 "   >>> Cancel the existing take profit or and place a new one!")

                    # NOTE: Cancel the existing take profit order, update it's db record,
                    #  then place a new take profit with the the updated price and size

                    if len(tp_order_id) > 0:
                        # Pass the order_id as a list. Can place multiple order ids if necessary, but not in this case
                        cancelled_order = self.cb_adv_api.cancel_order(order_ids=[tp_order_id])
                        self.log.log(True, "I",
                                     "    cancelled_order", cancelled_order)

                        field_values = {
                            "bot_active": 0,
                            "order_status": "CANCELLED"
                        }
                        # Update order so we don't the system doesn't try to use it for future orders
                        updated_cancelled_order = self.cb_adv_api.update_order_fields(
                            client_order_id=tp_client_order_id,
                            field_values=field_values)
                        self.log.log(True, "I",
                                     "    updated_cancelled_order", updated_cancelled_order)

                    self.log.log(True, "I", None,
                                 "   >>> Creating new order with updated PRICE or SIZE settings!")
                    # Take Profit Order
                    take_profit_order_created = self.cb_adv_api.create_order(side=take_profit_side,
                                                                             product_id=product_id,
                                                                             size=new_size,
                                                                             limit_price=take_profit_price,
                                                                             leverage='',
                                                                             order_type=order_type,
                                                                             bot_note="TAKE_PROFIT")
                    self.log.log(True, "I",
                                 "   >>> take_profit_order_created", take_profit_order_created)
                else:
                    self.log.log(True, "I", None,
                                 "   ...No changes with take profit order in PRICE or SIZE...")
        else:
            self.log.log(True, "W",
                         "    No open positions | orders", position, order)


if __name__ == "__main__":
    print(__name__)

    ############################
    # def on_message(msg):
    #     print(msg)
    # ws_client = WSClient(api_key=API_KEY, api_secret=API_SECRET, on_message=on_message, verbose=True)
    # ws_client.open()
    # # ws_client.subscribe(["BTC-USD"], ["heartbeats", "ticker"])
    # ws_client.subscribe(["BIT-26APR24-CDE"], ["heartbeats", "ticker"])
    # ws_client.sleep_with_exception_check(30)
    # # ws_client.run_forever_with_exception_check()
    # ws_client.close()

    ############################
    # def on_message(msg):
    #     print(msg)
    # ws_client = WSClient(api_key=API_KEY, api_secret=API_SECRET, on_message=on_message, verbose=True)
    #
    # try:
    #     ws_client.open()
    #     ws_client.subscribe(product_ids=["BTC-USD",], channels=["ticker", "heartbeats"])
    #     ws_client.run_forever_with_exception_check()
    # except WSClientConnectionClosedException as e:
    #     print("Connection closed! Retry attempts exhausted.")
    # except WSClientException as e:
    #     print("Error encountered!")
