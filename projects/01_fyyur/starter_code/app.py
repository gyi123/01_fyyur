#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import db, Venue,Artist,Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database

migrate = Migrate(app, db)


    
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
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.order_by(Venue.city.asc(), Venue.state.asc()).all()
  data = []
  elem = {
    "city": "",
    "state": "",
    "venues": []
      }
  now = datetime.now()
  for v in venues:
      upcomingShows = list(filter(lambda s : s.start_time > now, v.shows))
      if v.state == elem["state"] and v.city == elem["city"]:
          elem["venues"].append({
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows": len(upcomingShows)
              })
      else:
          elem = {
              "city": v.city,
              "state": v.state,
              "venues": []
              } 
          elem["venues"].append({
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows": len(upcomingShows)
              })          
          data.append(elem)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  searchString = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.contains(searchString)).all()
  data = []
  now = datetime.now().time()
  for venue in venues:
      shows = list(filter(lambda s: s.start_time > now, venue.shows))
      data.append(
          {"id": venue.id,
           "name": venue.name,
           "num_upcoming_shows": len(shows)
              }
          )
  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
 
  venues = Venue.query.all()
  venue = list(filter(lambda d: d.id == venue_id, venues))[0]
  allShows = venue.shows
  now = now = datetime.now()
  pastShows = []
  upcomingShows = []
  for s in allShows:
      showItem = {
              "artist_id": s.artist_id,
              "artist_name": s.artist.name,
              "artist_image_link": s.artist.image_link,
              "start_time": s.start_time.strftime("%Y-%m-%d %H:%M:%S")
              }
      if s.start_time > now:
          upcomingShows.append(showItem)
      else:
          pastShows.append(showItem)
          
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split("|"),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": pastShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows)
    }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  spliter="|"
  genres = spliter.join(request.form.getlist('genres'))
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_talent = request.form.get('seeking_talent')
  isSeekingTalent = seeking_talent.lower() in ("yes", "true", "t", "1", "y")
  seeking_description = request.form.get('seeking_description')
  venue = Venue(
      name = name,
      city = city,
      state = state,
      address = address,
      phone = phone,
      genres = genres,
      facebook_link = facebook_link,
      image_link = image_link,
      website_link = website_link,
      seeking_talent = isSeekingTalent,
      seeking_description = seeking_description
      )
  try: 
      db.session.add(venue)
      db.session.commit()
  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as error:
      print(str(error.orig) + " for parameters" + str(error.params))
      db.session.rollback()
      flash('Error: Venue ' + request.form['name'] + ' could not be listed!')
  finally:
      db.session.close()
 
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
  except Exception as error:
      print(str(error.orig) + " for parameters" + str(error.params))
      db.session.rollback()
  finally:
      db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():  
  searchString = request.form.get('search_term')
  data = Artist.query.filter(Artist.name.contains(searchString)).all()
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artists = Artist.query.all()

  artist = list(filter(lambda d: d.id == artist_id, artists))[0]
  allShows = artist.shows
  now = now = datetime.now()
  pastShows = []
  upcomingShows = []
  for s in allShows:
      showItem = {
              "venue_id": s.venue_id,
              "venue_name": s.venue.name,
              "venue_image_link": s.venue.image_link,
              "start_time": s.start_time.strftime("%Y-%m-%d %H:%M:%S")
              }
      if s.start_time > now:
          upcomingShows.append(showItem)
      else:
          pastShows.append(showItem)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split("|"),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": pastShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows)
      }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  x =artist.genres.split("|")
  genres = []
  for a in x:
      genres.append(a)
  form.genres.data = x
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.checked = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  spliter="|"
  genres = spliter.join(request.form.getlist('genres'))
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  seeking_venue = request.form.get('seeking_venue')
  isSeekingVenue = seeking_venue.lower() in ("yes", "true", "t", "1", "y")
  
  website_link = request.form.get('website_link')
  seeking_description = request.form.get('seeking_description')
  artist = Artist.query.get(artist_id)

  artist.name = name
  artist.city = city
  artist.state = state
  artist.phone= phone
  artist.genres = genres
  artist.facebook_link = facebook_link
  artist.image_link = image_link
  artist.seeking_venue = isSeekingVenue
  artist.website_link = website_link
  artist.seeking_description = seeking_description
      
  try: 
      db.session.commit()
  # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully updated!')  # TODO: on unsuccessful db insert, flash an error instead.
  except Exception as error:
      print(str(error.orig) + " for parameters" + str(error.params))
      db.session.rollback()
      flash('Error: Artist ' + request.form['name'] + ' could not be updated!')
  finally:
      db.session.close()
  
  
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres.split("|")
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_description.data = venue.seeking_description
  form.seeking_talent.data = venue.seeking_talent
  form.image_link.data = venue.image_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue= Venue.query.get(venue_id)
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  spliter="|"
  genres = spliter.join(request.form.getlist('genres'))
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  seeking_talent = request.form.get('seeking_talent')
  isSeekingTalent = seeking_talent.lower() in ("yes", "true", "t", "1",  "y")
  
  website_link = request.form.get('website_link')
  seeking_description = request.form.get('seeking_description')

  venue.name = name
  venue.city = city
  venue.state = state
  venue.phone= phone
  venue.genres = genres
  venue.facebook_link = facebook_link
  venue.image_link = image_link
  venue.seeking_talent = isSeekingTalent
  venue.website_link = website_link
  venue.seeking_description = seeking_description
      
  try: 
      db.session.commit()
  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully updated!')  # TODO: on unsuccessful db insert, flash an error instead.
  except Exception as error:
      print(str(error.orig) + " for parameters" + str(error.params))
      db.session.rollback()
      flash('Error: Venue ' + request.form['name'] + ' could not be updated!')
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
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  spliter="|"
  genres = spliter.join(request.form.getlist('genres'))
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  seeking_venue = request.form.get('seeking_venue')
  isSeekingVenue = seeking_venue.lower() in ("yes", "true", "t", "1", "y")
  
  website_link = request.form.get('website_link')
  seeking_description = request.form.get('seeking_description')
  artist = Artist(
      name = name,
      city = city,
      state = state,
      phone = phone,
      genres = genres,
      facebook_link = facebook_link,
      image_link = image_link,
      seeking_venue = isSeekingVenue,
      website_link = website_link,
      seeking_description = seeking_description
      )
  try: 
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')  # TODO: on unsuccessful db insert, flash an error instead.
  except Exception as error:
      print(str(error.orig) + " for parameters" + str(error.params))
      db.session.rollback()
      flash('Error: Artist ' + request.form['name'] + ' could not be listed!')
  finally:
      db.session.close()
 return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  allShows = Show.query.all() 
  data = []
  for show in allShows: 
      data.append(
          {
              "venue_id": show.venue_id,
              "venue_name": show.venue.name,
              "artist_id": show.artist_id,
              "artist_name": show.artist.name,
              "artist_image_link": show.artist.image_link,
              "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")              
              }
          )
      
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  artistId = request.form.get('artist_id')
  venueId = request.form.get('venue_id')
  time = request.form.get('start_time')
  startTime = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
  show = Show(
      artist_id = artistId,
      venue_id = venueId,
      start_time = startTime
      )
  try :
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
  # on successful db insert, flash success
  except Exception as error:
      print(str(error.orig) + " for parameters" + str(error.params))
      db.session.rollback()
      flash('Error: Show ' + request.form['name'] + ' could not be listed!')
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
