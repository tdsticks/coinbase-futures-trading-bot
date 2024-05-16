from collections import defaultdict
from datetime import datetime
from app.models import db, set_db_errors, joinedload
import pytz

# Models
from app.models.signals import AuroxSignal, FuturePriceAtSignal


class SignalProcessor:
    def __init__(self, app):
        self.log = app.custom_log.log
        self.log(True, "D", None, ":Initializing SignalProcessor:")

        self.app = app
        self.db_errors = set_db_errors

        self.cb_adv_api = self.app.cb_adv_api

        self.signals = {}
        self.signal_weights = {}
        self.load_signal_weights()

    def write_db_signal(self, data):
        self.log(True, "I", None, ":write_db_signal:")

        # TODO: May need to convert these timestamps from Aurox as they're in ISO format

        signal_stored = False

        # Create a new AuroxSignal object from received data
        # Also write a record using the signal spot price, futures bid and ask
        #   and store the relationship ids to both
        with self.app.app_context():  # Push an application context
            # try:
            # Convert timestamp to datetime object if necessary
            # timestamp = data['timestamp']
            timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            timestamp = timestamp.replace(tzinfo=pytz.utc)
            # self.log(True, "I", "timestamp", timestamp)

            signal_spot_price = data['price'].replace(',', '')

            # Define a unique key combination for updating or inserting signals
            unique_key = {
                'trading_pair': data['trading_pair'],
                'time_unit': data['timeUnit']
            }

            # Attempt to find an existing signal with the same trading pair and time unit
            existing_signal = AuroxSignal.query.filter_by(**unique_key).order_by(
                AuroxSignal.timestamp.desc()).first()
            self.log(True, "I", "    > Existing Signal", existing_signal)

            new_signal = None

            try:
                # Check for existing signal to prevent duplicates
                if existing_signal:
                    # Update existing record
                    existing_signal.timestamp = timestamp
                    existing_signal.price = signal_spot_price
                    existing_signal.signal = data['signal']

                    # self.app.db.session.add(existing_signal)
                    db.session.add(existing_signal)

                    self.log(True, "I", "    > Updated existing signal", existing_signal)
                else:
                    # Create a new signal if none exists for the specific time unit and trading pair
                    new_signal = AuroxSignal(
                        timestamp=timestamp,
                        price=signal_spot_price,
                        signal=data['signal'],
                        trading_pair=data['trading_pair'],
                        time_unit=data['timeUnit']
                    )

                    # self.app.db.session.add(new_signal)
                    db.session.add(new_signal)

                    self.log(True, "I", "    > Stored new signal", new_signal)

                # self.app.db.session.commit()  # Commit changes at the end of processing
                db.session.commit()  # Commit changes at the end of processing

                signal_stored = True

            except self.db_errors as e:
                self.log(True, "E",
                         "    >>> Error with storing or retrieving AuroxSignal",
                         str(e))

                # self.app.db.session.rollback()
                db.session.rollback()

            next_months_product_id, next_month = self.cb_adv_api.check_for_contract_expires()

            # Now, get the bid and ask prices for the current futures product
            relevant_future_product = self.cb_adv_api.get_relevant_future_from_db(month_override=next_month)
            self.log(True, "I", "relevant_future_product product_id",
                     relevant_future_product.product_id)

            # Get the current bid and ask prices for the futures product related to this signal
            future_bid_price = 0
            future_ask_price = 0
            try:
                future_bid_ask_price = self.cb_adv_api.get_current_bid_ask_prices(
                    relevant_future_product.product_id)
                if 'pricebooks' in future_bid_ask_price:
                    future_bid_price = future_bid_ask_price['pricebooks'][0]['bids'][0]['price']
                    future_ask_price = future_bid_ask_price['pricebooks'][0]['asks'][0]['price']
            except AttributeError as e:
                self.log(True, "E",
                         "Unable to get Future Bid and Ask Prices",
                         "AttributeError:", e)
            except ValueError as e:
                self.log(True, "E",
                         "Unable to get Future Bid and Ask Prices",
                         "ValueError:", e)

            if next_months_product_id:
                self.log(True, "I",
                         "    > next_months_product_id", next_months_product_id)
                self.log(True, "I",
                         "    > next_month", next_month)

            if new_signal:
                signal_id = new_signal.id
            else:
                signal_id = existing_signal.id
            self.log(True, "I", "    > Signal ID", signal_id)

            try:
                # Find the related futures product based on the current futures product
                if relevant_future_product:
                    existing_future_price_signal = FuturePriceAtSignal.query.filter_by(signal_id=signal_id).first()
                    if existing_future_price_signal:
                        # Correct the updating process by setting each field separately
                        existing_future_price_signal.signal_spot_price = float(signal_spot_price)
                        existing_future_price_signal.future_bid_price = future_bid_price
                        existing_future_price_signal.future_ask_price = future_ask_price
                        existing_future_price_signal.future_id = relevant_future_product.id
                        self.log(True, "I", "Updated existing future price signal details")
                    else:
                        # If no existing record, create a new one
                        new_future_price_signal = FuturePriceAtSignal(
                            signal_id=signal_id,
                            signal_spot_price=float(signal_spot_price),
                            future_bid_price=future_bid_price,
                            future_ask_price=future_ask_price,
                            future_id=relevant_future_product.id
                        )

                        # self.app.db.session.add(new_future_price_signal)
                        db.session.add(new_future_price_signal)

                        self.log(True, "I", "Stored new future price signal")

                    # self.app.db.session.commit()
                    db.session.commit()
            except self.db_errors as e:
                self.log(True, "E",
                         "    >>> Error with storing or retrieving FuturePriceAtSignal",
                         str(e))

                # self.app.db.session.rollback()
                db.session.rollback()

            # except self.db_errors as e:
            #     self.log(True, "E",
            #              "    >>> Error with storing or retrieving the Aurox signal",
            #              str(e))

        return signal_stored

    def get_latest_weekly_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_weekly_signal:")

        with self.app.app_context():
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
        # self.log(True, "D", None,
        #                         ":get_latest_five_day_signal:")

        with self.app.app_context():

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
        # self.log(True, "D", None,
        #                         ":get_latest_three_day_signal:")

        with self.app.app_context():

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
        # self.log(True, "D", None,
        #                         ":get_latest_two_day_signal:")

        with self.app.app_context():

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
        # self.log(True, "D", None,
        #                         ":get_latest_daily_signal:")

        with self.app.app_context():

            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '1 Day') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_twelve_hr_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_12_hourly_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '12 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_eight_hr_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_8_hourly_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '8 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_six_hr_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_6_hour_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '6 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_four_hr_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_4_hourly_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '4 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_three_hr_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_3_hour_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '3 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_two_hr_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_2_hour_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '2 Hours') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_one_hour_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_1_hour_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '1 Hour') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_thirty_min_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_30_minute_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '30 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_twenty_min_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_20_minute_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '20 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_fifteen_min_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_15_minute_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '15 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_ten_min_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_10_minute_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '10 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def get_latest_five_min_signal(self):
        # self.log(True, "D", None,
        #                         ":get_latest_5_minute_signal:")

        with self.app.app_context():
            latest_signal = AuroxSignal.query \
                .options(joinedload(AuroxSignal.future_prices)) \
                .filter(AuroxSignal.time_unit == '5 Minutes') \
                .order_by(AuroxSignal.timestamp.desc()) \
                .first()
            if latest_signal:
                return latest_signal
            else:
                return None

    def load_signal_weights(self):
        """Load and cache signal weights from configuration."""
        for key in ['WEEKLY', 'FIVE_DAY', 'THREE_DAY', 'TWO_DAY', 'DAILY', 'TWELVE_HR',
                    'EIGHT_HR', 'SIX_HR', 'FOUR_HR', 'THREE_HR', 'TWO_HR', 'ONE_HOUR',
                    'THIRTY_MIN', 'TWENTY_MIN', 'FIFTEEN_MIN', 'TEN_MIN', 'FIVE_MIN']:
            self.signal_weights[key] = float(self.app.config[f'{key}_WEIGHT'])

    def fetch_signals(self):
        """Fetch latest signals for all time frames."""
        for key in self.signal_weights:
            key_lower = key.lower()
            method_name = f'get_latest_{key_lower}_signal'
            if hasattr(self, method_name):
                # print("method_name:", method_name)
                self.signals[key] = getattr(self, method_name)()
            else:
                self.log(True, "E", None, f"Method not found: {method_name}")
                self.signals[key] = None

    def calculate_scores(self):
        """Calculate scores for all signal groups."""
        group_scores = defaultdict(float)
        max_scores = defaultdict(float)

        for key, signal in self.signals.items():
            if signal:
                # print("signal.time_unit:", signal.time_unit)
                # print(" signal.signal:", signal.signal)
                weight = self.signal_weights[key]
                group = self.determine_group(key)
                direction_multiplier = 1 if signal.signal == 'long' else -1  # Determines the direction of the score
                group_scores[group] += direction_multiplier * weight  # Apply direction to the weight
                max_scores[group] += weight  # Accumulate maximum possible scores for normalization
                # print("group:", group)
        return group_scores, max_scores

    @staticmethod
    def determine_group(time_frame):
        """Determine which group a time frame belongs to."""
        if time_frame in ['WEEKLY', 'FIVE_DAY', 'THREE_DAY', 'TWO_DAY', 'DAILY', 'TWELVE_HR']:
            return 'group1'
        elif time_frame in ['EIGHT_HR', 'SIX_HR', 'FOUR_HR', 'THREE_HR', 'TWO_HR', 'ONE_HOUR']:
            return 'group2'
        elif time_frame in ['THIRTY_MIN', 'TWENTY_MIN', 'FIFTEEN_MIN', 'TEN_MIN', 'FIVE_MIN']:
            return 'group3'

    # @staticmethod
    def decide_direction_strength(self, normalized_score):

        strong = float(self.app.config['STRONG_SIGNAL_WEIGHT'])  # 0.5
        moderate = float(self.app.config['MODERATE_SIGNAL_WEIGHT'])  # 0.2
        neutral = float(self.app.config['NEUTRAL_SIGNAL_WEIGHT'])  # 0

        # Check for strong strength, where absolute value is needed to account
        #  for both positive and negative scores
        if normalized_score >= strong or normalized_score <= -strong:
            return 'STRONG'
        # Check for moderate strength, again using absolute value for both sides
        elif normalized_score >= moderate or normalized_score <= -moderate:
            return 'MODERATE'
        # Check for weak strength - non-zero but within the moderate range
        elif neutral < normalized_score < moderate or -moderate < normalized_score < neutral:
            return 'WEAK'
        # Neutral is exactly zero
        elif normalized_score == 0:
            return 'NEUTRAL'
        else:
            # This else condition might be redundant as all possible conditions are covered above
            return 'NEUTRAL'

    def should_enter_trade(self, group1, group2, group3):
        # Group 1 TF = Higher Timeframes
        # Group 2 TF = Mid-level Timeframes
        # Group 3 TF = Lower Timeframes

        trading_permitted = False

        grp1_msg = f"Grp 1 Dir: {group1['direction']} | Strength: {group1['strength']}"
        grp2_msg = f"Grp 2 Dir: {group2['direction']} | Strength: {group2['strength']}"
        grp3_msg = f"Grp 3 Dir: {group3['direction']} | Strength: {group3['strength']}"

        msg = (f"NOT a good time to trade!"
               f"\n > Group 1: {grp1_msg} "
               f"\n > Group 2: {grp2_msg} "
               f"\n > Group 3: {grp3_msg}")

        # If all three TF groups are in the same direct and a STRONG OR MODERATE lower TF strength
        if group3['direction'] == group2['direction'] == group1['direction']:
            if group3['strength'] == 'STRONG' or group3['strength'] == 'MODERATE':
                msg = (f"Higher, Mid-level and Lower are same direction with lower strength of: {group3['strength']}"
                       f"\nHigher TF Strength: {group1['strength']} | Mid-level TF Strength: {group2['strength']}")
                trading_permitted = True

        # Check the Mid TF and Lower TF direction first and a STRONG lower TF strength
        elif group2['direction'] == group3['direction'] and group3['strength'] == 'STRONG':
            msg = (f"Mid-level and Lower are same direction with lower strength of: {group3['strength']}"
                   f"\nHigher TF Strength: {group1['strength']} | Mid-level TF Strength: {group2['strength']}")
            trading_permitted = True

        # REVIEW: Disabling this for now as we may not want to factor in the higher timeframes with
        #  opening futures trades
        # Now, check the High TF and Lower TF direction second and a STRONG lower TF strength
        # elif group3['direction'] == group1['direction'] and group3['strength'] == 'STRONG':
        #     msg = (f"Higher and Lower are same direction with lower strength of: {group3['strength']}"
        #            f"\nHigher TF Strength: {group1['strength']} | Mid-level TF Strength: {group2['strength']}")
        #     trading_permitted = True

        self.log(True, "I", "Trading Message", msg)
        return trading_permitted

    def run(self):
        self.fetch_signals()
        scores, max_scores = self.calculate_scores()
        groups = {}
        group1 = {}
        group2 = {}
        group3 = {}
        trade_direction = 'neutral'

        for group, score in scores.items():
            # print(f"\n Group: {group} Score: {score}")

            direction = 'long' if score > 0 else 'short'
            # print(f" Direction: {direction}")

            normalized_score = round(score / max_scores[group], 2) if max_scores[group] != 0 else 0
            # print(f" normalized_score: {normalized_score}")

            strength = self.decide_direction_strength(normalized_score)
            self.log(True, "I", f"{group.upper()}"
                                f" | Direction: {direction.upper()}"
                                f" | Strength: {strength.upper()}"
                                f" | Normalized Score: {normalized_score}")
            if group == 'group1':
                group1['direction'] = direction
                group1['strength'] = strength
                group1['score'] = score
                group1['normalized_score'] = normalized_score
            elif group == 'group2':
                group2['direction'] = direction
                group2['strength'] = strength
                group2['score'] = score
                group2['normalized_score'] = normalized_score
            elif group == 'group3':
                group3['direction'] = direction
                group3['strength'] = strength
                group3['score'] = score
                group3['normalized_score'] = normalized_score

        groups["group1"] = group1
        groups["group2"] = group2
        groups["group3"] = group3

        trading_permitted = self.should_enter_trade(group1, group2, group3)
        # self.log(True, "I", " >>> Trade Permitted", trading_permitted)

        if trading_permitted:
            trade_direction = group3['direction']

        return trading_permitted, trade_direction, groups
