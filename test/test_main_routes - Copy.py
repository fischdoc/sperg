import unittest
from datetime import datetime

from flask import Flask
from flask.testing import FlaskClient
from app import create_app, db
from app.models.game import Game
from app.models.user import User
from app.models.opap import Opap


class MainRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # self.opap = Opap(name="Test Opap", location="Test Location", currency="USD", config_schema={})  # not this
            self.opap = Opap(location="SERBIA", name="Nostrabet", currency="RSD", config_schema={
                "generator": "random_recs",
                "schema": {
                    "game_id": "integer",
                    "team_home": "string",
                    "team_away": "string"
                }
            })
            # self.user = User(name="Test User", opap=self.opap)  # not this
            self.user = User(opap_id=1, name="xrhstos xrhsths", birth_date=datetime(1997, 5, 15), reg_date=datetime(2020, 1, 10))
            # self.game = Game(team_home="Team A", team_away="Team B", score_home=2, score_away=1)  # not this
            self.game = Game(team_home="Team A", team_away="Team B", score_home=2, score_away=1, start=datetime(2020, 10, 1, 14, 0), end=datetime(2023, 10, 1, 16, 0), location="CROATIA")

            db.session.add(self.opap)
            db.session.add(self.user)
            db.session.add(self.game)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_echo(self):
        response = self.client.post('/echo', json={"key": "value"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"key": "value"})

    def test_generate_recommendations(self):
        response = self.client.get(f'/recommendation/{self.user.user_id}')
        self.assertEqual(response.status_code, 200)
        recommendations = response.json.get("recommendations")
        self.assertIsInstance(recommendations, list)
        if recommendations:
            self.assertIn("game_id", recommendations[0])
            self.assertIn("team_home", recommendations[0])
            self.assertIn("team_away", recommendations[0])

    def test_set_configs(self):
        new_config = {
            "generator": "all_games_recs",
            "schema": {
                "game_id": "integer",
                "team_home": "string",
                "team_away": "string"
            }
        }
        response = self.client.post(f'/config/{self.opap.opap_id}', json=new_config)
        self.assertEqual(response.status_code, 200)

        # verify the config was updated
        with self.app.app_context():
            updated_opap = Opap.query.get(self.opap.opap_id)
            self.assertEqual(updated_opap.config_schema, new_config)


if __name__ == '__main__':
    unittest.main()
