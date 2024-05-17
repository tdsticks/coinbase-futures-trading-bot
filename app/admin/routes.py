from flask import redirect, url_for, request, current_app, jsonify
from flask_admin import expose, AdminIndexView
from flask_login import current_user
from app.models import and_
from app.models.signals import AuroxSignal
from app.models.futures import FuturePosition, FuturesOrder

# TODO: Add ajax updates for signals (2-3 min) and orders (1 min)


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated and not current_user.is_superuser:
            return redirect(url_for('login', next=request.url))

        # Query data for the dashboard
        latest_positions = FuturePosition.query.order_by(FuturePosition.expiration_time.desc()).limit(1).all()
        latest_orders = FuturesOrder.query.filter(
            and_(
                FuturesOrder.creation_origin == "bot_order",
                FuturesOrder.bot_active == 1,
            )
        ).all()
        latest_signals = AuroxSignal.query.order_by(AuroxSignal.timestamp.desc()).limit(17).all()

        avg_filled_price = 0.0
        current_price = 0.0

        if current_app.trade_manager.avg_filled_price:
            avg_filled_price = int(current_app.trade_manager.avg_filled_price)

        # Assign TradeManager properties to profit_loss object
        profit_loss_data = {
            "product_id": current_app.trade_manager.product_id,
            "side": current_app.trade_manager.side,
            "avg_filled_price": avg_filled_price,
            "current_price": current_price,
            "number_of_contracts": current_app.trade_manager.number_of_contracts,
            "calc_percentage": float(current_app.trade_manager.calc_percentage),
            "calc_profit_or_loss": float(current_app.trade_manager.calc_profit_or_loss)
        }

        # Render the custom dashboard template
        return self.render('admin/dashboard.html',
                           latest_signals=latest_signals,
                           latest_positions=latest_positions,
                           latest_orders=latest_orders,
                           profit_loss_data=profit_loss_data
                           )
        # return super(MyAdminIndexView, self).index()

    @expose('/latest_profit_loss_data')
    def latest_profit_loss_data(self):
        # print(":latest_profit_loss_data:")

        product_id = current_app.trade_manager.product_id

        avg_filled_price = 0.0
        current_price = 0.0

        if current_app.trade_manager.avg_filled_price:
            avg_filled_price = int(current_app.trade_manager.avg_filled_price)

        if product_id:
            bid, ask, avg_price = current_app.cb_adv_api.get_current_average_price(product_id=product_id)
            current_price = int(avg_price)

        profit_loss_data = {
            "product_id": current_app.trade_manager.product_id,
            "side": current_app.trade_manager.side,
            "avg_filled_price": avg_filled_price,
            "current_price": current_price,
            "number_of_contracts": current_app.trade_manager.number_of_contracts,
            "calc_percentage": float(current_app.trade_manager.calc_percentage),
            "calc_profit_or_loss": float(current_app.trade_manager.calc_profit_or_loss)
        }
        # print(" profit_loss_data:", profit_loss_data)
        return jsonify(profit_loss_data)

    @expose('/orders')
    def get_orders_for_tv(self):
        print(":get_orders_for_tv:")
        # Query the FuturesOrder model
        # orders = FuturesOrder.query.all()
        orders = FuturesOrder.query.filter(
            and_(
                FuturesOrder.creation_origin == "bot_order",
                FuturesOrder.bot_active == 1,
            )
        ).all()

        # Transform the query result into a list of dictionaries
        orders_data = [
            {
                'id': order.id,
                'creation_origin': order.creation_origin,
                'bot_note': order.bot_note,
                'order_status': order.order_status,
                'side': order.side,
                'limit_price': order.limit_price,
                'base_size': order.base_size,
                'settled': order.settled,
                'created_time': order.created_time.isoformat(),
                'last_fill_time': order.last_fill_time.isoformat() if order.last_fill_time else None
            }
            for order in orders
        ]

        # Return the JSON response
        return jsonify(orders_data)
