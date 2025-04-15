from .. import db

class Bet(db.Model):
    __tablename__ = 'bets'

    bet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    prediction = db.Column(db.PickleType, nullable=False)  # tuple of ints
    result = db.Column(db.PickleType, nullable=True)       # likewise
    risk = db.Column(db.Float, nullable=False)             # god knows. keep it why not

    def __repr__(self):
        return f'<Bet {self.bet_id}>'
