from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app import db
from app.models.coupon import Coupon
from app.models.game import Game
from app.models.user import User
from app.models.opap import Opap
from app.services.rec_registry import rec_registry
from app.services.sandbox import execute_recommendation
from app.services.rec_registry import register_rec

bp = Blueprint('main', __name__)

'''
@bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def handle_request(path):
    response = {
        "type": request.method,
        "path": f"/{path}"
    }
    return jsonify(response)
'''


@bp.route('/echo', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def echo():
    data = request.get_json()
    print(rec_registry)
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    return jsonify(data), 200


@bp.route('/recommendation/<int:user_id>', methods=['GET'])
def generate_recommendations(user_id):
    # this is very efficient
    games = Game.query.all()
    users = User.query.all()
    coupons = Coupon.query.all()
    opaps = Opap.query.all()

    user = User.query.get(user_id)
    opap = Opap.query.get(user.opap_id)

    # handle potential absence of data
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not opap or not opap.config_schema:
        return jsonify({"error": "No recommendation schema found"}), 404

    # prepare before getting method from registry
    generator = opap.preferred_generator  # a name to look up in the registry
    schema = opap.config_schema

    # get method from registry and generate recommendations
    method = rec_registry.get(generator)  # cannot run this directly
    if not method:
        print(rec_registry)
        method = rec_registry.get("random_recs")    # default behaviour is to get random recs. can be changed.
    recommended_games = method(games, users, coupons, opaps)

    """
    # TODO: you may replace the above with this:
    method = rec_registry.get(generator)

    # fallback to default if the given one is not registered
    if not method:
        method = rec_registry.get("random_recs")
    
    # decide whether it's a class method or a standalone function
    if hasattr(method, "__self__"):  # it's a bound method of RecGenerator
        recommended_games = method(user_id)
    else:  # standalone function, call directly
        recommended_games = method(user_id, games, users)
    
    >>> original:
    # get method from registry and generate recommendations
    method = rec_registry.get(generator)  # cannot run this directly
    if not method:
        method = rec_registry.get("random_recs")    # default behaviour is to get random recs. can be changed.
    rec_method = getattr(rec_gen, method.__name__)  # get the requested method (name)
    recommended_games = rec_method(user_id)
    """

    # format recommendations according to schema
    recommendations = []
    for game in recommended_games:
        rec = {key: getattr(game, key) for key in schema if hasattr(game, key)}
        recommendations.append(rec)

    # perfect handling - excellent use of foresight. errors were not a primary motivating factor here.
    def serialise_datetimes(obj):
        if isinstance(obj, list):
            return [serialise_datetimes(item) for item in obj]
        if isinstance(obj, dict):
            return {
                key: val.isoformat() if isinstance(val, datetime) else val
                for key, val in obj.items()
            }
        return obj

    # create coupon and send it to user
    # TODO: this clogs up the database. coupons must be deleted periodically. they must have an expiration date.
    coupon = Coupon()
    coupon.selections = serialise_datetimes(recommendations)  # straight up json idc. client figures this out on their own.
    db.session.add(coupon)
    db.session.commit()

    # do not add the user stuff bc the user hasn't bought it yet. that's for a different endpoint
    return jsonify({"coupon_id": coupon.coupon_id, "recommendations": recommendations})


@bp.route('/<int:user_id>/buy/<int:coupon_id>', methods=['GET'])
def buy_coupon(coupon_id, user_id):
    # here you could add sth about payment details. in the POST body
    # ideally this would be a POST request but i dont like opening postman every 2 seconds
    coupon = Coupon.query.get(coupon_id)
    user = User.query.get(user_id)

    # error handling. good target for tests ig
    if not coupon:
        return jsonify({"error": "Coupon not found"}), 404
    if coupon.user is not None:
        return jsonify({"error": "Coupon already sold"}), 400
    if not user:
        return jsonify({"error": "User not found"}), 404

    coupon.sale_timestamp = datetime.now(timezone.utc)
    coupon.user = user

    # attempt to save to data store (db for now)
    db.session.add(coupon)
    db.session.commit()

    # not checking for money or anything. let the fictional frontend devs handle this
    return jsonify({"message": "Coupon sale successful"}), 200


@bp.route('/recommendation/<string:generator_name>/<int:user_id>', methods=['GET'])
def old_generate_recommendations(generator_name, user_id):
    # Ffetch all for optimal performance
    games = Game.query.all()
    users = User.query.all()

    #rec_gen = RecGenerator(games, users)

    # best most scalable way to pick generators
    if generator_name == 'random_recs':
        recommendations = rec_gen.random_recs(user_id)
    elif generator_name == 'all_games_recs':
        recommendations = rec_gen.all_games_recs(user_id)
    else:
        return jsonify({"error": "Invalid generator name"}), 400

    return jsonify({"user_id": user_id, "recommendations": recommendations})


@bp.route('/config/<int:opap_id>', methods=['POST'])
def set_config(opap_id):
    data = request.get_json()
    opap = Opap.query.get(opap_id)

    # handle potential data nonexistence
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    if not opap:
        return jsonify({"error": "Opap not found"}), 404
    if "generator" not in data or "schema" not in data:
        # generator and schema must be defined. anything else is optional. prob ignored.
        return jsonify({"error": "Missing required fields: 'generator' and 'schema'"}), 400

    # get the code from the generator list
    if "code" in data:
        if opap.generator_codes is None:
            opap.generator_codes = []
        if "overwrite" in data and data["overwrite"] == 1:
            opap.generator_codes = [data["code"]]
        else:
            opap.generator_codes.append(data["code"])

    print(opap.generator_codes)

    # store data after all is done
    opap.config_schema = data["schema"]  # store schema in opap entry
    opap.preferred_generator = data["generator"]
    db.session.commit()

    return jsonify({"message": "Configuration updated successfully"}), 200


@bp.route('/config/<int:opap_id>', methods=['GET'])
def get_config(opap_id):
    opap = Opap.query.get(opap_id)
    if not opap:
        return jsonify({"error": "Opap not found"}), 404

    schema = opap.config_schema

    if schema:
        return opap.config_schema, 200
    else:
        return jsonify({"error": "Configuration schema not found"}), 404


@bp.route('/cleanup', methods=['GET'])
def debug_cleanup():
    db.session.query(Coupon).delete()
    db.session.commit()
    return jsonify({"message": "Database cleanup successful"}), 200
