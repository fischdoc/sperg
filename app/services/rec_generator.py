import random
from .rec_registry import register_rec
from ..models.game import Game


"""
default recommendation generators. they take all the input they can, even if its not used.
this allows the client to do whatever they want with their own custom code later.
Consider doing this:
def some_strategy(games, users, **kwargs):
    user_id = kwargs.get("user_id")
    tags = kwargs.get("tags", [])
    ...
"""


@register_rec("random_recs")
def random_recs(games, users, coupons, opaps):
    # just pick sth random for now
    games = Game.query.all()
    user_recs = [game for game in games if random.choice([True, False])]
    return user_recs


@register_rec("all_games_recs")
def all_games_recs(games, users, coupons, opaps):
    # recommend literally everything
    return Game.query.all()
