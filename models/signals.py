from db import db


class AuroxSignal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=True)
    price = db.Column(db.String(20), nullable=True)
    signal = db.Column(db.String(10), nullable=True)
    trading_pair = db.Column(db.String(30), nullable=True)
    time_unit = db.Column(db.String(10), nullable=True)
    message = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<AuroxSignal {self.trading_pair} {self.signal} @ {self.timestamp}>"
