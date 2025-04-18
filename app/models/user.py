from .. import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    opap_id = db.Column(db.Integer, db.ForeignKey('opaps.opap_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)  # Assuming birth_date can be nullable
    reg_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Automatically set to current time
    #betting_history = db.relationship('Bet', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'
