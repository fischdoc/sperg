from .. import db
from datetime import datetime


class Coupon(db.Model):
    __tablename__ = 'coupons'

    coupon_id = db.Column(db.Integer, primary_key=True)
    pred_home_score = db.Column(db.Integer, nullable=False)
    pred_away_score = db.Column(db.Integer, nullable=False)
    selections = db.Column(db.JSON, nullable=False)  # json based on opap.config_schema. recs generated elsewhere
    gen_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sale_timestamp = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    user = db.relationship('User', backref=db.backref('coupons', lazy=True))

    def __repr__(self):
        return f'<Coupon {self.coupon_id} bought by {self.user_id}>'
