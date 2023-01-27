from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(90))
    state = db.Column(db.String(90))
    address = db.Column(db.String(90))
    phone = db.Column(db.String(90))
    website = db.Column(db.String(90))
    image_link = db.Column(db.String(650))
    facebook_link = db.Column(db.String(211))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(725))
    shows = db.relationship('Show', backref='venue', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f'<Venue {self.id} name: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(92))
    state = db.Column(db.String(92))
    phone = db.Column(db.String(92))
    website = db.Column(db.String(92))
    image_link = db.Column(db.String(650))
    facebook_link = db.Column(db.String(211))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(725))
    shows = db.relationship('Show', backref='artist', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f'<Artist {self.id} name: {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'