from app import create_app, db
from app.models.user import User
from app.models.game import Game
from app.models.opap import Opap
from app.models.bet import Bet
from app.models.recs import Recs
from datetime import datetime

app = create_app()
app.app_context().push()


# populate with dummy data
def populate_database():
    db.session.add_all([
        Opap(location="GREECE", name="OPAP Drosopoulou", currency="EUR"),
        Opap(location="SERBIA", name="Nostrabet", currency="RSD")
    ])

    db.session.add_all([
        Game(team_home="Fenerbahce", team_away="Dinamo Zagreb", score_home=2, score_away=1, start=datetime(2020, 10, 1, 14, 0), end=datetime(2023, 10, 1, 16, 0), location="CROATIA"),
        Game(team_home="Red Star Belgrade", team_away="Olympiakos", score_home=3, score_away=2, start=datetime(2022, 10, 2, 15, 0), end=datetime(2023, 10, 2, 17, 0), location="SERBIA"),
        Game(team_home="Galatasaray SK", team_away="PAOK", score_home=3, score_away=2, start=datetime(2023, 10, 2, 15, 0), end=datetime(2023, 10, 2, 17, 0), location="TURKIYE"),
        Game(team_home="HNK Hajduk Split", team_away="FK Partizani", score_home=None, score_away=None, start=datetime(2025, 10, 3, 16, 0), end=None, location="ALBANIA")
    ])

    db.session.add_all([
        User(opap_id=1, name="xrhstos xrhsths", birth_date=datetime(1997, 5, 15), reg_date=datetime(2020, 1, 10)),
        User(opap_id=1, name="elvisi prislliu", birth_date=datetime(1935, 1, 8), reg_date=datetime(2020, 4, 10)),
        User(opap_id=2, name="serial better", birth_date=datetime(1990, 3, 24), reg_date=datetime(2018, 1, 5)),
        User(opap_id=2, name="fatima", birth_date=datetime(1985, 8, 23), reg_date=datetime(2021, 3, 15))
    ])

    db.session.add_all([
        Recs(user_id=1, recommended_games=[Game.query.get(1), Game.query.get(2)]),
        Recs(user_id=2, recommended_games=[Game.query.get(2), Game.query.get(3)])
    ])

    db.session.add_all([
        Bet(user_id=1, game_id=1, amount=50.0, prediction=(2, 1), result=(2, 1), risk=0.5),
        Bet(user_id=2, game_id=2, amount=100.0, prediction=(3, 2), result=(3, 2), risk=0.3)
    ])

    db.session.commit()

    print("Database populated with dummy data.")


if __name__ == "__main__":
    populate_database()
