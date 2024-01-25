from app import db

class Venue(db.Model):
    __tablename__ = 'Venue'

    def __init__(
      self, 
      name,
      city,
      state,
      address,
      phone,
      genres,
      facebook_link,
      image_link,
      website,
      seeking_talent,
      seeking_description):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.genres = genres
        self.facebook_link = facebook_link
        self.image_link = image_link
        self.website = website
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500), default='')
    shows = db.relationship('Show', backref='venue', lazy='dynamic')
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    def __init__(
      self, 
      name,
      city,
      state,
      phone,
      genres,
      facebook_link,
      image_link,
      website,
      seeking_venue,
      seeking_description):
        self.name = name
        self.city = city
        self.state = state
        self.phone = phone
        self.genres = genres
        self.facebook_link = facebook_link
        self.image_link = image_link
        self.website = website
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=True)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500), default='')
    shows_art = db.relationship('Show', backref='artist', lazy='dynamic')
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)


class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
