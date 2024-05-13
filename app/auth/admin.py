from flask import redirect, url_for, request
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.form import Select2Widget
from flask_login import current_user

from app.models import db
from app.models.admin import Role
from app.models.futures import AccountBalanceSummary, FuturesOrder, FuturePosition, CoinbaseFuture
from app.models.signals import AuroxSignal


class SecureModelView(ModelView):
    def is_accessible(self):
        # print('SecureModelView.is_accessible')
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # print('SecureModelView.inaccessible')
        # Redirect to login page if user is not logged in
        return redirect(url_for('login', next=request.url))


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated and not current_user.is_superuser:
            return redirect(url_for('login', next=request.url))
        return super(MyAdminIndexView, self).index()


class UserAdmin(SecureModelView):
    column_list = ('username', 'email', 'role', 'is_active', 'is_authenticated', 'is_superuser')
    column_labels = {'username': 'Username', 'email': 'Email Address', 'role': 'Role'}
    column_filters = ('username', 'email', 'role.name')

    # Define the query factory for roles
    @staticmethod
    def role_query():
        return db.session.query(Role)

    form_extra_fields = {
        'role': QuerySelectField(
            label='Role',
            # query_factory=role_query,
            query_factory=lambda: db.session.query(Role),
            get_label='name',
            widget=Select2Widget(),
            allow_blank=False
        )
    }

    # Optional: Override to use your form_extra_fields
    def create_form(self, obj=None):
        return self._use_custom_form(super(UserAdmin, self).create_form(obj))

    def edit_form(self, obj=None):
        return self._use_custom_form(super(UserAdmin, self).edit_form(obj))

    def _use_custom_form(self, form):
        form.role.query_factory = lambda: db.session.query(
            Role).all()  # ensure this matches your database session and query
        return form


class RoleAdmin(SecureModelView):
    column_list = ('name',)
    column_labels = {'name': 'Role Name'}
    column_filters = ('name',)


class BalancesAdmin(SecureModelView):
    column_list = ('available_margin', 'cbi_usd_balance', 'cfm_usd_balance',
                   'daily_realized_pnl', 'futures_buffer_amount', 'initial_margin',
                   'liquidation_buffer_amount', 'liquidation_buffer_percentage', 'liquidation_threshold',
                   'total_open_orders_hold_amount', 'total_usd_balance', 'unrealized_pnl'
                   )
    column_labels = {'available_margin': 'Available Margin',
                     'cbi_usd_balance': 'USD Balance'}
    # column_filters = ('available_margin', 'cbi_usd_balance')


class CoinbaseFutureAdmin(SecureModelView):
    column_list = (
        'id', 'product_id', 'price', 'price_change_24h', 'volume_24h', 'volume_change_24h',
        'display_name', 'product_type', 'contract_expiry', 'contract_size', 'contract_root_unit',
        'status', 'trading_disabled'
    )


class AuroxSignalAdmin(SecureModelView):
    column_list = ('timestamp', 'price', 'signal', 'trading_pair', 'time_unit', 'message')
    column_labels = {'timestamp': 'Timestamp',
                     'price': 'Price',
                     'signal': 'Signal',
                     'trading_pair': 'Trading Pair',
                     'message': 'Message'
                     }
    column_filters = ('signal', 'time_unit', 'message')


class FuturesPositionAdmin(SecureModelView):
    column_list = (
        'id', 'product_id', 'creation_origin', 'expiration_time', 'side', 'number_of_contracts',
        'current_price', 'avg_entry_price', 'unrealized_pnl', 'daily_realized_pnl'
    )


class FuturesOrderAdmin(SecureModelView):
    column_list = (
        'id', 'order_id', 'client_order_id', 'product_id', 'product_type', 'order_type', 'creation_origin', 'bot_note',
        'bot_active', 'order_status', 'time_in_force', 'order_placement_source', 'side', 'limit_price', 'base_size',
        'number_of_fills', 'filled_size', 'filled_value', 'average_filled_price', 'completion_percentage', 'fee',
        'total_fees', 'total_value_after_fees', 'settled', 'edit_history', 'cancel_message', 'reject_message',
        'reject_reason', 'created_time', 'last_fill_time'
    )


# Add Flask Admin
admin = Admin(app, name='ATB Admin Panel',
              index_view=MyAdminIndexView(),
              template_mode='bootstrap4',
              # base_template='admin/my_admin.html'
              )

# Register the models with Flask-Admin
# admin.add_view(UserAdmin(User, db.session, name='Users'))
# admin.add_view(RoleAdmin(Role, db.session, name='Roles'))
admin.add_view(BalancesAdmin(AccountBalanceSummary, db.session))
admin.add_view(CoinbaseFutureAdmin(CoinbaseFuture, db.session))
admin.add_view(AuroxSignalAdmin(AuroxSignal, db.session))
admin.add_view(FuturesPositionAdmin(FuturePosition, db.session))
admin.add_view(FuturesOrderAdmin(FuturesOrder, db.session))