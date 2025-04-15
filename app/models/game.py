from app import db


class Game(db.Model):
    __tablename__ = 'games'

    game_id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)  # start of game
    end = db.Column(db.DateTime, nullable=True)     # end of game (null if not finished yet)
    location = db.Column(db.String(100), nullable=False)   # country -> matches with opap.location
    team_home = db.Column(db.String(100), nullable=False)  # just a name
    team_away = db.Column(db.String(100), nullable=False)
    score_home = db.Column(db.Integer, nullable=True)      # simple int. null if no score
    score_away = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<Game {self.team_home} vs {self.team_away}>'
