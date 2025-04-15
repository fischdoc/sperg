import unittest
from unittest.mock import patch
from app.services.rec_generator import RecGenerator
from app.models.game import Game


class TestRecGenerator(unittest.TestCase):

    def setUp(self):
        # more fake data
        self.games = [Game(game_id=1), Game(game_id=2), Game(game_id=3)]
        self.users = [1, 2, 3]  # sna duhet akoma
        self.rec_generator = RecGenerator(games=self.games, users=self.users)

    def test_all_games_recs(self):
        # are all games recommended?
        recommendations = self.rec_generator.all_games_recs(user_id=1)
        expected_recommendations = self.games
        self.assertEqual(recommendations, expected_recommendations)

    @patch('random.choice')
    def test_random_recs(self, mock_choice):
        # are random* games recommended?
        mock_choice.side_effect = [True, False, True]  # mock choices
        recommendations = self.rec_generator.random_recs(user_id=1)
        expected_recommendations = [self.games[0], self.games[2]]
        self.assertEqual(recommendations, expected_recommendations)


if __name__ == '__main__':
    unittest.main()
