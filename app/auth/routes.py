from flask_login import login_user, logout_user, login_required
from flask import request, flash, abort, redirect, url_for, render_template
from urllib.parse import urlparse, urljoin
from app.models.admin import User

from . import auth
from .. import bcrypt, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("login request.method == 'POST'")
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            print("login user:", user)
            login_user(user)
            next_page = request.args.get('next')
            print("next_page:", next_page)
            # Security check to make sure we do not redirect to a different site
            if not is_safe_url(next_page):
                print("is_safe_url next_page:", next_page)
                return abort(400)
            print("redirect(next_page or url_for('admin.index'))")
            return redirect(next_page or url_for('admin.index'))
        else:
            print("Invalid username or password")
            flash('Invalid username or password')
    print("render_template('login.html')")
    return render_template('login.html')


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
