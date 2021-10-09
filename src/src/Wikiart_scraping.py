# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Lucile Senicourt
# Created Date: Mon May 24 12:04:00 2021
# =============================================================================
# References : https://github.com/robbiebarrat/art-DCGAN/blob/master/genre-scraper.py
# =============================================================================
# Imports
# =============================================================================
import time
import os
import string
from glob import iglob
import random
import urllib
from unidecode import unidecode
from tqdm import tqdm
from urllib.request import urlopen, Request
import urllib.parse
import shutil
import requests
from typing import *
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.utils import MakeDir, dict_to_json, run_imap_multiprocessing, open_json_file
from utils.utils_scraping import get_user_agent
from utils.utils_data import artist_dict, artist_count_dict 

# -- log
import logging
from utils.utils_log import Log

# -- Mutliprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
from threading import Thread
import multiprocessing
import random

# =============================================================================
# Functions
# =============================================================================

def get_url_painting_list(artist:str) -> Tuple[str, list, int]:
    """
    Get all painting url's basename from the artist page 
    """
    try:
        time.sleep(4.0*random.random())  # random sleep to decrease concurrence of requests
        base_url = "https://www.wikiart.org"
        search_artist  = artist.lower().replace(' ','-')
        print(f'\n-------------- {search_artist} ------------------\n')
        artist_url = base_url + "/en/%s/all-works/text-list"%(search_artist)
        soup = BeautifulSoup(urlopen(artist_url), "lxml")
        url_painting_list = [a.get('href').split('/')[-1] for a in soup.select("li.painting-list-text-row a")]
        count = len(url_painting_list)
        print(f'Number of paintings for this artist: {count}')
        return artist, url_painting_list, count
    except Exception as e:
        print('failed to scrape %s'%artist_url, e)
        log.info('failed to scrape %s'%artist_url, e) 

def download_image(painting_name:str, artist:str, output_DIR:str, save_Dict=True) -> Tuple[str,dict]:
    """
    Download image from the painting's wikiart page 
    """
    search_artist  = artist.lower().replace(' ','-')
    # -- Artist Output Directory Settings
    artist_DIR = os.path.join(output_DIR, search_artist)
    MakeDir(artist_DIR)
    # -- Painting page 
    base_url = "https://www.wikiart.org"
    painting_url = base_url + f"/en/{search_artist}/{painting_name}"
    painting_name_dec = urllib.parse.unquote(painting_name)
    output_file_path=os.path.join(artist_DIR, painting_name_dec+'.json')
    filename = os.path.join(artist_DIR, painting_name_dec+'.jpg')
    if os.path.exists(filename) and os.path.exists(output_file_path):
        pass
    else: 
        time.sleep(5.0*random.random()) 
        headers = get_user_agent()
        try:
            page = requests.get(painting_url, headers=headers, proxies = {'http': 'http://46.201.219.210:3128/'})
            soup = BeautifulSoup(page.text,"lxml")
            # -- get painting_attribut
            attributs =  get_painting_attributs(soup,painting_name_dec)
            print(attributs)
            # -- retrieve image url
            image_url = soup.find('img')['src']
        except Exception as e:
            print(f'Image url exception : {e}')
            print(painting_name)
            log.info('Image_url finding %s'%painting_name, e) 
        # -- Open a local file with wb ( write binary ) permission.
        if not os.path.exists(filename):
            # -- Open the url image, set stream to True, this will return the stream content.
            time.sleep(4.0*random.random()) 
            try:
                r = requests.get(image_url, stream = True)
                # -- Check if the image was retrieved successfully
                if r.status_code == 200:
                    # -- Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                    r.raw.decode_content = True
                    with open(filename,'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                        print('Image sucessfully Downloaded: ', filename)
                else:
                    print(f"Image {painting_name} Couldn't be retreived")
                    log.info('Image %s Couldnt be retreived'%painting_name, e) 
            except Exception as e :
                print(f'Image url request exception : {e}')
                print(painting_name)
                log.info('Image url request exception %s'%painting_name, e) 
        else:
            print('Image already Downloaded: ', filename)
        if save_Dict: 
            painting_Dict = {}
            painting_Dict[painting_name] = attributs
            painting_Dict[painting_name]['Artist'] = artist
            # -- save RESULTS as json each time to void loosing if an error occurs
            dict_to_json(painting_Dict, output_file_path)

        return painting_name, attributs


def get_Name(soup):
    decoded_name = urllib.parse.unquote(soup.select('article h3')[0].text)
    # -- to remobe \xa0 is actually non-breaking space in Latin1 
    return decoded_name.replace(u'\xa0', u' ')   

def get_Date(soup):
    return  int(soup.find("span", itemprop="dateCreated").text)

def get_Style(soup):
    return  unidecode(soup.select_one('a[href*="/paintings-by-style/"]').text)

def get_Genre(soup):
    return  unidecode(soup.find("span", itemprop="genre").text)

def get_Tags(soup):
    return  [unidecode(item.text.strip()) for item in soup.find_all("a", {"class": "tags-cheaps__item__ref"})]


def get_painting_attributs(soup, painting_name:str) -> dict:
    # -- To store attibuts 
    attributs = {}

    # -- Map for looping
    attributs_map ={
    'Name': get_Name, 
    'Date': get_Date,
    'Style': get_Style,
    'Genre': get_Genre,
    'Tags': get_Tags,
    }

    for attribut, func in attributs_map.items():
        try:
            attributs[attribut] = attributs_map[attribut](soup)
        except Exception as e :
            print(f'--{attribut}--')
            print(e)
            attributs[attribut] = None
            log.info(f'Get attribut {attribut} exception {painting_name}')

    return attributs

# =============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    """
    artist url example : https://www.wikiart.org/en/claude-monet
    painting page url example : https://www.wikiart.org/en/claude-monet/water-lily-pond-evening-right-panel-1926
    <img itemprop="image" src="https://uploads0.wikiart.org/images/claude-monet/view-at-rouelles-le-havre.jpg!Large.jpg" alt="Vue prise à Rouelles, 1858 - Claude Monet" title="Vue prise à Rouelles, 1858 - Claude Monet">
    """
    # -- option to run the scraping
    run = True
    # -- option to test with one painting 
    test = False
    # -- option to check image scraped
    check = False
    # -- option to trigger multiprocessing
    multiprocessing_option = True

    # -- Directory Setting
    main_DIR  = os.path.join(os.path.dirname(__file__),'..')
    output_DIR = os.path.join(main_DIR,'Data')
    MakeDir(output_DIR) # create the directory if not existing
    output_file_path = os.path.join(output_DIR,'paintings.json')  # to store painting attributs

    # -- log Settings 
    LOG_DIR = os.path.join(main_DIR,'logs')
    MakeDir(LOG_DIR) # create the directory if not existing
    LOG_FILE = 'Wikiart_scraping'
    LOGGER_NAME = 'Wikiart_scraping'

    log = Log(LOG_FILE, log_dir= LOG_DIR).get_logger(LOGGER_NAME, level=logging.INFO)

    # -- Variable Setttings
    num_downloaded = 0
    num_paintings = 0
    # -- Dictionnary to track results
    if os.path.exists(output_file_path):
        RESULTS= open_json_file(output_file_path)
        print('Json file already exists, data will be append to it')
    else : 
        RESULTS = {} # dict
    
    ## run ##
    if run :
        artist_list = list(artist_dict.keys())
        search_artist_list = [artist.lower().replace(' ','-') for artist in artist_list]

        # -- Retrieve painting list from artist's page
        print('multiprocessing in progress...')
        results = run_imap_multiprocessing(get_url_painting_list, artist_list)
        print('multiprocessing finished...')

        current_artists = [item[0] for item in results]
        current_painting_lists =  [item[1] for item in results]
        current_counts = [item[2] for item in results]

        for artist, painting_list, count in results:
            search_artist = artist.lower().replace(' ','-')
            RESULTS[artist] = {}
            RESULTS[artist]['Paintings'] = dict.fromkeys(painting_list, None)
            RESULTS[artist]['Count']  = int(count)
            RESULTS[artist]['Folder_name']  = str(search_artist)
            num_paintings += count
        print(f"Total Number of paintings: {num_paintings}")

        #-- Download painting images
        print('Images Downloading...')
        for artist, url_painting_list, count in zip(current_artists,current_painting_lists, current_counts) :
            if not multiprocessing_option: 
                for i, url_painting in tqdm(enumerate(url_painting_list)):
                    _, attributs = download_image(url_painting,artist,output_DIR)
                    RESULTS[artist]['Paintings'][url_painting]= attributs
                    # -- save RESULTS as json each time to avoid loosing data if an error occurs
                    if i % 20 == 0:
                        dict_to_json(RESULTS,output_file_path)
            else: 
                with multiprocessing.Pool(processes=multiprocessing.cpu_count()-1) as pool:
                    results = pool.starmap(download_image, zip(url_painting_list, [artist]*count, [output_DIR]*count)
                    )            
        dict_to_json(RESULTS,output_file_path)
        num_downloaded = len([img for img in iglob(output_DIR+'/*.jpg')])
        print(f'Images Downloading finished : {num_downloaded}')

    ## test ##
    if test:
        artist= "Katsushika Hokusai"
        base_url = "https://www.wikiart.org"
        print(get_url_painting_list(artist))
        search_artist  = artist.lower().replace(' ','-')
        painting_name =  "waterfall-at-yoshino-in-wash%C5%AB"
        print(urllib.parse.unquote(painting_name))
        painting_url = base_url + f"/en/{search_artist}/{painting_name}"
        time.sleep(3.0*random.random()) 
        download_image(painting_name, search_artist, output_DIR)
    
    ## check ##
    if check:
        print('------------- Check -----------------')
        artists = {}
        for DIR in iglob(output_DIR + '/*'):
            if os.path.isdir(DIR):
                artist = os.path.basename(DIR)
                Artist = string.capwords(artist.replace('-',' '))
                jpg_file_count = len([img for img in iglob(DIR + '/*.jpg')])
                artists[Artist] = jpg_file_count
                json_file_count = len([file for file in iglob(DIR + '/*.json')])
                print(f'{artist}: {jpg_file_count } / {artist_count_dict[Artist]}  downloaded images')
                print(f'{artist}: {json_file_count } / {artist_count_dict[Artist]}  json files')
        num_downloaded = len([img for img in iglob(output_DIR+'/*/*.jpg')])
        print(f'Total number of downloaded images : {num_downloaded}')
        print(f'Artists in json file : {list(RESULTS.keys())}')
        plt.figure(figsize=(10,10))
        artists = dict(sorted(artists.items(), key=lambda t: t[::-1]))
        plt.yticks(fontsize=14)
        plt.barh(*zip(*artists.items()),color='gold')
        # Add the data value on head of the bar
        for i, v in enumerate(artists.values()):
            plt.text(v+0.3,i-0.05, str(v), color='gray', fontsize=9)
    
        plt.title('Nombre de peintures téléchargées par artiste.')
        plt.show()


