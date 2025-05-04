import os
from redis import Redis
from rq import Queue
from app import db
from app.models.coupon import Coupon


# broker setup stuff. do not touch if not broken
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(redis_url)
q = Queue(connection=redis_conn)


def add_coupon(selections, user_id=None):
    """create new coupon based on list of selections"""
    # TODO: pls improve this
    from app import create_app
    app = create_app()

    with app.app_context():
        new_coup = Coupon(
            selections=selections,
            user_id=user_id
        )
        db.session.add(new_coup)
        db.session.commit()
        print(f"Coupon ID {new_coup.coupon_id} added")


def process_data(data):
    # fake job this does nothing
    print(f"Processing data: {data}")
