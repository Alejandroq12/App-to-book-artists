import json
import dateutil.parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import babel
import datetime
from flask_moment import Moment
import collections
from config import *
from models import *
collections.Callable = collections.abc.Callable

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime


@app.route('/')
def index():
    venues = []
    artists = []

    try:
        recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()

        for venue in recent_venues:
            venues.append({
                "id": venue.id,
                "name": venue.name
            })

        recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
        for artist in recent_artists:
            artists.append({
                "id": artist.id,
                "name": artist.name
            })
    except:
        flash('An error occurred.')
    return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    # get all venues
    try:
        venues = Venue.query.all()

        areas = Venue.query.distinct(Venue.city, Venue.state).all()

        for location in areas:
            venuesQuery = Venue.query.filter_by(city=location.city).filter_by(state=location.state)
            #venuesQuery = Venue.query.all()

            venues = []
            for venue in venuesQuery:
                venues.append({
                    "id": venue.id,
                    "name": venue.name
                })

            data.append({
                "city": location.city,
                "state": location.state,
                "venues": venues
            })

        return render_template('pages/venues.html', areas=data);
    except:
        flash('An error occurred. Cannot display venues')
        return redirect(url_for('index'))


@app.route('/venues/search', methods=['POST'])
def search_venues():
    data = []
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    try:
        search_term = request.form.get('search_term', '')

        search = Venue.query.filter(
            Venue.name.ilike(f'%{search_term}%')
        ).filter(
            Venue.city.ilike(f'%{city}%')
        ).filter(
            Venue.state.ilike(f'%{state}%')
        ).all()

        for venue in search:
            data.append({
                "id": venue.id,
                "name": venue.name
            })

        response={
            "count": len(data),
            "data": data
        }
        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
    except:
        flash('An error occurred while searching')
        return redirect(url_for('venues'))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.filter_by(id=venue_id).all()[0]

    data={
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
        "upcoming_shows": []
    }

    shows = db.session.query(Show, Artist).filter_by(venue_id=venue_id).join(Artist).all()

    for (show, artist) in shows:
        if(show.start_time<datetime.datetime.now()):
            add_to="past_shows"
        else:
            add_to="upcoming_shows"
        data[add_to].append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })

    data["past_shows_count"]=len(data["past_shows"])
    data["upcoming_shows_count"]=len(data["upcoming_shows"])

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        # get form data and create 
        form = VenueForm()
        if request.method == 'POST' and form.validate():
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                seeking_description=form.seeking_description.data,
                website=form.website.data,
                seeking_talent=form.seeking_talent.data
            )

            # commit session to database
            db.session.add(venue)
            db.session.commit()

            # flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        else:
            errorMessage = "Errors in the following fields: "
            for error in form.errors:
                errorMessage += error + " "
            flash(errorMessage)
    except:
        # catches errors
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        # closes session
        db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Show.query.filter_by(venue_id=venue_id).delete()
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Successfully deleted the venue')
    except:
        flash('An error occurred when trying to delete the venue')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = []
    artists = Artist.query.order_by(Artist.name.asc()).all()
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    data = []
    try:
        search_term = request.form.get('search_term', '')

        search = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

        for artist in search:
            data.append({
                "id": artist.id,
                "name": artist.name
            })

        response = {
            "count": len(data),
            "data": data
        }
        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
    except:
        flash('An error occurred while searching')
        return redirect(url_for('artists'))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).all()[0]
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
        "upcoming_shows": []
    }

    shows = db.session.query(Show, Venue).filter_by(artist_id=artist_id).join(Venue).all()

    for (show, venue) in shows:
        if(show.start_time < datetime.now()):
            add_to = "past_shows"
        else:
            add_to = "upcoming_shows"
        data[add_to].append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })

    data["past_shows_count"] = len(data["past_shows"])
    data["upcoming_shows_count"] = len(data["upcoming_shows"])

    return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        Show.query.filter_by(artist_id=artist_id).delete()
        Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
        flash('Successfully deleted the artist')
    except:
        flash('An error occurred when trying to delete the artist')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))

# Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()
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
    }
    # populate form with fields from artist with ID <artist_id>
    form.state.default = data["state"]
    form.genres.default = data["genres"]
    form.seeking_venue.default = data["seeking_venue"]
    form.process()
    return render_template('forms/edit_artist.html', form=form, artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        form = ArtistForm()

        if request.method == 'POST' and form.validate():
            artist = Artist.query.filter_by(id=artist_id).first()
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.data
            artist.facebook_link = form.facebook_link.data
            artist.seeking_description = form.seeking_description.data
            artist.image_link = form.image_link.data
            artist.seeking_venue = form.seeking_venue.data

            # commit session to database
            db.session.add(artist)
            db.session.commit()

            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully updated!')

        else:
            error_message = "An error occurred. Errors in the following fields: "
            for error in form.errors:
                error_message += error + " "
            flash(error_message)

    except:
        # catches errors
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        # closes session
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).all()[0]
    data={
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
        "image_link": venue.image_link
    }
    form.state.default=data["state"]
    form.genres.default=data["genres"]
    form.seeking_talent.default=data["seeking_talent"]
    form.process()
    return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        form = VenueForm()

        if request.method == 'POST' and form.validate():

            venue = Venue.query.filter_by(id=venue_id).all()[0]

            venue.name=form.name.data
            venue.city=form.city.data
            venue.state=form.state.data
            venue.phone=form.phone.data
            venue.genres=form.genres.data
            venue.facebook_link=form.facebook_link.data
            venue.seeking_description=form.seeking_description.data
            venue.image_link=form.image_link.data
            venue.seeking_talent=form.seeking_talent.data

            # commit session to database
            db.session.add(venue)
            db.session.commit()
            # called upon submitting the new venue listing form

            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully updated!')
        else:
            errorMessage="An error occurred. Errors in the following fields: "
            for error in form.errors: errorMessage+=error+" "
            flash(errorMessage)
    except:
        # catches errors
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    finally:
        # closes session
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
    try:
        form = ArtistForm()
        if request.method == 'POST' and form.validate():

            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                seeking_description=form.seeking_description.data,
                image_link=form.image_link.data,
                seeking_venue=form.seeking_venue.data
            )

            # commit session to database
            db.session.add(artist)
            db.session.commit()
            # called upon submitting the new artist listing form

            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')

        else:
            errorMessage = "Errors in the following fields: "
            for error in form.errors:
                errorMessage += error + " "
            flash(errorMessage)

    except:
        # catches errors
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

    finally:
        # closes session
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []

    shows = db.session.query(Show, Venue, Artist).join(Venue).join(Artist).all()

    for (show, venue, artist) in shows:
        data.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # Renders form
    form = ShowForm()
    venues = Venue.query.filter_by(seeking_talent=True).all()
    form.venue_id.choices = [(venue.id, venue.name) for venue in venues]
    artists = Artist.query.filter_by(seeking_venue=True).all()
    form.artist_id.choices = [(artist.id, artist.name) for artist in artists]
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create/at_venue/<int:venue_id>')
def create_shows_at_venue(venue_id):
    # Renders form
    form = ShowForm()
    venue = Venue.query.filter_by(id=venue_id).first()
    form.venue_id.choices = [(venue.id, venue.name)]
    artists = Artist.query.all()
    form.artist_id.choices = [(artist.id, artist.name) for artist in artists]
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create/with_artist/<int:artist_id>')
def create_shows_with_artist(artist_id):
    # Renders form
    form = ShowForm()
    artist = Artist.query.filter_by(id=artist_id).first()
    form.artist_id.choices = [(artist.id, artist.name)]
    venues = Venue.query.filter_by(seeking_talent=True).all()
    form.venue_id.choices = [(venue.id, venue.name) for venue in venues]
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        form = ShowForm()
        show = Show(
            artist_id=form.artist_id.data, 
            venue_id=form.venue_id.data, 
            start_time=form.start_time.data
        )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
        app.logger.exception(e)
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
    app.logger.setLevel(logging.ERROR)
    file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(file_handler)



# Default port:
if __name__ == '__main__':
    app.run()

# Specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''