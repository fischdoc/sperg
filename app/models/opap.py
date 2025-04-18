from sqlalchemy.ext.mutable import MutableList

from .. import db


class Opap(db.Model):
    __tablename__ = 'opaps'

    opap_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(10), nullable=False)  # a string like 'USD', 'EUR', etc
    users = db.relationship('User', backref='opap', lazy=True)

    config_schema = db.Column(db.JSON, nullable=True)               # store the config schema. the whole thing.
    preferred_generator = db.Column(db.String(100), nullable=True)  # name to look up in registry
    generator_codes = db.Column(MutableList.as_mutable(db.JSON), nullable=True)  # store the raw code. this is compiled at runtime

    def __repr__(self):
        return f'<Opap {self.name}>'
