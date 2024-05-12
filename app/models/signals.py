from app import db
from datetime import datetime


class AuroxSignal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # timestamp = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    price = db.Column(db.String(20), nullable=True)
    signal = db.Column(db.String(10), nullable=True)
    trading_pair = db.Column(db.String(30), nullable=True)
    time_unit = db.Column(db.String(10), nullable=True)
    message = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<AuroxSignal {self.trading_pair} {self.signal} @ {self.timestamp}>"


class FuturePriceAtSignal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    signal_spot_price = db.Column(db.Float, nullable=True)
    future_bid_price = db.Column(db.Float, nullable=True)
    future_ask_price = db.Column(db.Float, nullable=True)
    signal_id = db.Column(db.Integer, db.ForeignKey('aurox_signal.id'), nullable=False)
    future_id = db.Column(db.Integer, db.ForeignKey('coinbase_future.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    signal = db.relationship('AuroxSignal', backref=db.backref('future_prices', lazy=True))
    future = db.relationship('CoinbaseFuture', backref=db.backref('signal_prices', lazy=True))

    def __repr__(self):
        return f"<FuturePriceAtSignal bid={self.future_bid_price} ask={self.future_ask_price} signal_id={self.signal_id} future_id={self.future_id}>"
