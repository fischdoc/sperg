import unittest
from datetime import datetime

from flask import Flask
from flask.testing import FlaskClient
from app import create_app, db
from app.models.game import Game
from app.models.user import User
from app.models.opap import Opap


# original class, for the get endpoint
class MainRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # copy dummy data
            self.opap = Opap(location="SERBIA", name="Nostrabet", currency="RSD", config_schema={
                "generator": "random_recs",
                "schema": ["game_id", "team_home", "team_away"]
            })
            self.user = User(opap_id=1, name="xrhstos xrhsths", birth_date=datetime(1997, 5, 15), reg_date=datetime(2020, 1, 10))
            self.game = Game(team_home="Team A", team_away="Team B", score_home=2, score_away=1, start=datetime(2020, 10, 1, 14, 0), end=datetime(2023, 10, 1, 16, 0), location="CROATIA")

            db.session.add(self.opap)
            db.session.add(self.user)
            db.session.add(self.game)
            db.session.commit()

            # get actual user_id after committing
            self.user_id = self.user.user_id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_echo(self):
        response = self.client.post('/echo', json={"key": "value"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"key": "value"})

    def test_generate_recommendations_user_not_found(self):
        response = self.client.get('/recommendation/695437289')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "User not found"})

    def test_generate_recommendations_success(self):
        response = self.client.get(f'/recommendation/{self.user_id}')
        self.assertEqual(response.status_code, 200)
        recommendations = response.json.get("recommendations")
        self.assertIsInstance(recommendations, list)
        if recommendations:
            self.assertIn("game_id", recommendations[0])
            self.assertIn("team_home", recommendations[0])
            self.assertIn("team_away", recommendations[0])


# just for the config endpoint
class ConfigRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create test data
            self.opap = Opap(location="SERBIA", name="Nostrabet", currency="RSD", config_schema={})
            db.session.add(self.opap)
            db.session.commit()

            # Retrieve the actual opap_id after committing
            self.opap_id = self.opap.opap_id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_set_config_empty_json(self):
        # json is empty
        response = self.client.post(
            f'/config/{self.opap_id}',
            json={},  # sending empty JSON object
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "No JSON data provided"})

    def test_set_config_missing_required_fields(self):
        # json exists, but is invalid
        payload = {
            "key": "value",
            "something": 123
        }

        response = self.client.post(
            f'/config/{self.opap_id}',
            json=payload,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Missing required fields: 'generator' and 'schema'"})

    def test_set_config_opap_not_found(self):
        fake_id = 9999
        payload = {
            "generator": "test_gen",
            "schema": "test_schema"
        }
        response = self.client.post(
            f'/config/{fake_id}',
            json=payload,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Opap not found"})


if __name__ == '__main__':
    unittest.main()
