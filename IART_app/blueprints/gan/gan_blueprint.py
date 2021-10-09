"""
The "gan" blueprint handles neural style transfer.
"""
import os
from matplotlib.pyplot import get 
import torch
#from app import app
from flask import current_app 
from flask import request, Blueprint,  flash , redirect, url_for #flash for message flashing;  url_for dynamic url
from flask import render_template, send_from_directory
from werkzeug.utils import secure_filename
import time
from project.models_db import PAINTING, ARTIST
from build_app import db
from blueprints.gan.gan_models import Genre_classes, Artist_classes, run_gan, get_key

gan_blueprint = Blueprint(name='gan',  import_name=__name__, template_folder=None)

DIR= os.path.dirname(os.path.abspath(__file__))
abs_portrait_DIR = os.path.join(DIR,'..','..','static','artists')
abs_genre_DIR = os.path.join(DIR,'..','..','static','genres')
selected_genre = ''
selected_style = ''
label=''
OUTPUT_FOLDER = os.path.join(DIR,'gallery')

@gan_blueprint.route('/gan/', methods=['GET','POST'])
def home():
  URI = current_app.config['SQLALCHEMY_DATABASE_URI']
  # Read artist from db
  artists = db.session.query(ARTIST.Name).all()
  artists =  sorted([r[0] for r in artists])
  artist_portrait_filenames =  [r.lower().replace(' ','-')+'-Portrait.jpg' for r in artists]
  artist_portrait_paths = [os.path.join(abs_portrait_DIR ,filename) for filename in artist_portrait_filenames]
  artist_portraits = sorted([os.path.basename(path)  for path in artist_portrait_paths  if os.path.exists(path) ])
  artist_names = [artist.replace('-Portrait.jpg','').replace('-',' ').title().split(' ')[-1] for artist in artist_portraits]
  artist_names= map(lambda x: x if x != 'Gogh' else 'Van Gogh', artist_names)
  # artist_names = sorted([ portrait.split('-Portrait.jpg')[0].replace('-',' ').capitalize() for portrait  in artist_portraits])
  return render_template('gan_home.html', by='by_artist', data = list(zip(artist_portraits, artist_names, range(len(artist_portraits)) )) )


@gan_blueprint.route('/gan/index', methods=['GET','POST'])
def index():
    if request.form['options'] == 'Artist':
        URI = current_app.config['SQLALCHEMY_DATABASE_URI']
        # Read artist from db
        artists = db.session.query(ARTIST.Name).all()
        artists =  sorted([r[0] for r in artists])
        artist_portrait_filenames =  [r.lower().replace(' ','-')+'-Portrait.jpg' for r in artists]
        artist_portrait_paths = [os.path.join(abs_portrait_DIR ,filename) for filename in artist_portrait_filenames]
        artist_portraits = sorted([os.path.basename(path)  for path in artist_portrait_paths  if os.path.exists(path) ])
        artist_names = [artist.replace('-Portrait.jpg','').replace('-',' ').title().split(' ')[-1] for artist in artist_portraits]
        artist_names= map(lambda x: x if x != 'Gogh' else 'Van Gogh', artist_names)
        # artist_names = sorted([ portrait.split('-Portrait.jpg')[0].replace('-',' ').capitalize() for portrait  in artist_portraits])
        return render_template('gan_artist_index.html', by='by_artist', data = list(zip(artist_portraits, artist_names, range(len(artist_portraits)) )) )

    if request.form['options'] == 'Genre':
        genres = list(Genre_classes.keys())
        genre_filenames  = [g.lower().replace(' ','_')+'.jpg' for g in genres]
        genre_img_paths = [os.path.join(abs_genre_DIR ,filename) for filename in genre_filenames]
        genre_names =  [g.title().replace('Painting','').replace('(Nu)','') for g in genres]
        return render_template('gan_genre_index.html', by='by_genre', data = list(zip(genre_filenames, genre_names, range(len(genre_img_paths)) )) )



# @gan_blueprint.route('/gan/genre', methods=['GET','POST'])
# def by_genre_index():
#   genres = list(Genre_classes.keys())
#   genre_filenames  = [g.lower().replace(' ','_')+'.jpg' for g in genres]
#   genre_img_paths = [os.path.join(abs_genre_DIR ,filename) for filename in genre_filenames]
#   genre_names =  [g.title().replace('Painting','').replace('(Nu)','') for g in genres]
#   return render_template('gan_genre_index.html', by='by_genre', data = list(zip(genre_filenames, genre_names, range(len(genre_img_paths)) )) )


@gan_blueprint.route('/gan/gallery/<by_genre_or_artist>/<filename>', methods = ['GET', 'POST']) # <filename> is a variable here content or style
def send_output_image(by_genre_or_artist,filename):
	return send_from_directory(os.path.join(OUTPUT_FOLDER, by_genre_or_artist), filename)

@gan_blueprint.route('/gan/<by_genre_or_artist>', methods=['POST'])
def generate_fake(by_genre_or_artist):
  if request.method=='POST':
      if by_genre_or_artist == "by_genre":
        selected_genre = request.form.get('genre')
        label = selected_genre 
        classe = get_key(Genre_classes,int(label))
      if by_genre_or_artist == "by_artist":
        selected_artist = request.form.get('artist')
        label = selected_artist
        classe = get_key(Artist_classes,int(label))
      print('label:',label)
      output_dir = os.path.join(OUTPUT_FOLDER, by_genre_or_artist)
      outputs = []
      number_of_generated_imgs = 4
      for i in range(number_of_generated_imgs):
        output_filename = run_gan(int(label), output_dir=output_dir, by=by_genre_or_artist)
        outputs.append(output_filename)
        print(f'Output Filename: {output_filename}')
      return render_template(f'gan_results.html',by=by_genre_or_artist, output_images=outputs, classe=classe)

