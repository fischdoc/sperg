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

    # do this or the tests wont pass
    def __eq__(self, other):
        if not isinstance(other, Game):
            return False
        return (
            self.game_id == other.game_id and
            self.start == other.start and
            self.end == other.end and
            self.location == other.location and
            self.team_home == other.team_home and
            self.team_away == other.team_away and
            self.score_home == other.score_home and
            self.score_away == other.score_away
        )

    def __hash__(self):
        return hash((
            self.game_id,
            self.start,
            self.end,
            self.location,
            self.team_home,
            self.team_away,
            self.score_home,
            self.score_away
        ))