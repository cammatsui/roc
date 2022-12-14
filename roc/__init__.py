import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DB_URI = 'SQLALCHEMY_DATABASE_URI'
TEST_DB_URI = 'sqlite:///site.db'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465


def create_app():
    # Create/configure the app.
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=os.environ['SECRET_KEY'])

    # Attach the app to the flask-sqlalchemy db instance according to the test_config.
    if 'DB_URL' in os.environ:
        # Use prod db; url/creds come from environment vars
        app.config[DB_URI] = "postgresql://{}:{}@{}/{}".format(
            os.environ['DB_USERNAME'],
            os.environ['DB_PASSWORD'],
            os.environ['DB_URL'],
            os.environ['DB_INSTANCE_NAME'],
        )
    else:
        # Use sqlite test db.
        app.config[DB_URI] = TEST_DB_URI

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['MAIL_SERVER'] = MAIL_SERVER
    app.config['MAIL_PORT'] = MAIL_PORT
    app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True


    db.init_app(app)

    # Register blueprints for the app.   
    from . import auth, routes, reviews, user, api
    app.register_blueprint(reviews.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(routes.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(api.bp)

    return app

app = create_app()
