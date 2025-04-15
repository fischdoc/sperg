from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

"""app factory = best practice"""


# db init
db = SQLAlchemy()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # testing errors persist if this is not included
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'mydatabase.db')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # more db init
    db.init_app(app)

    with app.app_context():
        # update this ose ke me pas problem
        from .models.user import User
        from .models.game import Game
        from .models.bet import Bet
        from .models.opap import Opap
        db.create_all()

        from .routes import main_routes
        app.register_blueprint(main_routes.bp)

    return app
