#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import os
import json
import dateutil.parser
import babel
import re
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from re import search

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# Heroku db path
database_path = os.getenv("DATABASE_URL")
if database_path.startswith("postgres://"):
    database_path = database_path.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

setup_db(app)
#db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Helper Functions.
#----------------------------------------------------------------------------#

def assign_artist_data_to_past_shows(data, show):
    artist = db.session.query(Artist).join(Show, Artist.id==show.artist_id).first()
    print(artist)
    data["past_shows"].append({
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
def assign_artist_data_to_upcoming_shows(data, show):
    artist = Artist.query.filter_by(id=show.artist_id).first()
    data["upcoming_shows"].append({
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
def assign_venue_data_to_past_shows(data, show):
    venue = db.session.query(Venue).join(Show, Venue.id==show.venue_id).first()
    data["past_shows"].append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
def assign_venue_data_to_upcoming_shows(data, show):
    venue = Venue.query.filter_by(id=show.venue_id).first()
    data["upcoming_shows"].append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  venue_query = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  city_and_state = ''
  data = []
  for venue in venue_query:
      
      upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
      if city_and_state == venue.city + venue.state:
          data[len(data) - 1]["venues"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(upcoming_shows)
          })
      else:
          city_and_state = venue.city + venue.state
          data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": [{
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": len(upcoming_shows)
            }]
          })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  
  data = []
  count = 0
  searchTerm = request.form.get('search_term')
  venues = Venue.query.all()
  for venue in venues:
    name = venue.name
    if search(searchTerm, name, re.IGNORECASE):
      data.append({
        "id": venue.id,
        "name": name,
        "num_upcoming_shows": venue.upcoming_shows_count
      })
      count+=1

  response = {
    "count": count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  
  venue = Venue.query.get(venue_id)
  current_time = datetime.now()
  past_shows = venue.shows.filter(Show.start_time < current_time).order_by('artist_id').all()
  upcoming_shows = venue.shows.filter(Show.start_time > current_time).order_by('artist_id').all()
  print(venue.genres)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  for show in past_shows:
    assign_artist_data_to_past_shows(data, show)
  for show in upcoming_shows:
    assign_artist_data_to_upcoming_shows(data, show)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  venueName = request.form['name']
  seekingTalent = True if (request.form.get('seeking_talent') == 'y') else False

  for item in request.form.get('genres'):
    print(item)
  try:
    venue = Venue (
      venueName,
      request.form.get('city'),
      request.form.get('state'),
      request.form.get('address'),
      request.form.get('phone'),
      request.form.getlist('genres'),
      request.form.get('facebook_link'),
      request.form.get('image_link'),
      request.form.get('website_link'),
      seekingTalent,
      request.form.get('seeking_description')
    )
    
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venueName + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + venueName + ' could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  

  data = []
  artists = Artist.query.order_by('id').all()
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  

  data = []
  count = 0
  searchTerm = request.form.get('search_term')
  artists = Artist.query.all()
  for artist in artists:
    name = artist.name
    if search(searchTerm, name, re.IGNORECASE):
      data.append({
        "id": artist.id,
        "name": name,
        "num_upcoming_shows": artist.upcoming_shows_count
      })
      count+=1

  response = {
    "count": count,
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  #done but why are genres showing up weird????????
  
  artist = Artist.query.get(artist_id)
  current_time = datetime.now()
  past_shows = artist.shows_art.filter(Show.start_time < current_time).all()
  upcoming_shows = artist.shows_art.filter(Show.start_time > current_time).all()
  print(artist.genres)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  for show in past_shows:
    assign_venue_data_to_past_shows(data, show)
  for show in upcoming_shows:
    assign_venue_data_to_upcoming_shows(data, show)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  #do i need to put the current values as placeholders in the form fields?????
  
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  seekingVenue = True if (request.form.get('seeking_venue') == 'y') else False

  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link = request.form.get('image_link')
    artist.website = request.form.get('website_link')
    artist.seeking_venue = seekingVenue
    artist.seeking_description = request.form.get('seeking_description')

    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  #do i need to put the current values as placeholders in the form fields?????

  form = VenueForm()
  venue = Venue.query.get(venue_id)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  seekingTalent = True if (request.form.get('seeking_talent') == 'y') else False

  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link')
    venue.image_link = request.form.get('image_link')
    venue.website = request.form.get('website_link')
    venue.seeking_talent = seekingTalent
    venue.seeking_description = request.form.get('seeking_description')

    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  artistName = request.form['name']
  seekingVenue = True if (request.form.get('seeking_venue') == 'y') else False
  try:
    artist = Artist (
      artistName,
      request.form.get('city'),
      request.form.get('state'),
      request.form.get('phone'),
      request.form.getlist('genres'),
      request.form.get('facebook_link'),
      request.form.get('image_link'),
      request.form.get('website_link'),
      seekingVenue,
      request.form.get('seeking_description')
    )
    
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + artistName + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + artistName + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
 
  data = []

  shows = Show.query.order_by('id').all()

  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    data.append({
      "venue_id": show.venue_id,
      "artist_id": show.artist_id,
      "venue_name": venue.name,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    show = Show (
      artist_id=request.form.get('artist_id'),
      venue_id=request.form.get('venue_id'),
      start_time=request.form.get('start_time')
    )
    
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
