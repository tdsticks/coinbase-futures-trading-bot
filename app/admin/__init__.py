from flask import Blueprint
from flask_admin import Admin
from app.models.admin import User
from app.models.futures import AccountBalanceSummary, FuturesOrder, FuturePosition, CoinbaseFuture
from app.models.signals import AuroxSignal

from .routes import *
from .admin import *

# Initialize Blueprint
admin_bp = Blueprint('admin_bp', __name__,
                     template_folder='templates',)

# Initialize Flask-Admin
admin = Admin(name='ATB Admin Panel',
              index_view=MyAdminIndexView(),
              template_mode='bootstrap4',
              base_template='admin/my_admin.html')

# Add administrative views here
admin.add_view(UserAdmin(User, db.session, name='Users'))
admin.add_view(RoleAdmin(Role, db.session, name='Roles'))
admin.add_view(BalancesAdmin(AccountBalanceSummary, db.session))
admin.add_view(CoinbaseFutureAdmin(CoinbaseFuture, db.session))
admin.add_view(AuroxSignalAdmin(AuroxSignal, db.session))
admin.add_view(FuturesPositionAdmin(FuturePosition, db.session))
admin.add_view(FuturesOrderAdmin(FuturesOrder, db.session))


def setup_admin(app):
    admin.init_app(app)
    app.register_blueprint(admin_bp, url_prefix='/admin')
