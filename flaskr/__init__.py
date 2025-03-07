import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path,'flaskr.sqlite'),
    )

    if test_config is None:
        #load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        #load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits = ["200 per day","50 per hour"]
    )

    # a simple page that says hello
    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    blog.init_app(app, limiter)
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')


    return app
