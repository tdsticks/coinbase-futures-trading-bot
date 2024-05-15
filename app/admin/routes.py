from flask import redirect, url_for, request
from flask_admin import expose, AdminIndexView
from flask_login import current_user


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated and not current_user.is_superuser:
            return redirect(url_for('login', next=request.url))
        return super(MyAdminIndexView, self).index()