import os

from flask import Flask, render_template
from flask_login import LoginManager
from bigbucks import auth
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
from .db import update_db
from bigbucks import global_logger



def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    scheduler = BackgroundScheduler()
    scheduler.start()
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "db.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from bigbucks import db

    db.init_app(app)
    # initialize Flask-Login extension
    login_manager = LoginManager()
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        #from bigbucks.auth import User
        #return User.get(user_id)
        db = get_db()
        user_data = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user_data:
            return auth.User(user_data['id'], user_data['username'], user_data['password'])
        return None


    @app.route("/hello")
    def hello():
        return "Hello, World!"
    @app.route("/")
    def welcome():
        return render_template("auth/welcome.html")


    from . import home
    app.register_blueprint(home.bp)

    
    app.add_url_rule('/',endpoint = "index")
    
    # apply the blueprints to the app
    from bigbucks import auth
    # install log
    global_logger.setup_global_logger()
    print("set up logging")
    app.register_blueprint(auth.bp)
    
    from . import transactions
    app.register_blueprint(transactions.bp)
    
    from . import charting
    app.register_blueprint(charting.bp)

    from . import portfolio_builder
    app.register_blueprint(portfolio_builder.bp)

    from bigbucks import symbol
    app.register_blueprint(symbol.sy)



    # Schedule the update_db function to run every day at 00:00
    scheduler.add_job(func=update_db,
                      args=[app],
                      trigger=CronTrigger(hour=00, minute=00),  # Run daily at 00:00
                      id='update_database_job',
                      name='Update database',
                      replace_existing=True)
    # Shut down the scheduler when the Flask app is stopped
    atexit.register(lambda: scheduler.shutdown())
    
    
    return app
