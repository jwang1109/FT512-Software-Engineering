import os

from flask import Flask


def create_app(test_config=None):#jw822.SRP violated.there are too many responsibilities in one function, there is setting config, access to db. and register blueprint and so on. However, I believe it's acceptable, since these are all the things one must do when creating an app.
    
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'My NetID:jw822  Hello, World!'

    from . import db
    db.init_app(app)
    db.update_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from . import examples
    app.register_blueprint(examples.bp)


    return app
