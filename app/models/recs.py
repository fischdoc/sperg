from .. import db

"""none of this is needed right now"""


class Recs(db.Model):
    __tablename__ = 'recs'

    rec_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    recommended_games = db.relationship('Game', secondary='recs_games', backref=db.backref('recs', lazy='dynamic'))

    def __repr__(self):
        return f'<Recs {self.rec_id}>'


# ass.table for many to many relationship
class RecsGames(db.Model):
    __tablename__ = 'recs_games'

    rec_id = db.Column(db.Integer, db.ForeignKey('recs.rec_id'), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), primary_key=True)
