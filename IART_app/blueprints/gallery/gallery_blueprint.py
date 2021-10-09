"""
The "gallery" blueprint handles displaying paintings.
"""
from flask import Blueprint
from flask import render_template, abort
import os
from flask import current_app 
from flask import request, Blueprint,  flash , redirect, url_for #flash for message flashing;  url_for dynamic url
from flask import render_template, send_from_directory
from werkzeug.utils import secure_filename
import time
from glob import iglob
from project.models_db import PAINTING, ARTIST
from build_app import db
from blueprints.gan.gan_models import Genre_classes, Artist_classes, run_gan, get_key


gallery_blueprint = Blueprint(name='gallery', import_name=__name__, template_folder=None)


DIR= os.path.dirname(os.path.abspath(__file__))
abs_portrait_DIR = os.path.join(DIR,'..','..','static','artists')
abs_genre_DIR = os.path.join(DIR,'..','..','static','genres')
ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif']
data_DIR=os.path.join(DIR,'..','..','static','Data')


def join_tuple_string(strings_tuple) -> str:
   return '/'.join(strings_tuple)

@gallery_blueprint.route('/gallery/', methods=['GET','POST'])
def home():
    return render_template('gallery_home.html')


@gallery_blueprint.route('/gallery/index', methods=['GET','POST'])
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
        return render_template('gallery_artist_index.html', by='by_artist', data = list(zip(artist_portraits, artist_names, range(len(artist_portraits)) )) )

    if request.form['options'] == 'Genre':
        genres = list(Genre_classes.keys())
        genre_filenames  = [g.lower().replace(' ','_')+'.jpg' for g in genres]
        genre_img_paths = [os.path.join(abs_genre_DIR ,filename) for filename in genre_filenames]
        genre_names =  [g.title().replace('Painting','').replace('(Nu)','') for g in genres]
        return render_template('gallery_genre_index.html', by='by_genre', data = list(zip(genre_filenames, genre_names, range(len(genre_img_paths)) )) )



@gallery_blueprint.route('/gallery/<by_genre_or_artist>', methods=['POST','GET'])
def show_gallery(by_genre_or_artist):
  if request.method=='POST':
    if by_genre_or_artist == "by_genre":
        selected_genre = request.form.get('genre')
        label = selected_genre 
        classe = get_key(Genre_classes,int(label))
        #print('classe', classe)
        # -- select file by genre 
        query_results = db.session.query(PAINTING.Artist,PAINTING.Filename).filter_by(Genre=classe).all() # list of tuples (artist,painting)
        # -- put artist name in the correct format corresponding to folder name
        query_results =  [(x[0].lower().replace(' ','-'), x[1]) for x in query_results]
        #paintings, artists = list(list(zip(*query_results))[0]), list(list(zip(*query_results))[1])
        # join artist folder namer and paintings filename to create part of the image path
        results= list(map(join_tuple_string, query_results))
        #print(results)
        images = [img for result in results for img in iglob(data_DIR+'/'+result+'*') if os.path.splitext(img)[1] in ALLOWED_EXTENSIONS]
        images = [img.split(data_DIR+'/')[1] for img in images] # remove data_DIR from path to be able to use send from directory 

    if by_genre_or_artist == "by_artist":
        selected_artist = request.form.get('artist')
        label = selected_artist
        classe = get_key(Artist_classes,int(label))
        #print('classe', classe)
        artist_folder = classe.lower().replace(' ','-')
        # print('artist folder',artist_folder)
        # print('data_DIR',data_DIR)
        images = [img for img in iglob(os.path.join(data_DIR,artist_folder)+'/*') if os.path.splitext(img)[1] in ALLOWED_EXTENSIONS]
        images = [img.split(data_DIR+'/')[1] for img in images]
    path = [os.path.join(data_DIR,filename) for filename in images]
    #print('path',path)
    return render_template('gallery_result.html',by=by_genre_or_artist, classe=classe, images=images)



@gallery_blueprint.route('/gallery/<filename>',methods = ['GET', 'POST'])
def send_image(filename):
    """
    attention absolute path ça marche pas https://stackoverflow.com/questions/5157772/src-absolute-path-problem
    ou alors pb de slash 
    """
    print(filename)
    return send_from_directory(data_DIR,filename)