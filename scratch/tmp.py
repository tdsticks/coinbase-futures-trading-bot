def write_db_signal(self, data):
    with self.flask_app.app_context():  # Ensures we're in the right context
        try:
            # Parse timestamp and adjust for timezone
            timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            timestamp = timestamp.replace(tzinfo=pytz.utc)

            # Convert signal spot price to float, assuming it's formatted as a string with commas
            signal_spot_price = float(data['price'].replace(',', ''))

            # Define a unique key combination for updating or inserting signals
            unique_key = {
                'trading_pair': data['trading_pair'],
                'time_unit': data['timeUnit']
            }

            # Attempt to find an existing signal with the same trading pair and time unit
            existing_signal = AuroxSignal.query.filter_by(**unique_key).order_by(AuroxSignal.timestamp.desc()).first()

            if existing_signal:
                # Update existing record
                existing_signal.timestamp = timestamp
                existing_signal.price = signal_spot_price
                existing_signal.signal = data['signal']
                db.session.add(existing_signal)
                self.log.log(True, "I", "Updated existing signal", existing_signal)
            else:
                # Create a new signal if none exists for the specific time unit and trading pair
                new_signal = AuroxSignal(
                    timestamp=timestamp,
                    price=signal_spot_price,
                    signal=data['signal'],
                    trading_pair=data['trading_pair'],
                    time_unit=data['timeUnit']
                )
                db.session.add(new_signal)
                self.log.log(True, "I", "Stored new signal", new_signal)

            # Additional logic to handle future prices (as per existing logic in your snippet)

            db.session.commit()  # Commit changes at the end of processing

        except db_errors as e:
            self.log.log(True, "E", "Error in signal processing", str(e))
            db.session.rollback()
