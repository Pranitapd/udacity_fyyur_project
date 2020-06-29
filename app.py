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
from babel.dates import get_timezone
from sqlalchemy.types import DateTime
#from datetime import datetime, date , tzinfo, timedelta, time
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database
SQLALCHEMY_DATABASE_URI = 'postgres://postgres:Pranita123@localhost:5432/fyyur'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String)
    seeking_description = db.Column(db.String(1000))
    website = db.Column(db.String(500))
    venue_shows = db.relationship('Show',backref='some_venue')
    genre = db.relationship('Venue_genre',backref='some_genre_venue')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String)
    seeking_description = db.Column(db.String(1000))
    website = db.Column(db.String(500))
    artist_shows = db.relationship('Show',backref='artist_shows')
    genre = db.relationship('Genre',backref='some_genre_artist')
    avail_time = db.relationship('Artist_available_time', backref = "avail_time")

class Genre(db.Model):
  __tablename__ = 'Genre'
  id = db.Column(db.Integer, primary_key=True)
  genre = db.Column(db.String)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)

class Venue_genre(db.Model):
  __tablename__ = 'Venue_genre'
  id = db.Column(db.Integer, primary_key=True)
  genre = db.Column(db.String)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable = False)

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
  start_time = db.Column(db.DateTime,nullable=False)

class Artist_available_time(db.Model):
  __tablename__ = "Artist_available_time"
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
  available_time = db.Column(db.DateTime,nullable=False)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  data = []
  data1= []
  # Showing Recent added artists and venues on home page.
  # Since We are adding both using web we cannot add their ID'd manually
  # so,Id's will be in the increasing number. Last item will have the highest ID.
  arts = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  for a in arts:
    artists = {
    "name" : a.name,
    }
    data.append(artists)

  vens = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  for a in vens:
    venues = {
    "name" : a.name,
  }
    data1.append(venues)
  return render_template('pages/home.html',artists=data,venues=data1)

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues') #done
def venues():
  # TODO: replace with real venues data.
  areas = Venue.query.distinct('city','state').all() #selecting two columns city and state
  data = []
  for area in areas:
    ve = Venue.query.filter(Venue.city == area.city , Venue.state == area.state).all()
   
    ven =[]
    for row in ve:
      rec ={
        "id" : row.id,
        "name" : row.name,
        "num_upcoming_shows": 0,
      }
      ven.append(rec)          

    record = {
      "city" :  area.city,
      "state" : area.state,
      "venues" : [ v for v in ve ],
    }
    data.append(record)
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template("pages/venues.html", areas=data);

@app.route('/venues/search', methods=['POST']) #done
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_term = request.form.get('search_term', '')
  if ',' in search_term: #for searching by city,state
    new = [x.strip() for x in search_term.split(',')]
    city = new[0]
    state = new[1]
    ve = Venue.query.filter(Venue.city == city).filter(Venue.state == state).all()
  else:
    ve = Venue.query.filter(Venue.name.ilike("%{}%".format(search_term))).all()

  response = []
  rec = []
  for row in ve:
    re = {
    "id" : row.id,
    "name" : row.name,
    "num_upcoming_shows": 0,
    }
    rec.append(re)

  response = {
      "count" : len(ve),
      "data" : [ v for v in rec],
    }
  
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template("pages/search_venues.html", results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>') #done
def show_venue(venue_id):
  # TODO: replace with real venue data from the venues table, using venue_id
  
  entry = Venue.query.get(venue_id)
  past_shows =[]
  upcoming_shows = []
  v = Show.query.filter(Show.venue_id == entry.id).all() #to get artist data associated with this venue

  for show in v:
    art = Artist.query.get(show.artist_id)
    show_data = {
		"artist_id": show.artist_id,
		"artist_name": art.name,
		"artist_image_link": art.image_link,
		"start_time": str(show.start_time),
		}
    if show.start_time < datetime.now():
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)
  
  gens = []
  gen = Venue_genre.query.filter(Venue_genre.venue_id == venue_id)
  for g in gen:
    gens.append(g.genre)

  data = {
    "id" : entry.id,
    "name" : entry.name,
    "genres": gens,
    "address" : entry.address,
    "city" : entry.city,
    "state" : entry.state,
    "phone" : entry.phone,
    "website" : entry.website,
    "facebook_link" : entry.facebook_link,
    "seeking_talent" : entry.seeking_talent,
    "seeking_description" : entry.seeking_description,  
    "image_link" : entry.image_link,
    "past_shows" : [a for a in past_shows ],
    "upcoming_shows" : [ a for a in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count" : len(upcoming_shows),
    }

  #Pra 
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST']) #done
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    genres = []
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    gen1 = request.form.get('genres')
    genres.append(gen1)
    facebook_link = request.form.get('facebook_link')

    venue = Venue(name=name,city=city,state=state,address=address,phone=phone,facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()

    venue = Venue.query.get(venue.id)

    for gen in genres:
      g1 = Venue_genre(genre = gen)
      venue.genre.append(g1)
      db.session.add(venue)
      db.session.commit()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE']) 
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists') #done
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  arts = Artist.query.all()

  for a in arts:
    data1 = {
    "id" : a.id,
    "name" : a.name,
    }
    data.append(data1)
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST']) #done
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  search_term = request.form.get('search_term', '')
  if ',' in search_term: #for searching by city,state
    new = [x.strip() for x in search_term.split(',')]
    city = new[0]
    state = new[1]
    ve = Artist.query.filter(Artist.city == city).filter(Artist.state == state).all()
  else:
    ve = Artist.query.filter(Artist.name.ilike("%{}%".format(search_term))).all()
  response = []
  rec = []
  for row in ve:
    re = {
    "id" : row.id,
    "name" : row.name,
    "num_upcoming_shows": 0,
    }
    rec.append(re)

  response = {
      "count" : len(ve),
      "data" : [ v for v in rec],
    }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>') 
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  entry = Artist.query.get(artist_id)
  past_shows=[]
  upcoming_shows = []
  v = Show.query.filter(Show.artist_id == entry.id).all() #To find the venue dataassociated with this artist

  for show in v:
    venue = Venue.query.get(show.venue_id)
    show_data = {
		"venue_id": show.venue_id,
		"venue_name": venue.name,
		"venue_image_link": venue.image_link,
		"start_time": str(show.start_time)
		}
    if show.start_time < datetime.now():
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)

  time = []
  t = Artist_available_time.query.filter(Artist_available_time.artist_id == artist_id)
  for tis in t:
    time.append(tis.available_time)
    
  gen1 = []
  gen = Genre.query.filter(Genre.artist_id == entry.id)
  for g in gen:
    gen1.append(g.genre)

  data = {
    "id" : entry.id,
    "name" : entry.name,
    "genres" : gen1,
    "city" : entry.city,
    "state" : entry.state,
    "phone" : entry.phone,
    "website" : entry.website,
    "facebook_link" : entry.facebook_link,
    "seeking_venue" : entry.seeking_venue,
    "seeking_description" : entry.seeking_description,  
    "image_link" : entry.image_link,
    "past_shows" : [ a for a in past_shows ],
    "upcoming_shows" : [ a for a in upcoming_shows ],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count" : len(upcoming_shows),
    "avail_time" : time,
    }
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET']) 
def edit_artist(artist_id):
  form = ArtistForm()

  a = Artist.query.get(artist_id)

  gen = []
  g = Genre.query.filter(Genre.artist_id == artist_id)
  for gs in g:
    gen.append(gs.genre)

  artist = {
    "id" : a.id,
    "name" : a.name,
    "genres" : gen,
    "city" : a.city,
    "state" : a.state,
    "phone" : a.phone,
    "website" : a.website,
    "facebook_link" : a.facebook_link,
    "seeking_venue" : a.seeking_venue,
    "seeking_description" : a.seeking_description,
    "image_link" : a.image_link,
  }

  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST']) 
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  a = Artist.query.get(artist_id)
  a.name = request.form.get('name')
  a.city = request.form.get('city')
  a.state = request.form.get('state')
  a.phone = request.form.get('phone')
  a.seeking_venue = request.form.get('seeking_venue')
  a.seeking_description = request.form.get('seeking_description')
  a.image_link = request.form.get('image_link')
  a.website = request.form.get('website')
  a.facebook_link = request.form.get('facebook_link')

  #To edit genres table for the artist
  genres = []
  gen = request.form.get('genres')
  genres.append(gen)
  for g in genres:
    ges = Genre(genre = g)
    a.genre.append(ges)
    db.session.add(a)
    db.session.commit()

  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  entry =  Venue.query.get(venue_id)

  genres = []
  gen = Venue_genre.query.filter(Venue_genre.venue_id == venue_id)
  for g in gen:
    genres.append(g.genre)

  venue = {
  "id" : entry.id,
  "name" : entry.name,
  "genres" : genres,
  "address" : entry.address,
  "city" : entry.city,
  "state" : entry.state,
  "phone" : entry.phone,
  "website" : entry.website,
  "facebook_link" : entry.facebook_link,
  "seeking_talent" : entry.seeking_talent,
  "seeking_description" : entry.seeking_description,  
  "image_link" : entry.image_link,
  }
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST']) 
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  a = Venue.query.get(venue_id)
  a.name = request.form.get('name')
  a.city = request.form.get('city')
  a.state = request.form.get('state')
  a.phone = request.form.get('phone')
  a.seeking_talent = request.form.get('seeking_talent')
  a.seeking_description = request.form.get('seeking_description')
  a.image_link = request.form.get('image_link')
  a.website = request.form.get('website')
  a.facebook_link = request.form.get('facebook_link')
  db.session.commit()

  #To edit genres table for venue
  genres = []
  gen = request.form.get('genres')
  genres.append(gen)
  for g in genres:
    new = Venue_genre(genre = g)
    a.genre.append(new)
    db.session.add(a)
    db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST']) #done
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
  # on successful db insert, flash success
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    facebook_link = request.form.get('facebook_link')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')
    image_link = request.form.get('image_link')
    website = request.form.get('website')

    artist1 = Artist(name=name,city=city,state=state,phone=phone,facebook_link=facebook_link)
    db.session.add(artist1)
    db.session.commit()

    genres = []
    gen = request.form.get('genres')
    genres.append(gen)
    for g in genres:
      new = Genre(genre = g)
      artist1.genre.append(new)
      db.session.add(artist1)
      db.session.commit()      

    avail_time = []
    time = request.form.get('available_time')

    if ',' in time:
      imp = [i for i in time.split(',')]
      for x in imp:
        avail_time.append(x)

    for t in avail_time:
      new = Artist_available_time(available_time = t)
      artist1.avail_time.append(new)
      db.session.add(artist1)
      db.session.commit()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist1.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows') #done
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []

  show = Show.query.all()
  for a in show:
    venue = Venue.query.get(a.venue_id)
    artist = Artist.query.get(a.artist_id)
    data1 = {
      "venue_id" : a.venue_id, 
      "venue_name" : venue.name,
      "artist_id" : a.artist_id,
      "artist_name" : artist.name,
      "artist_image_link" : artist.image_link,
      "start_time" : str(a.start_time),
    }
    data.append(data1)

  
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST']) #done
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')

    avail_time = Artist_available_time.query.filter(Artist_available_time.available_time == start_time).filter(Artist_available_time.artist_id == artist_id).all()
 
    a = Artist.query.get(artist_id)
    if avail_time:
      show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
    else:
      flash('Show cannot be created. Artist is not available.Check availability for Artist name {0}'.format(a.name))
  except:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
  #   flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/shows/search', methods=['POST']) #extra
def search_shows():
  search_term = request.form.get('search_term', '')
  art = Artist.query.filter(Artist.name.ilike("%{}%".format(search_term))).all()
  ven = Venue.query.filter(Venue.name.ilike("%{}%".format(search_term))).all()

  data = []
  total =[]
  data1 = []

  for a in art:
    show = Show.query.filter(Show.artist_id == a.id).all()
    #i think need to add a for loop
    for s in show:
      if s.id in total:
        continue
      else:
        total.append(s.id) 
        artist = Artist.query.get(a.id)
        venue = Venue.query.get(s.venue_id)
        data1 = {
          "artist_name" : artist.name,
          "venue_name" : venue.name,
          "start_time" : s.start_time,
        }
        data.append(data1)

  for v in ven:
    show = Show.query.filter(Show.venue_id == v.id).all()
    for s in show:
      if s.id in total:
        continue
      else:
        total.append(s.id)
        artist = Artist.query.get(s.artist_id)
        venue = Venue.query.get(v.id)
        data1 = {
        "artist_name" : artist.name,
        "venue_name" : venue.name,
        "start_time" : s.start_time,
        }
        data.append(data1)

  result = {
  "count" : len(data),
  "data" : [d for d in data],
  }
    
  return render_template('pages/show.html', results=result, search_term=request.form.get('search_term', ''))


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
