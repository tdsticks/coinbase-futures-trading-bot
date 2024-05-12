from . import auth
from flask import render_template, request, jsonify

# @main.route('/')
# def index():
#     return "Welcome to the Home Page!"


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         print("login request.method == 'POST'")
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#         if user and bcrypt.check_password_hash(user.password, password):
#             print("login user:", user)
#             login_user(user)
#             next_page = request.args.get('next')
#             print("next_page:", next_page)
#             # Security check to make sure we do not redirect to a different site
#             if not is_safe_url(next_page):
#                 print("is_safe_url next_page:", next_page)
#                 return abort(400)
#             print("redirect(next_page or url_for('admin.index'))")
#             return redirect(next_page or url_for('admin.index'))
#         else:
#             print("Invalid username or password")
#             flash('Invalid username or password')
#     print("render_template('login.html')")
#     return render_template('login.html')
#
#
# def is_safe_url(target):
#     ref_url = urlparse(request.host_url)
#     test_url = urlparse(urljoin(request.host_url, target))
#     return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
#
#
# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login'))
