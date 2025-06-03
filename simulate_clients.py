import os
import random
from datetime import datetime, timedelta, date
from faker import Faker
from redis import Redis
from rq import Queue
from app.tasks.jobs import add_user, add_game, add_coupon, add_opap

"""
    How to run this:
    > open terminal 1
    > type the following in this order:
        > docker-compose down --volumes  # needed bc old volumes contain old code
        > docker-compose build --no-cache
        > docker-compose up redis
    > open terminal 2
    > type the following in this order:
        > docker-compose up --scale rqworker=5  # adjust as needed
    > click the run current file button on the top right of pycharm
"""

fake = Faker()

# adjust as needed for more data
NUM_OPAPS = 10
NUM_USERS = 100
NUM_GAMES = 200
NUM_COUPONS = 10

SIMULATED_OPAP_IDS = list(range(1, NUM_OPAPS))  # must match existing opap_ids in DB // theyre added incrementally anyway

user_ids = []
game_ids = []
balkan_teams = [
    "Panathinaikos",
    "Olympiacos",
    "Partizan Belgrade",
    "Red Star Belgrade",
    "Ludogorets Razgrad",
    "CSKA Sofia",
    "Dinamo București",
    "Hajduk Split",
    "Dinamo Zagreb",
    "Željezničar Sarajevo",
    "Vardar Skopje",
    "Shkëndija",
    "Partizani Tirana",
    "Budućnost Podgorica",
    "Olimpija Ljubljana",
]


redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(redis_url)
q = Queue(connection=redis_conn)

# do this to clear rqworker spam
# q.empty()
# exit()


def generate_user_data():
    opap_id = random.choice(SIMULATED_OPAP_IDS)
    name = fake.name()
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90)
    return [opap_id, name, birth_date]


def generate_game_data():
    start = datetime.utcnow() + timedelta(days=random.randint(1, 60))
    location = fake.country()
    team_home = random.choice(balkan_teams)
    team_away = random.choice([team for team in balkan_teams if team != team_home])
    return [start, location, team_home, team_away]


def generate_coupon_data():
    num_selections = random.randint(1, 5)
    selections = []
    for _ in range(num_selections):
        team_home = random.choice(balkan_teams)
        team_away = random.choice([team for team in balkan_teams if team != team_home])

        selections.append({
            "game_id": random.randint(1, 1000),
            "team_home": team_home,
            "team_away": team_away,
            "score_home": random.randint(0, 3),
            "score_away": random.randint(0, 3),
            "start": datetime.utcnow().replace(microsecond=0).isoformat(),
            "location": random.choice(["GREECE", "SERBIA", "BULGARIA", "ROMANIA"])  # who cares if they dont match
        })

    pred_home_score = random.randint(0, 5)
    pred_away_score = random.randint(0, 5)
    predictions = [pred_home_score, pred_away_score]
    user_id = random.choice(user_ids) if random.random() < 0.9 else None

    return [selections, predictions, user_id]


def generate_opap_data():
    name = fake.company()
    location = fake.city()
    currencies = ["EUR", "USD", "GBP", "JPY", "CHF", "AUD", "CAD"]
    currency = random.choice(currencies)
    return [name, location, currency]


def main():
    try:
        print("Queueing opap creation jobs...")
        for _ in range(NUM_OPAPS):
            name, location, currency = generate_opap_data()
            print(name, location, currency)
            q.enqueue(add_opap, [name, location, currency])

        print("Queueing user creation jobs...")
        for _ in range(NUM_USERS):
            user_data = generate_user_data()
            print(user_data)
            job = q.enqueue(add_user, user_data)
            user_ids.append(1)  # temp since user_id is unavailable

        print("Queueing game creation jobs...")
        for _ in range(NUM_GAMES):
            game_data = generate_game_data()
            print(game_data)
            job = q.enqueue(add_game, game_data)
            game_ids.append(1)  # temp

        print("Queueing coupon creation jobs...")
        for _ in range(NUM_COUPONS):
            selections, predictions, user_id = generate_coupon_data()
            print(selections, user_id)
            q.enqueue(add_coupon, selections, predictions, user_id)
        print("Simulation jobs queued successfully.")

    except ConnectionError:
        print("Error: Redis server cannot be reached.")


if __name__ == "__main__":
    main()