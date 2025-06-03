import unittest
from datetime import datetime, timedelta, date
from app import create_app, db
from app.models.game import Game
from app.models.user import User
from app.models.opap import Opap
from app.models.coupon import Coupon
from app.tasks.jobs import add_coupon, add_user, add_game, add_opap


class TestAddCoupon(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.db_session = db.session

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_valid_coupon(self):
        selections = [{'game_id': 1, 'bet': 'home'}]
        predictions = [0, 0]
        coupon = add_coupon(selections, predictions, user_id=123, db_session=self.db_session)
        saved_coupon = Coupon.query.get(coupon.coupon_id)

        self.assertIsNotNone(saved_coupon)
        self.assertEqual(saved_coupon.user_id, 123)
        self.assertEqual(saved_coupon.selections, selections)
        self.assertEqual(saved_coupon.pred_home_score, predictions[0])
        self.assertEqual(saved_coupon.pred_away_score, predictions[1])

    def test_empty_selections(self):
        with self.assertRaises(ValueError) as context:
            add_coupon([], [0,0], user_id=123)
        self.assertIn("Selections list is empty", str(context.exception))

    def test_selections_with_empty_dict(self):
        with self.assertRaises(ValueError) as context:
            add_coupon([{}], [0,0], user_id=123)
        self.assertIn("Selections contains empty dict", str(context.exception))

    def test_invalid_user_id(self):
        with self.assertRaises(ValueError) as context:
            add_coupon([{'game_id': 1, 'bet': 'away'}], [0,0], user_id='abc')
        self.assertIn("user_id must be an integer", str(context.exception))

    def test_predictions_list_empty(self):
        with self.assertRaises(ValueError) as context:
            add_coupon([{'game_id': 1, 'bet': 'away'}], [], user_id='abc')
        self.assertIn("Predictions list is empty", str(context.exception))


class TestAddUser(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.db_session = db.session

        self.opap = Opap(
            name="Test Opap",
            location="Greece",
            currency="EUR",
            preferred_generator="default"
        )
        db.session.add(self.opap)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_valid_user(self):
        birth_date = date(1990, 5, 12)
        user_data = [self.opap.opap_id, "abc", birth_date]
        add_user(user_data, db_session=db.session)
        saved_user = User.query.first()
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.opap_id, self.opap.opap_id)
        self.assertEqual(saved_user.name, "abc")
        self.assertEqual(saved_user.birth_date, birth_date)

    def test_invalid_data_type(self):
        with self.assertRaises(ValueError) as context:
            add_user(654878, db_session=db.session)  # not a list
        self.assertIn("User data must be a non-empty list", str(context.exception))

    def test_empty_user_data_list(self):
        with self.assertRaises(ValueError) as context:
            add_user([], db_session=db.session)
        self.assertIn("User data must be a non-empty list", str(context.exception))

    def test_empty_value_in_data_list(self):
        with self.assertRaises(ValueError) as context:
            add_user([None, "", None], db_session=db.session)
        self.assertIn("User data list contains empty values", str(context.exception))

    def test_non_integer_opap_id(self):
        with self.assertRaises(ValueError) as context:
            add_user(["noStringIDs", "abc", datetime(1990, 1, 1)], db_session=db.session)
        self.assertIn("opap_id must be an integer or None", str(context.exception))


class TestAddGame(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.opap = Opap(
            name="TEST OPAP",
            location="GREECE",
            currency="EUR",
            preferred_generator="default"
        )
        db.session.add(self.opap)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_valid_game(self):
        future_time = datetime.utcnow() + timedelta(days=1)
        game_data = [future_time, "GREECE", "team1", "team2"]
        game = add_game(game_data, db_session=db.session)

        self.assertIsNotNone(game.game_id)
        saved_game = Game.query.get(game.game_id)
        self.assertIsNotNone(saved_game)
        self.assertEqual(saved_game.location, "GREECE")
        self.assertEqual(saved_game.team_home, "team1")
        self.assertEqual(saved_game.team_away, "team2")
        self.assertEqual(saved_game.start, future_time)

    def test_invalid_inputs(self):
        test_cases = [
            ("not a list", "Game data must be a non-empty list"),
            ([], "Game data must be a non-empty list"),
            ([None, "", "", ""], "Game data contains empty values"),
            ([datetime.utcnow() - timedelta(days=1), "GREECE", "team1", "team1"], "Game date must be in the future"),
        ]

        for game_data, expected_msg in test_cases:
            with self.subTest(game_data=game_data):
                with self.assertRaises(ValueError) as context:
                    add_game(game_data, db_session=db.session)
                self.assertIn(expected_msg, str(context.exception))


class TestAddOpap(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.db_session = db.session

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_valid_opap(self):
        opap_data = ["New Opap", "Athens", "EUR"]
        new_opap = add_opap(opap_data, db_session=self.db_session)
        saved_opap = Opap.query.get(new_opap.opap_id)

        self.assertIsNotNone(saved_opap)
        self.assertEqual(saved_opap.name, "New Opap")
        self.assertEqual(saved_opap.location, "Athens")
        self.assertEqual(saved_opap.currency, "EUR")

    def test_invalid_not_list(self):
        with self.assertRaises(ValueError) as context:
            add_opap("not a list", db_session=self.db_session)
        self.assertIn("Opap data must be a non-empty list", str(context.exception))

    def test_empty_opap_data_list(self):
        with self.assertRaises(ValueError) as context:
            add_opap([], db_session=self.db_session)
        self.assertIn("Opap data must be a non-empty list", str(context.exception))

    def test_empty_value_in_opap_data(self):
        with self.assertRaises(ValueError) as context:
            add_opap([None, "Athens", "EUR"], db_session=self.db_session)
        self.assertIn("Opap data list contains empty values", str(context.exception))

    def test_non_string_name(self):
        with self.assertRaises(ValueError) as context:
            add_opap([123, "Athens", "EUR"], db_session=self.db_session)
        self.assertIn("opap name must be a string", str(context.exception))
