from db import db


class CoinbaseFuture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(128), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=True)
    price_change_24h = db.Column(db.Float, nullable=True)
    volume_24h = db.Column(db.Float, nullable=True)
    volume_change_24h = db.Column(db.Float, nullable=True)
    # quote_increment = db.Column(db.Float, nullable=True)
    # quote_min_size = db.Column(db.Float, nullable=True)
    # quote_max_size = db.Column(db.Float, nullable=True)
    # base_min_size = db.Column(db.Float, nullable=True)
    # base_max_size = db.Column(db.Float, nullable=True)
    # base_name = db.Column(db.String(128), nullable=True)
    # quote_name = db.Column(db.String(128), nullable=True)
    display_name = db.Column(db.String(128), nullable=True)
    product_type = db.Column(db.String(64), nullable=True)
    contract_expiry = db.Column(db.DateTime, nullable=True)
    contract_size = db.Column(db.Float, nullable=True)
    contract_root_unit = db.Column(db.String(64), nullable=True)
    # venue = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(64), nullable=True)
    trading_disabled = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return f'<CoinbaseFuture {self.display_name} {self.product_id}>'
