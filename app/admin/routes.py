from flask import redirect, url_for, request
from flask_admin import expose, AdminIndexView
from flask_login import current_user
from app.models import db
from app.models.signals import AuroxSignal, FuturePriceAtSignal
from app.models.futures import FuturePosition, FuturesOrder


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated and not current_user.is_superuser:
            return redirect(url_for('login', next=request.url))
        # return super(MyAdminIndexView, self).index()

        # Query data for the dashboard
        latest_signals = AuroxSignal.query.order_by(AuroxSignal.timestamp.desc()).limit(17).all()
        latest_positions = FuturePosition.query.order_by(FuturePosition.expiration_time.desc()).limit(1).all()
        latest_orders = FuturesOrder.query.order_by(FuturesOrder.created_time.desc()).limit(10).all()

        # Render the custom dashboard template
        return self.render('admin/dashboard.html',
                           latest_signals=latest_signals,
                           latest_positions=latest_positions,
                           latest_orders=latest_orders)