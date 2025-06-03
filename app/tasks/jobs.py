from datetime import timedelta, datetime
from app.models import User
from app.models.coupon import Coupon
from app.models.game import Game
from app.models.opap import Opap


def add_coupon(selections, predictions, user_id, db_session=None):
    """ create a new coupon based on a list of selections and predictions"""

    # input validation for selections
    if not isinstance(selections, list) or not selections:
        raise ValueError("Selections list is empty")
    if not all(isinstance(sel, dict) and sel for sel in selections):
        raise ValueError("Selections contains empty dicts")
    # same but for predictions = [pred_home_Score, pred_away_score]
    if not isinstance(predictions, list) or not predictions:
        raise ValueError("Predictions list is empty")
    # other
    if user_id is not None:
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            raise ValueError("user_id must be an integer")

    # if no session is passed, assume job context and load app/db manually  // zot na ruj
    if db_session is None:
        from app import create_app, db
        app = create_app()
        with app.app_context():
            return _create_and_commit_coupon(selections, predictions, user_id, db.session)
    else:
        return _create_and_commit_coupon(selections, predictions, user_id, db_session)


def _create_and_commit_coupon(selections, predictions, user_id, session):
    new_coup = Coupon(pred_home_score=predictions[0], pred_away_score=predictions[1], selections=selections, user_id=user_id)
    session.add(new_coup)
    session.commit()
    print(f"Coupon with ID {new_coup.coupon_id} added")
    return new_coup


def add_user(user_data, db_session=None):
    """Register a new user. No authentication supported."""

    if not isinstance(user_data, list) or not user_data:
        raise ValueError("User data must be a non-empty list")
    if not all(user_data):
        raise ValueError("User data list contains empty values")
    if user_data[0] is not None and not isinstance(user_data[0], int):
        raise ValueError("opap_id must be an integer or None")

    # if no session is passed, assume job context and load app/db manually
    if db_session is None:
        from app import create_app, db
        app = create_app()
        with app.app_context():
            return _create_and_commit_user(user_data, db.session)
    else:
        return _create_and_commit_user(user_data, db_session)


def _create_and_commit_user(user_data, session):
    new_user = User(
        opap_id=user_data[0],
        name=user_data[1],
        birth_date=user_data[2]
    )
    session.add(new_user)
    session.commit()
    print(f"User with ID {new_user.user_id} added")
    return new_user


def add_game(game_data, db_session=None):
    """Register a new game. No authentication supported. Only future games allowed."""

    if not isinstance(game_data, list) or not game_data:
        raise ValueError("Game data must be a non-empty list")
    if not all(game_data):
        raise ValueError("Game data contains empty values")
    if game_data[0] < datetime.utcnow():
        raise ValueError("Game date must be in the future")

    # if no session is passed, assume job context and load app/db manually
    if db_session is None:
        from app import create_app, db
        app = create_app()
        with app.app_context():
            return _create_and_commit_game(game_data, db.session)
    else:
        return _create_and_commit_game(game_data, db_session)


def _create_and_commit_game(game_data, session):
    new_game = Game(
        start=game_data[0],
        location=game_data[1],
        team_home=game_data[2],
        team_away=game_data[3]
    )
    session.add(new_game)
    session.commit()
    print(f"Game with ID {new_game.game_id} added")
    return new_game


def add_opap(opap_data, db_session=None):
    """Register a new opap. No authentication supported."""

    if not isinstance(opap_data, list) or not opap_data:
        raise ValueError("Opap data must be a non-empty list")
    if not all(opap_data):
        raise ValueError("Opap data list contains empty values")
    if opap_data[0] is None or not isinstance(opap_data[0], str):
        raise ValueError("opap name must be a string")

    # if no session is passed, assume job context and load app/db manually
    if db_session is None:
        from app import create_app, db
        app = create_app()
        with app.app_context():
            return _create_and_commit_opap(opap_data, db.session)
    else:
        return _create_and_commit_opap(opap_data, db_session)


def _create_and_commit_opap(opap_data, session):
    new_opap = Opap(
        name=opap_data[0],
        location=opap_data[1],
        currency=opap_data[2]
    )
    session.add(new_opap)
    session.commit()
    print(f"Opap with ID {new_opap.opap_id} added")

    return new_opap


# def process_data(data):
#     # fake job this does nothing
#     print(f"Processing data: {data}")
#     print("Data type:", type(data))
