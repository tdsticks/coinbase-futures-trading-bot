


#
# Routes
#
@app.route('/', methods=['GET'])
def index():
    # print(":index:")
    log.log(True, "I", True, None, ":index:")

    if request.method == 'GET':
        return "Its a bit empty here..."

    # if request.method == 'POST':
    #     data = request.json
    #     print("Received signal:", data)
    #     return jsonify({"status": "success", "message": "Signal received"}), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    log.log(True, "I", None, ":webhook:")

    # Parse the incoming JSON data
    data = request.json

    # If we get data
    if data:
        log.log(True, "I", None, "\nReceived signal:")
        # pp(data)
        log.log(True, "I", None, data)

        if 'signal' not in data:
            data['signal'] = 'test'

        signal_data = {
            'timestamp': data['timestamp'],
            'price': data['price'].replace(',', ''),  # Remove commas for numeric processing if necessary
            'signal': data['signal'],
            'trading_pair': data['symbol'],
            'timeUnit': data['timeUnit'],
            # 'message': data.get('message')  # Use .get for optional fields
        }

        now = datetime.now(pytz.utc)
        # print("Is trading time?", tm.is_trading_time(now))

        # Check if the market is open or not
        if tm.is_trading_time(now):
            try:
                # Get the SignalProcessor through the TradeManager
                signal_stored = tm.signal_processor.write_db_signal(signal_data, tm)
                log.log(True, "I", None, "  >>> Signal Stored", signal_stored)

                # Respond back to the webhook sender to acknowledge receipt
                return jsonify({"Status": "Success", "Message": "Signal received and stored"}), 201

            except Exception as e:
                log.log(True, "E", "Unexpected write_db_signal Error:", msg1=e)
                return jsonify({"Status": "Unsuccessful",
                                "Message": "Signal received, but NOT stored",
                                "Data": data,
                                "Error": e}), 405
    else:
        # Respond back to the webhook sender to acknowledge receipt
        return jsonify({"Status": "Unsuccessful",
                        "Message": "Signal not received",
                        "Sata": data}), 204


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))