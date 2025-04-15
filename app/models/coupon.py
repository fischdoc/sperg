from .. import db


class Coupon(db.Model):
    __tablename__ = 'coupons'

    coupon_id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', backref='coupon', lazy=True)

    def __repr__(self):
        return f'<Coupon {self.name}>'
