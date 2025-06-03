import random
from sqlalchemy import and_
from .rec_registry import register_rec
from ..models import User
from ..models.coupon import Coupon
from ..models.game import Game


"""
default recommendation generators. they take all the input they can, even if its not used.
this allows the client to do whatever they want with their own custom code later.
"""


@register_rec("random_recs")
def random_recs(user_id, games, users, coupons, opaps):
    # just pick sth random for now
    games = Game.query.all()
    user_recs = [game for game in games if random.choice([True, False])]

    # this is bad. do not do this
    if not user_recs:
        if not games[0]:
            return []
        return [games[0]]

    return user_recs


@register_rec("all_games_recs")
def all_games_recs(user_id, games, users, coupons, opaps):
    # recommend literally everything
    return Game.query.all()


@register_rec("recent_games_recs")
def relevant_recs(user_id, games, users, coupons, opaps):
    # get the user's latest 10 purchases
    user = User.query.get(user_id)
    coupons = Coupon.query.filter_by(user_id=user.user_id).order_by(Coupon.sale_timestamp.desc()).limit(10).all()

    # gather unique teams in the user's previous purchases
    unique_teams = []
    for coupon in coupons:
        if coupon.user_id != user_id:
            continue  # very efficient practice
        selection_json_schema = coupon.selections
        for selection in selection_json_schema:
            team_away = selection["team_away"]
            team_home = selection["team_home"]
            if team_away not in unique_teams:
                unique_teams.append(team_away)
            if team_home not in unique_teams:
                unique_teams.append(team_home)

    # unique_teams is now a list of all team names the user has bought coupons for (home/away is irrelevant)
    # now do some sql sorcery to get only the games that involve those teams + are not finished yet
    relevant_games = Game.query.filter(
        and_(
            Game.team_away.in_(unique_teams),
            Game.team_home.in_(unique_teams),
            Game.score_home.is_(None)  # this is enough
        )
    ).all()

    return relevant_games
