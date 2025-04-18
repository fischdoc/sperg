import random
from .rec_registry import register_rec


class RecGenerator:
    def __init__(self, games, users):
        self.games = games
        self.users = users

    @register_rec("random_recs")
    def random_recs(self, user_id):
        # just pick sth random for now
        user_recs = [game for game in self.games if random.choice([True, False])]
        return user_recs

    @register_rec("all_games_recs")
    def all_games_recs(self, user_id):
        # recommend literally everything
        return self.games
