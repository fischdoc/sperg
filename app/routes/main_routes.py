from flask import Blueprint, request, jsonify
from app import db
from app.models.game import Game
from app.models.user import User
from app.models.opap import Opap
from app.services.rec_generator import RecGenerator

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
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    return jsonify(data), 200


@bp.route('/recommendation/<int:user_id>', methods=['GET'])
def generate_recommendations(user_id):
    games = Game.query.all()
    users = User.query.all()

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    opap = Opap.query.get(user.opap_id)
    if not opap or not opap.config_schema:
        return jsonify({"error": "No recommendation schema found"}), 404

    generator_name = opap.config_schema.get("generator")
    schema = opap.config_schema.get("schema")
    rec_gen = RecGenerator(games, users)

    if generator_name == 'random_recs':
        recommended_games = rec_gen.random_recs(user_id)
    elif generator_name == 'all_games_recs':
        recommended_games = rec_gen.all_games_recs(user_id)
    else:
        return jsonify({"error": "Invalid generator name in schema"}), 400

    # format recommendations according to schema
    recommendations = []
    for game in recommended_games:
        rec = {key: getattr(game, key) for key in schema if hasattr(game, key)}
        recommendations.append(rec)

    return jsonify({"user_id": user_id, "recommendations": recommendations})


@bp.route('/recommendation/<string:generator_name>/<int:user_id>', methods=['GET'])
def old_generate_recommendations(generator_name, user_id):
    # Ffetch all for optimal performance
    games = Game.query.all()
    users = User.query.all()

    rec_gen = RecGenerator(games, users)

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
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    # generator and schema must be defined. anything else is optional. prob ignored.
    if "generator" not in data or "schema" not in data:
        return jsonify({"error": "Missing required fields: 'generator' and 'schema'"}), 400

    opap = Opap.query.get(opap_id)
    if not opap:
        return jsonify({"error": "Opap not found"}), 404

    opap.config_schema = data  # store schema in opap entry
    db.session.commit()

    return jsonify({"message": "Configuration updated successfully"}), 200


@bp.route('/config/<int:opap_id>', methods=['GET'])
def set_config(opap_id):
    opap = Opap.query.get(opap_id)
    if not opap:
        return jsonify({"error": "Opap not found"}), 404
    return opap.config_schema, 200
