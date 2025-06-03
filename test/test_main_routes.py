import unittest
from datetime import datetime

from flask import Flask
from flask.testing import FlaskClient
from app import create_app, db
from app.models import Coupon
from app.models.game import Game
from app.models.user import User
from app.models.opap import Opap


# original class, for the get endpoint
class MainRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        # self.opap = None  # keep it here // out of context

        with self.app.app_context():
            db.create_all()

            # copy dummy data
            self.opap = Opap(opap_id=1, location="SERBIA", name="Nostrabet", currency="RSD", config_schema={
                "generator": "random_recs",
                "schema": {
                    "game_id": "integer",
                    "team_home": "string",
                    "team_away": "string",
                    "score_home": "integer",
                    "score_away": "integer",
                    "start": "datetime",
                    "location": "string"
                }
            })
            self.user = User(opap_id=1, name="xrhstos xrhsths", birth_date=datetime(1997, 5, 15), reg_date=datetime(2020, 1, 10))
            self.game = Game(team_home="Team A", team_away="Team B", score_home=2, score_away=1, start=datetime(2020, 10, 1, 14, 0), end=datetime(2023, 10, 1, 16, 0), location="CROATIA")

            db.session.add(self.opap)
            db.session.add(self.user)
            db.session.add(self.game)
            db.session.commit()
            # get actual user_id after committing
            self.user_id = self.user.user_id    # opap 1 user
            self.opap_id = self.opap.opap_id    # keep opap 1
            # self.config_schema = self.opap.config_schema  # bandage fix

            # create recommendations and coupon separately, since it needs a user id
            recommendations = [
                {
                    "game_id": 4,
                    "location": "ALBANIA",
                    "score_away": None,
                    "score_home": None,
                    "start": "Fri, 03 Oct 2025 16:00:00 GMT",
                    "team_away": "FK Partizani",
                    "team_home": "HNK Hajduk Split"
                },
                {
                    "game_id": 7,
                    "location": "TURKIYE",
                    "score_away": 2,
                    "score_home": 3,
                    "start": "Mon, 02 Oct 2023 15:00:00 GMT",
                    "team_away": "PAOK",
                    "team_home": "Galatasaray SK"
                }
            ]
            self.coupon = Coupon(
                coupon_id=1,
                user_id=self.user.user_id,
                selections={"recommendations": recommendations},
                pred_home_score=0,
                pred_away_score=2,
                gen_timestamp=datetime.utcnow()
            )

            db.session.add(self.coupon)
            db.session.commit()

    def tearDown(self):
        return
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_echo(self):
        """punon"""
        response = self.client.post('/echo', json={"key": "value"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"key": "value"})
        response = self.client.post('/echo', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "No JSON data provided"})

    def test_generate_recommendations_user_not_found(self):
        """ punon """
        response = self.client.get('/recommendation/695437289/0/0')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "User not found"})

    def test_generate_recommendations_success(self):
        """ punon """
        _ = self.user_id  # force evaluation // this is 1

        # check response validity first
        response = self.client.get(f'/recommendation/{self.user_id}/0/0')
        self.assertEqual(response.status_code, 200)

        # check contents
        recommendations = response.json.get("recommendations")
        self.assertIsInstance(recommendations, list)
        self.assertIsNotNone(recommendations)

    def test_generate_recommendations_schema_not_found(self):
        """ punon """
        with self.app.app_context():
            # create it here bc errors
            opap_no_schema = Opap(location="GREECE", name="noschemaopap", currency="EUR", config_schema=None)
            db.session.add(opap_no_schema)
            db.session.commit()
            user_temp = User(opap_id=opap_no_schema.opap_id, name="xrhstos axrhstos", birth_date=datetime(1990, 1, 1), reg_date=datetime.utcnow())
            db.session.add(user_temp)
            db.session.commit()

            response = self.client.get(f'/recommendation/{user_temp.user_id}/0/0')
            # assert according to main_routes.py
            self.assertEqual(response.status_code, 404)
            data = response.get_json()
            self.assertIn("error", data)
            self.assertEqual(data["error"], "No recommendation schema found")

    def test_generate_recommendations_opap_not_found(self):
        """ punon """
        with self.app.app_context():
            # test with no opaps
            user_temp = User(opap_id=3, name="xrhstos axrhstos", birth_date=datetime(1990, 1, 1), reg_date=datetime.utcnow())
            db.session.add(user_temp)
            db.session.commit()

            response = self.client.get(f'/recommendation/{user_temp.user_id}/0/0')
            # assert according to main_routes.py
            self.assertEqual(response.status_code, 404)
            data = response.get_json()
            self.assertIn("error", data)
            self.assertEqual(data["error"], "Opap not found")

    def test_set_config(self):
        """ punon """
        with self.app.app_context():
            opap_id = self.opap_id  # should already exist

            payload = {
                "generator": "random_recs",
                "schema": {
                    "game_id": "integer",
                    "team_home": "string",
                    "team_away": "string",
                    "score_home": "integer",
                    "score_away": "integer",
                    "start": "datetime",
                    "location": "string"
                },
                "code": "def random_recs(): return []"
            }
            response = self.client.post(
                f"/config/{opap_id}",
                json=payload
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("message", response.json)
            self.assertEqual(response.json["message"], "Configuration updated successfully")

            # check if db updates (which it should)
            updated_opap = Opap.query.get(opap_id)
            self.assertEqual(updated_opap.preferred_generator, payload["generator"])
            self.assertEqual(updated_opap.config_schema, payload["schema"])

            # now check is data["overwrite"]==1 overwrites the data
            payload = {
                "generator": "random_recs",
                "schema": {
                    "game_id": "integer",
                    "team_home": "string",
                    "team_away": "string",
                    "score_home": "integer",
                    "score_away": "integer",
                    "start": "datetime",
                    "location": "string"
                },
                "overwrite": 1,
                "code": "def random_recs(): return []"
            }
            response = self.client.post(
                f"/config/{opap_id}",
                json=payload
            )
            updated_opap = Opap.query.get(opap_id)
            self.assertEqual(updated_opap.generator_codes, [payload["code"]])

    def test_get_config(self):
        with self.app.app_context():
            # store opap_id but load opap itself
            opap_id = self.opap_id
            opap = Opap.query.get(self.opap_id)

            # check if config_schema exists // expect 200
            response = self.client.get(f'/config/{opap_id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, opap.config_schema)

            # check if config_schema missing // expect 404
            # recycle same opap
            opap.config_schema = None
            db.session.commit()

            response = self.client.get(f'/config/{opap_id}')
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {"error": "Configuration schema not found"})

            # check if opap_id not found // expect 404
            response = self.client.get('/config/9999999')
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {"error": "Opap not found"})


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
