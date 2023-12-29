#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
import sys
from sqlalchemy import func
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database - done
# updated the details in config.py file

# defining migrate
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Models are updated in models.py file


# creating table based on above models
# with app.app_context():
#     db.create_all()

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
  # TODO: replace with real venues data. - done
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  all_venues = Venue.query.with_entities(
     func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []
  for location in all_venues:
    venue_locations = Venue.query.filter_by(state=location.state).filter_by(city=location.city).all()
    venue_details = []
    num_upcoming_shows = db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all()
    for venue in venue_locations:
      venue_details.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": len(num_upcoming_shows)
      })
    data.append({
      "city": location.city,
      "state": location.state, 
      "venues": venue_details
    })

  '''data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]'''
  return render_template('pages/venues.html', areas=data);



@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. - done
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_text = request.form.get('search_term')
  search_results = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_text))).all()
  data = []
  for venue in search_results:
    num_upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(num_upcoming_shows),
    })  
  response={
    "count": len(search_results),
    "data": data
  }
  '''response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }'''
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id - done
  venue = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []
  current_time = datetime.now()
  upcoming_shows_data = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>current_time).all()
  past_shows_data = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<current_time).all()
  for past_show in past_shows_data:
     past_shows.append({
      "artist_id": past_show.artist_id,
      "artist_name": past_show.Artist.name,
      "artist_image_link": past_show.Artist.image_link,
      "start_time": str(past_show.start_time)
     })
  
  for upcoming_show in upcoming_shows_data:
     upcoming_shows.append({
        "artist_id": upcoming_show.artist_id,
        "artist_name": upcoming_show.Artist.name,
        "artist_image_link": upcoming_show.Artist.image_link,
        "start_time": str(upcoming_show.start_time)
     })

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
     "past_shows": past_shows,
     "upcoming_shows": upcoming_shows,
     "past_shows_count": len(past_shows),
     "upcoming_shows_count": len(upcoming_shows)
  }
  '''data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]'''
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead - done
  # TODO: modify data to be the data object returned from db insertion - done
  new_venue = Venue()
  new_venue.name = request.form.get('name')
  new_venue.city = request.form.get('city')
  new_venue.state = request.form.get('state')
  new_venue.address = request.form.get('address')
  new_venue.phone = request.form.get('phone')
  new_venue.genres = request.form.getlist('genres')
  new_venue.facebook_link = request.form.get('facebook_link')
  new_venue.image_link = request.form.get('image_link')  
  new_venue.website = request.form.get('website_link')
  new_venue.seeking_talent = True if 'seeking_talent' in request.form else False
  new_venue.seeking_description = request.form.get('seeking_description')
  error = False
  try:
     db.session.add(new_venue)
     db.session.commit()
     # on successful db insert, flash success
     flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
     db.session.rollback()
     print(sys.exc_info())
     error = True
  finally:
     db.session.close()  
  if error:
     # TODO: on unsuccessful db insert, flash an error instead. - done
     # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
     # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
     flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using- done
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
     venue = Venue.query.get(venue_id)
     db.session.delete(venue)
     db.session.commit()
     flash('Venue ' + venue + ' deleted successfully!')
  except:
     db.session.rollback()
     print(sys.exc_info())
     error = True
  finally:
     db.session.close()
  if error:
     flash('An error occurred. Venue ' + venue +' could not be deleted.')
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database - done
  data = Artist.query.all()
  '''data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]'''
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. - done
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_text = request.form.get('search_term')
  search_results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_text))).all()
  data = []
  for artist in search_results:
    num_upcoming_shows = db.session.query(Artist).filter(Artist.name.ilike('%{}%'.format(search_text))).all()
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(num_upcoming_shows),
    })  
  response={
    "count": len(search_results),
    "data": data
  }
  '''response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }'''
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id - done
  artist = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []
  current_time = datetime.now()
  upcoming_shows_data = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>current_time).all()
  past_shows_data = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<current_time).all()
  for past_show in past_shows_data:
     past_shows.append({
      "venue_id": past_show.venue_id,
      "venue_name": past_show.Venue.name,
      "venue_image_link": past_show.Venue.image_link,
      "start_time": str(past_show.start_time)
     })
  for upcoming_show in upcoming_shows_data:
     upcoming_shows.append({
        "venue_id": upcoming_show.artist_id,
        "venue_name": upcoming_show.Venue.name,
        "venue_image_link": upcoming_show.Venue.image_link,
        "start_time": str(upcoming_show.start_time)
     })
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
     "past_shows": past_shows,
     "upcoming_shows": upcoming_shows,
     "past_shows_count": len(past_shows),
     "upcoming_shows_count": len(upcoming_shows)
  }

  '''data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]'''
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  '''artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }'''
  # TODO: populate form with fields from artist with ID <artist_id> - done
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  artist.name= request.form.get('name')
  artist.genres= request.form.get('genres')
  artist.city= request.form.get('city')
  artist.state= request.form.get('state')
  artist.website= request.form.get('website_link')
  artist.facebook_link= request.form.get('facebook_link')
  artist.seeking_venue= True if 'seeking_venue' in request.form else False
  artist.seeking_description= request.form.get('seeking_description')
  artist.image_link= request.form.get('image_link')
  error = False
  try:
     db.session.commit()
     flash('Artist ' + artist.name + ' updated successfully.')
  except:
     db.session.rollback()
     print(sys.exc_info()) 
     error = True
  finally:
     db.session.close()
  if error:
     flash('An error occurred. Artist ' + artist.name +' could not be updated.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  '''venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }'''
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)

  venue.name= request.form.get('name')
  venue.genres= request.form.get('genres')
  venue.address= request.form.get('address')
  venue.city= request.form.get('city')
  venue.state= request.form.get('state')
  venue.phone= request.form.get('phone')
  venue.website= request.form.get('website_link')
  venue.facebook_link= request.form.get('facebook_link')
  venue.seeking_venue= True if 'seeking_venue' in request.form else False
  venue.seeking_description= request.form.get('seeking_description')
  venue.image_link= request.form.get('image_link')
  print('request.form.get("name"): '+ request.form.get('name'))
  error = False
  try:
     db.session.commit()
     flash('Venue ' + venue.name + ' updated successfully.')
  except:
     db.session.rollback()
     print(sys.exc_info()) 
     error = True
  finally:
     db.session.close()
  if error:
     flash('An error occurred. Venue ' + venue.name +' could not be updated.')
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead - done
  # TODO: modify data to be the data object returned from db insertion - done
  new_artist = Artist()
  new_artist.name = request.form.get('name')
  new_artist.city = request.form.get('city')
  new_artist.state = request.form.get('state')
  new_artist.phone = request.form.get('phone')
  new_artist.genres = request.form.getlist('genres')
  new_artist.facebook_link = request.form.get('facebook_link')
  new_artist.image_link = request.form.get('image_link')
  new_artist.website = request.form.get('website_link')
  new_artist.seeking_venue = True if 'seeking_venue' in request.form else False
  new_artist.seeking_description = request.form.get('seeking_description')
  error = False  
  try:
     db.session.add(new_artist)
     db.session.commit()
     # on successful db insert, flash success
     flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
     db.session.rollback()
     print(sys.exc_info())
     error = True
  finally:
     db.session.close()
  if error:
     # TODO: on unsuccessful db insert, flash an error instead. - done
     # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
     flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')  
  return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data. - done
  all_show = Show.query.all()
  data = []
  for show in all_show:
     artist = Artist.query.get(show.artist_id)
     venue = Venue.query.get(show.venue_id)
     if (show.upcoming_show):
        data.append({
           "venue_id": show.venue_id,
           "venue_name": venue.name,
           "artist_id": show.artist_id,
           "artist_name": artist.name,
           "artist_image_link": artist.image_link,
           "start_time": str(show.start_time)           
        })
  '''data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]'''
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead -- done
  new_show = Show()
  new_show.artist_id = request.form.get('artist_id')
  new_show.venue_id = request.form.get('venue_id')
  new_show.start_time = request.form.get('start_time')
  error = False
  try:
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
     db.session.close()  
  if error: 
    # TODO: on unsuccessful db insert, flash an error instead. -- done
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ 
    flash('An error occurred. Show could not be listed.')
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
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)