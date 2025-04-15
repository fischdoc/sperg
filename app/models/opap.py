from .. import db


class Opap(db.Model):
    __tablename__ = 'opaps'

    opap_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(10), nullable=False)  # a string like 'USD', 'EUR', etc
    config_schema = db.Column(db.JSON, nullable=True)
    users = db.relationship('User', backref='opap', lazy=True)

    def __repr__(self):
        return f'<Opap {self.name}>'
