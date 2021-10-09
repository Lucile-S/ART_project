
#%%
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Lucile Senicourt
# Created Date: Mon May 27 2021
# 
# =============================================================================
# Imports
# =============================================================================
import pandas as pd 
import os 
from glob import iglob
import urllib
import sys
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unidecode import unidecode
from utils.utils import dict_to_json
from utils.utils_data import Painting, Artist, artist_count_dict, artist_dict, artist_nationality_dict

# -- pandas options
pd.set_option('max_colwidth', None)
pd.set_option("max_columns", None) # show all cols
pd.set_option('max_colwidth', None) # show full width of showing cols
pd.set_option("expand_frame_repr", False) # print cols side by side as it's supposed to be


    
# =============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    step_1 = False # remove accent + add Artist and Filename to json
    step_2 = False # handle "not_detected" files
    step_3  = False # Create Artist csv
    check = True # check dataframes 

    # -- Directory Setting
    main_DIR  = os.path.join(os.path.dirname(__file__),'..')
    img_DIR = os.path.join(main_DIR,'Data')
    artist_paths = [path for path in iglob(img_DIR +'/*') if os.path.isdir(path)]
    print(f'There are {len(artist_paths)} artists')
    print(artist_paths)
    print('')

    # -- path for saved df 
    df_path = os.path.join(img_DIR,'Paintings.csv')
    artist_df_path = os.path.join(img_DIR,'Artists.csv')

    if step_1: 
        # -- Create a dataframe to store everything 
        df = pd.DataFrame(columns=['Filename','Name','Date','Style','Genre','Tags','Artist'])
        for artist_path in artist_paths:
            ARTIST =  Artist(artist_path)
            file_paths = ARTIST.file_paths
            print(f'There are {len(file_paths)} files')
            # -- Remove accent from file name and json key
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                filename = urllib.parse.unquote(filename)
                filename = unidecode(filename)
                new_path = os.path.join(os.path.dirname(file_path), filename)
                os.rename(file_path, new_path)

                if new_path.endswith('.json'):
                    PAINTING = Painting(new_path)
                    new_json = {}

                    # -- decode key 
                    if PAINTING.filename != PAINTING._key:
                        key = PAINTING.filename
                    else: 
                        key = PAINTING._key
                
                    # -- create new json with Artist 
                    new_json[key] = list(PAINTING.data.values())[0]
                    new_json[key]['Artist'] = ARTIST.name 

                    # -- create filename in json
                    new_json[key]['Filename'] = key

                    # -- if genre == genre painting
                    if new_json[key]['Genre'] == "genre painting":
                        new_json[key]['Genre'] = None

                    # -- save it 
                    dict_to_json(new_json, new_path)

                    # -- add to df
                    df= df.append(list(new_json.values())[0], ignore_index=True)
        
        print(df)
        # -- convert list to tuple for database
        df['Tags']= df['Tags'].apply(lambda x: tuple(x))
        df.to_csv(df_path, sep=';', index=False)
        print('------')


    if step_2:
        df = pd.read_csv(df_path,  sep=';')

        # -- find "not_detected" files 
        sub_df = df[df['Filename'].str.contains('not_detected', case=False, regex=True)]
        print(sub_df)

        print(f'There are {len(sub_df)} not_detected files')
        not_detected_files = list(sub_df['Filename'].values)
        not_detected_files_names = list(sub_df['Name'].values)
        print(not_detected_files)

        for not_detected_file, not_detected_files_name in zip(not_detected_files, not_detected_files_names):
            not_detected_file_path = list(iglob(img_DIR +'/*/'+not_detected_file+'*'))
            print(not_detected_files_name)
            if not_detected_files_name == "Picture II, Gnomus. (Stage set for Mussorgsky's Pictures at an Exhibition in Friedrich Theater, Dessau)":
                true_filename = "picture-ii-gnomus"
            else:
                true_filename = unidecode(not_detected_files_name.lower().replace(',','').replace("'","-").replace(' ','-'))
            print(true_filename)
            
            for file_path in not_detected_file_path:
                if file_path.endswith('.jpg'):
                    ext = '.jpg'
                else : 
                    ext = '.json'
                new_path  = os.path.join(os.path.dirname(file_path),true_filename+ext)
                print(new_path)
                os.rename(file_path, new_path)
            print('----')

    if step_3: 
        #pd.DataFrame(d.items(), columns=['Date', 'DateValue'])
        list_of_tuples  = tuple(list(zip(artist_dict.keys(), artist_nationality_dict.values(), artist_dict.values(), artist_count_dict.values())))
        artist_df = pd.DataFrame(list_of_tuples, columns = ['Name', 'Nationality','Style','Painting_count'])
        print(artist_df)
        artist_df.to_csv(artist_df_path, sep=';', index=False)
        print('------')

    if check:
        df_artist = pd.read_csv(artist_df_path ,  sep=';')
        df = pd.read_csv(df_path,  sep=';', dtype={'Date': 'Int64'})
        print(df.shape)
        print(df.head())
        print(df['Genre'].unique())
        print(df['Date'].unique())
        print('')
        print(df_artist.shape)
        print(df_artist.head())
        print('------ painting by genre-------')
        painting_by_genre ={}
        # -- Genre
        Genres = [g for g in df['Genre'].unique() if str(g) != 'nan']
        print('Genres:', Genres)
        print(f'There are {len(Genres)} genres')
        for genre in Genres:
            painting_list = list(df[df['Genre']==genre]['Filename'])
            painting_list = [painting for painting in painting_list]
            painting_by_genre[genre] = int(len(painting_list))
        # -- plot genre distribution 
        plt.figure(figsize=(10,10))
        genres = dict(sorted(painting_by_genre.items(), key=lambda t: t[::-1]))
        print(f'total number of paintings with genre attribut {sum(genres.values())}')
        plt.barh(*zip(*genres.items()))
        # -- Add the data value on head of the bar
        for i, v in enumerate(genres.values()):
            plt.text(v+0.3,i-0.05, str(v), color='gray', fontsize=9)
        plt.yticks(fontsize=14)
        plt.title('Nombre de peintures par genre.')
        plt.show()


        


 






# %%
