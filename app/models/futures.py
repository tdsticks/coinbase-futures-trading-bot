from app import db


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


class AccountBalanceSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.String(64), nullable=True)
    available_margin = db.Column(db.Float, nullable=True)
    cbi_usd_balance = db.Column(db.Float, nullable=True)
    cfm_usd_balance = db.Column(db.Float, nullable=True)
    daily_realized_pnl = db.Column(db.Float, nullable=True)
    futures_buying_power = db.Column(db.Float, nullable=True)
    initial_margin = db.Column(db.Float, nullable=True)
    liquidation_buffer_amount = db.Column(db.Float, nullable=True)
    liquidation_buffer_percentage = db.Column(db.Integer, nullable=True)
    liquidation_threshold = db.Column(db.Float, nullable=True)
    total_open_orders_hold_amount = db.Column(db.Float, nullable=True)
    total_usd_balance = db.Column(db.Float, nullable=True)
    unrealized_pnl = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<AccountBalanceSummary {self.id} - Total CFM USD Balance: {self.cfm_usd_balance}>'


class FuturesOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(128), nullable=True)
    client_order_id = db.Column(db.String(128), nullable=True)
    product_id = db.Column(db.String(128), nullable=True)
    product_type = db.Column(db.String(128), nullable=True)
    order_type = db.Column(db.String(128), nullable=True)
    creation_origin = db.Column(db.String(128), default="coinbase_ui", nullable=True)

    # Bot notes: MAIN, DCA1, DCA3, DCA3, TAKE_PROFIT
    bot_note = db.Column(db.String(128), nullable=True)
    bot_active = db.Column(db.Boolean, default=False, nullable=True)
    order_status = db.Column(db.String(128), nullable=True)
    time_in_force = db.Column(db.String(128), nullable=True)
    order_placement_source = db.Column(db.String(128), nullable=True)
    side = db.Column(db.String(32), nullable=True)
    limit_price = db.Column(db.String(128), nullable=True)
    leverage = db.Column(db.String(128), nullable=True)
    margin_type = db.Column(db.String(50), nullable=True)
    is_liquidation = db.Column(db.Boolean, nullable=True)
    quote_size = db.Column(db.String(128), nullable=True)
    base_size = db.Column(db.String(128), nullable=True)
    size_in_quote = db.Column(db.String(128), nullable=True)
    size_inclusive_of_fees = db.Column(db.String(128), nullable=True)
    number_of_fills = db.Column(db.Integer, nullable=True)
    filled_size = db.Column(db.String(128), nullable=True)
    filled_value = db.Column(db.String(128), nullable=True)
    average_filled_price = db.Column(db.String(128), nullable=True)
    completion_percentage = db.Column(db.String(50), nullable=True)
    fee = db.Column(db.String(128), nullable=True)
    total_fees = db.Column(db.String(128), nullable=True)
    total_value_after_fees = db.Column(db.String(128), nullable=True)
    outstanding_hold_amount = db.Column(db.String(128), nullable=True)
    # stop_price = db.Column(db.String(128), nullable=True)
    success = db.Column(db.Boolean, nullable=False, default=False)
    settled = db.Column(db.String(128), nullable=True)
    edit_history = db.Column(db.String(128), nullable=True)
    cancel_message = db.Column(db.String(128), nullable=True)
    pending_cancel = db.Column(db.String(128), nullable=True)
    reject_message = db.Column(db.String(128), nullable=True)
    reject_reason = db.Column(db.String(128), nullable=True)
    failure_reason = db.Column(db.String(255), nullable=True)
    error_message = db.Column(db.String(255), nullable=True)
    error_details = db.Column(db.String(255), nullable=True)
    post_only = db.Column(db.Boolean, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    trigger_status = db.Column(db.String(128), nullable=True)
    created_time = db.Column(db.DateTime, nullable=True)
    last_fill_time = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<FuturesOrder {self.order_id} - {self.product_id} - {self.side}>'


class FuturePosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(128), nullable=False)
    creation_origin = db.Column(db.String(128), default="coinbase_ui", nullable=True)
    expiration_time = db.Column(db.DateTime, nullable=False)
    side = db.Column(db.String(10), nullable=False)
    number_of_contracts = db.Column(db.Integer, nullable=False)
    current_price = db.Column(db.Float, nullable=True)
    avg_entry_price = db.Column(db.Float, nullable=True)
    unrealized_pnl = db.Column(db.Float, nullable=True)
    daily_realized_pnl = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<FuturePosition {self.product_id} {self.side}>'
