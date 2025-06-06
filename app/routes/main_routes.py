from datetime import datetime
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


######### ACTUAL ENDPOINTS #########
@bp.route('/recommendation/<int:user_id>/<int:score_home>/<int:score_away>', methods=['GET'])
def generate_recommendations(user_id, score_home, score_away):
    # this is very efficient
    games = Game.query.all()
    users = User.query.all()
    coupons = Coupon.query.all()
    opaps = Opap.query.all()

    # get data and handle potential absence thereof
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    opap = Opap.query.get(user.opap_id)
    if not opap:
        return jsonify({'error': 'Opap not found'}), 404
    if not opap.config_schema:
        return jsonify({"error": "No recommendation schema found"}), 404

    # prepare before getting method from registry
    generator = opap.preferred_generator  # a name to look up in the registry
    schema = opap.config_schema

    # get method from registry and generate recommendations
    method = rec_registry.get(generator)  # cannot run this directly
    if not method:
        # print(rec_registry)
        method = rec_registry.get("random_recs")    # default behaviour is to get random recs. can be changed.
    recommended_games = method(user_id, games, users, coupons, opaps)
    # print(recommended_games)

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
    coupon.pred_home_score = score_home
    coupon.pred_away_score = score_away

    db.session.add(coupon)
    db.session.commit()

    # do not add the user stuff bc the user hasn't bought it yet. that's for a different endpoint
    return jsonify({"coupon_id": coupon.coupon_id, "recommendations": recommendations})


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

        # now add that to the registry
        function = execute_recommendation(data["code"], allowed_globals={}, function_name=data["generator"])
        register_rec(data["generator"], function)

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


######### DEBUG & TESTING #########
@bp.route('/cleanup', methods=['GET'])
def debug_cleanup():
    # for my own convenience
    db.session.query(Coupon).delete()
    db.session.commit()
    return jsonify({"message": "Database cleanup successful"}), 200


@bp.route('/echo', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def echo():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    return jsonify(data), 200
