import unittest
from unittest.mock import patch

from app import create_app, db
from app.models import User, Coupon
from app.models.opap import Opap
from app.services.rec_generator import random_recs, all_games_recs, relevant_recs
from app.models.game import Game


class TestRecGenerator(unittest.TestCase):

    def setUp(self):
        # basic app context stuff // overdid it
        self.app = create_app('testing')
        self.client = self.app.test_client()

        # add fake data
        with self.app.app_context():
            db.create_all()

            from datetime import datetime
            db.session.add_all([
                Opap(location="GREECE", name="OPAP Drosopoulou", currency="EUR"),
                Opap(location="SERBIA", name="Nostrabet", currency="RSD", preferred_generator="random_recs"),
                Opap(location="BULGARIA", name="Efbet Sofia", currency="BGN", preferred_generator="top_games_recs"),
                Opap(location="ROMANIA", name="Superbet Bucharest", currency="RON", preferred_generator="all_games_recs"),
            ])

            db.session.add_all([
                Game(team_home="Manchester United", team_away="Chelsea", score_home=None, score_away=None,
                     start=datetime(2026, 4, 15, 16, 0), end=None, location="ENGLAND"),
                Game(team_home="Inter Milan", team_away="Napoli", score_home=None, score_away=None,
                     start=datetime(2027, 9, 10, 20, 45), end=None, location="ITALY"),
                Game(team_home="Sevilla", team_away="Atletico Madrid", score_home=None, score_away=None,
                     start=datetime(2026, 11, 2, 19, 30), end=None, location="SPAIN"),
                Game(team_home="Lyon", team_away="Monaco", score_home=None, score_away=None,
                     start=datetime(2027, 3, 22, 21, 0), end=None, location="FRANCE"),
                Game(team_home="RB Leipzig", team_away="Union Berlin", score_home=None, score_away=None,
                     start=datetime(2026, 7, 8, 18, 30), end=None, location="GERMANY"),
                Game(team_home="AZ Alkmaar", team_away="PSV", score_home=None, score_away=None,
                     start=datetime(2027, 5, 19, 15, 30), end=None, location="NETHERLANDS"),
                Game(team_home="Braga", team_away="Sporting CP", score_home=None, score_away=None,
                     start=datetime(2026, 8, 13, 20, 0), end=None, location="PORTUGAL"),
                Game(team_home="Barcelona", team_away="Real Madrid", score_home=3, score_away=3, start=datetime(2021, 5, 12, 18, 0), end=datetime(2021, 5, 12, 20, 0), location="SPAIN"),
                Game(team_home="Liverpool", team_away="Manchester City", score_home=1, score_away=2, start=datetime(2022, 3, 8, 17, 30), end=datetime(2022, 3, 8, 19, 30), location="ENGLAND"),
                Game(team_home="Juventus", team_away="AC Milan", score_home=0, score_away=1, start=datetime(2023, 4, 10, 20, 45), end=datetime(2023, 4, 10, 22, 45), location="ITALY"),
                Game(team_home="Bayern Munich", team_away="Borussia Dortmund", score_home=4, score_away=2, start=datetime(2020, 11, 21, 15, 30), end=datetime(2020, 11, 21, 17, 30), location="GERMANY")
            ])

            db.session.commit()

            db.session.add_all([
                User(opap_id=1, name="xrhstos xrhsths", birth_date=datetime(1997, 5, 15), reg_date=datetime(2020, 1, 10)),
                User(opap_id=2, name="elvisi prislliu", birth_date=datetime(1935, 1, 8), reg_date=datetime(2020, 4, 10)),
                User(opap_id=3, name="serial better", birth_date=datetime(1990, 3, 24), reg_date=datetime(2018, 1, 5)),
                User(opap_id=4, name="fatima", birth_date=datetime(1985, 8, 23), reg_date=datetime(2021, 3, 15))
            ])

            db.session.commit()
            self.games = Game.query.all()
            self.users = User.query.all()

    def test_all_games_recs(self):
        # are all games recommended?
        with self.app.app_context():
            recommendations = all_games_recs(None, self.games, self.users, None, None)
            expected_recommendations = self.games
            self.assertEqual(recommendations, expected_recommendations)

    @patch('random.choice')
    def test_random_recs(self, mock_choice):
        with self.app.app_context():
            all_games = Game.query.all()
            self.assertEqual(len(all_games), 11)  # i specifically added 11 random games

            # fake pattern. only the first 5 games are selected
            mock_choice.side_effect = [True] * 5 + [False] * 6

            recommendations = random_recs(None, None, None, None, None)
            expected = all_games[:5]

            self.assertEqual(recommendations, expected)

    @patch('random.choice')
    def test_random_recs_empty_fallback(self, mock_choice):
        # referring to the "this is bad" section of the random recs function
        mock_choice.side_effect = [False] * 11

        with self.app.app_context():
            recommendations = random_recs(None, None, None, None, None)
            if self.games:
                self.assertEqual(len(recommendations), 1)
                self.assertEqual(recommendations[0], self.games[0])
            else:
                self.assertEqual(recommendations, [])

    def test_relevant_recs_ignores_finished_games(self):
        with self.app.app_context():
            user = User(user_id=111, name="finished_games_test_user", opap_id=1)
            db.session.add(user)
            db.session.commit()

            from datetime import datetime
            coupon = Coupon(
                user_id=user.user_id,
                sale_timestamp=datetime.utcnow(),
                pred_home_score=0,
                pred_away_score=0,
                selections=[
                    {"game_id": 999, "team_home": "TeamX", "team_away": "TeamY",
                     "score_home": 0, "score_away": 0, "start": "2025-06-03T11:24:52", "location": "FRANCE"}
                ]
            )
            finished_game = Game(team_away="TeamY", team_home="TeamX", location="FRANCE",
                                 score_home=2, score_away=1, start=datetime(2024, 6, 3, 15, 30),
                                 end=datetime(2024, 6, 3, 17, 30))
            unfinished_game = Game(team_away="TeamY", team_home="TeamX", location="FRANCE",
                                   score_home=None, score_away=None, start=datetime(2027, 6, 3, 15, 30))

            db.session.add(coupon)           # coupon to be matched
            db.session.add(finished_game)    # finished game with matching teams
            db.session.add(unfinished_game)  # unfinished -||-
            db.session.commit()

            results = relevant_recs(user.user_id, None, None, None, None)

            # only unfinished should be returned
            self.assertIn(unfinished_game, results)
            self.assertNotIn(finished_game, results)


if __name__ == '__main__':
    unittest.main()
