import os 
from glob import iglob
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.utils import open_json_file

"""
This file contents usefull dictionnaries about artists for scraping   
as well as some classes to facilate structuraiton and retrieving of 
artist and painting information.
"""

# =============================================================================
# Related Artist dictionnaries 
# =============================================================================

artist_dict = {
    # "Vincent Van Gogh": {"Naturalism","Impressionnism","Expressionism"},
    "Joseph Mallord William Turner": {"Romanticism"},
    # "Katsushika Hokusai":{"Ukiyo-e"},
    # "Zdzislaw Beksinski":{"Surrealism", "Magic-Realism","Avant-garde"},
    # "Claude Monet": {"Impressionism"},
    "Arnold Bocklin": {"Symbolism"},
    # "Piet Mondrian":{"Neo-impressionnisme","De Stijl"},
    # "Edward Hopper": {"New-Realism"},
    # "Henri Rousseau": {"Primitivism"},
    # "Vassily Kandinsky": {"Abstract-Art"},
    # "Gustav Klimt": {"Symbolism", "Art-nouveau"},
    # "Sandro Botticelli" :{"Renaissance"},
    # "Artemisia Gentileschi":{"Baroque"},
    # "Pablo Picasso":{"Cubism"},
    # "Henri Matisse": {"Impressionnism"},
    # "Pierre Auguste Renoir":{"Impressionism"},
    # "Theophile Steinlen" : {"Art-nouveau"},
    # "David Burliuk" : {"Futurism"},
    # "Salvador Dali": {"Surrealisme"},
    # "John James Audubon" :{"Naturalism"},
    # "Ernst Ludwig Kirchner" :{'Expressionism'},
    # "Rembrandt" : {"Baroque"},
    # "Amedeo Modigliani" :{"Expressionism"},
    # "Caspar David Friedrich": {"Romanticism"},
    }


artist_nationality_dict = {
    "Vincent Van Gogh": "Dutch" ,
    "Joseph Mallord William Turner": "English",
    "Katsushika Hokusai": "Japanese",
    "Zdzislaw Beksinski": "Polish",
    "Claude Monet": "French",
    "Arnold Bocklin":"Swiss",
    "Piet Mondrian": "Dutch",
    "Edward Hopper": "American",
    "Henri Rousseau": "French",
    "Vassily Kandinsky": "Russian" ,
    "Gustav Klimt": "Austrian",
    "Sandro Botticelli" : "Italian",
    "Artemisia Gentileschi":"Italian",
    "Pablo Picasso": "Spanish",
    "Henri Matisse":"French",
    "Pierre Auguste Renoir":"French",
    "Theophile Steinlen" : "Swiss",
    "David Burliuk": "Ukrainian" ,
    "Salvador Dali": "Spanich",
    "John James Audubon" : "American",
    "Ernst Ludwig Kirchner" : "German",
    "Rembrandt" : "Dutch",
    "Amedeo Modigliani" : "Italian",
    "Caspar David Friedrich" : "German",
    }

artist_count_dict = {
    "Vincent Van Gogh": 1931,
    "Joseph Mallord William Turner": 245,
    "Katsushika Hokusai": 268,
    "Zdzislaw Beksinski": 708,
    "Claude Monet": 1368,
    "Arnold Bocklin": 123,
    "Piet Mondrian": 101,
    "Edward Hopper": 182,
    "Henri Rousseau": 123,
    "Vassily Kandinsky": 226,
    "Gustav Klimt": 161,
    "Sandro Botticelli" :136,
    "Artemisia Gentileschi":21,
    "Pablo Picasso":1167,
    "Henri Matisse":1008,
    "Pierre Auguste Renoir":1412,
    "Theophile Steinlen" : 1130,
    "David Burliuk" : 402,
    "Salvador Dali": 1178,
    "John James Audubon" :186,
    "Ernst Ludwig Kirchner" :392,
    "Rembrandt" : 769,
    "Amedeo Modigliani":349,
    "Caspar David Friedrich"  :50,
    }


genre_list = ['portrait', 'landscape', 'genre-painting', 'abstract', 'religious-painting', 
              'cityscape', 'sketch-and-study', 'figurative', 'illustration', 'still-life', 
              'design', 'nude-painting-nu', 'mythological-painting', 'marina', 'animal-painting', 
              'flower-painting', 'self-portrait', 'installation', 'photo', 'allegorical-painting', 
              'history-painting', 'interior', 'literary-painting', 'poster', 'caricature', 
              'battle-painting', 'wildlife-painting', 'cloudscape', 'miniature', 'veduta', 
              'yakusha-e', 'calligraphy', 'graffiti', 'tessellation', 'capriccio', 'advertisement', 
              'bird-and-flower-painting', 'performance', 'bijinga', 'pastorale', 'trompe-loeil', 
              'vanitas', 'shan-shui', 'tapestry', 'mosaic', 'quadratura', 'panorama', 'architecture']

style_list = ['impressionism', 'realism', 'romanticism', 'expressionism', 
            'post-impressionism', 'surrealism', 'art-nouveau', 'baroque', 
            'symbolism', 'abstract-expressionism', 'naive-art-primitivism', 
            'neoclassicism', 'cubism', 'rococo', 'northern-renaissance', 
            'pop-art', 'minimalism', 'abstract-art', 'art-informel', 'ukiyo-e', 
            'conceptual-art', 'color-field-painting', 'high-renaissance',
            'mannerism-late-renaissance', 'neo-expressionism', 'early-renaissance', 
            'magic-realism', 'academicism', 'pop-art', 'lyrical-abstraction', 
            'contemporary-realism', 'art-deco', 'fauvism', 'concretism', 
            'ink-and-wash-painting', 'post-minimalism', 'social-realism', 
            'hard-edge-painting', 'neo-romanticism', 'tachisme', 'pointillism', 
            'socialist-realism', 'neo-pop-art', "de Stijl"]

# =============================================================================
# Usefull Class Objects 
# =============================================================================

class Artist(object):
    """
    Artist Object
    """
    def __init__(self, folder_path:str, label_id=None ):
        self._path = folder_path.replace('\\',r'/')
        self._label_id = label_id

    @property
    def folder_name(self):
        return os.path.basename(self._path)

    @property
    def name(self):
      return os.path.basename(self._path).replace('-',' ').title()

    @property
    def path(self):
        return self._path
    
    @property
    def painting_paths(self):
        return list(iglob(self._path + '/*.jpg'))

    @property
    def json_paths(self):
        return list(iglob(self._path + '/*.json'))

    @property
    def file_paths(self):
        return  list(iglob(self._path + '/*')) 

    @property
    def painting_titles(self):
        return [ os.path.basename(painting_path).replace('.jpg','').replace('-',' ').capitalize() for painting_path in iglob(self._path + '/*.jpg') ]

    @property
    def painting_nb(self):
      return len(list(iglob(self._path + '/*.jpg')))

    @property
    def label(self):
        # just one label_id
        if isinstance(self._label_id, int):
            return self._label_id
        # sample associated with multiple labels
        else:
            return [int(label_id) for label_id in self._label_id]
  

class Painting(object):
    """
    Painting Object
    """
    def __init__(self, painting_path:str):
        self._path = painting_path.replace('\\',r'/')
        self._json = self._path.replace('.jpg','.json')
        self._data = open_json_file(self._json)
        self._filename = os.path.basename(self._json).replace('.json','')
        self._key = list(self._data.keys())[0]

    @property
    def data(self):
      return  self._data


    @property
    def filename(self):
      return  self._filename


    @property
    def name(self):
      return  self._data[self._key]['Name']

    @property
    def date(self):
      return self._data[self._key]['Date']
  
  
    @property
    def style(self):
      return self._data[self._key]['Style']
    
    @property
    def genre(self):
      return self._data[self._key]['Genre']

        
    @property
    def tags(self):
      return self._data[self._key]['Tags']

  