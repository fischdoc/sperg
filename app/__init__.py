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

    # ensure the instance folder exists
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
        from .models.opap import Opap
        from .models.coupon import Coupon
        #db.drop_all()
        db.create_all()

        from .routes import main_routes
        app.register_blueprint(main_routes.bp)

        # do the registry thing here zot na ruj
        from .services.rec_generator import random_recs
        from .services.rec_generator import all_games_recs
        from .services.rec_registry import register_rec
        register_rec("random_recs", random_recs)
        register_rec("all_games_recs", all_games_recs)

    return app
