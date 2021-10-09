#!/usr/bin/python

from posix import times_result
import sys 
import os 
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.models import PSQL  # Table's lasses
from sqlalchemy.dialects.postgresql import ARRAY


if __name__ == "__main__":
    add_csv = False
    recreate = False
    read = False
    delete = False
    CRUD_operations =  True


    # -- Directory 
    DIR = os.path.dirname(os.path.abspath(__file__))
    data_DIR  = os.path.join(DIR,'..','Data')

    # -- SQA to know about the Postgres instance
    db = PSQL()

    # -- csv path
    painting_csv_path = os.path.join(data_DIR, 'Paintings_new.csv')
    artist_csv_path = os.path.join(data_DIR, 'Artists_new.csv')

    # -- Create the Table if not existing else connect to it 
    db.create_database()

    # -- Check Tables
    db.get_all_table_schema()

    # ----------- #
    #    Create   #
    # ----------- #

    # -- Add data to table
    if add_csv:
        # --il faut le create database avant 
        db.add_data_from_csv([artist_csv_path, painting_csv_path], ['artist','painting'])
        db.close_all_connection()

    if recreate:
        db.drop_everything()
        print('database dropped to recreate one')
        # -- Check Tables
        db.get_all_table_schema()
        db.create_database()
        db.add_data_from_csv([artist_csv_path, painting_csv_path], ['artist','painting'])
        db.close_all_connection()

    # ----------- #
    #    read     #
    # ----------- #
    if read:
        print('======================= READ Query examples ======================')
        print('----------- All Table Names and Schemas ---------')
        db.get_all_table_schema()

        print('------------ Get first row of each table ---------')
        db.get_first_row()

        print(" \n ----------- All Artist Names -----------")
        db.get_artist_names()

        print(" \n ---------  Get one artist ----------")
        db.get_artist('Gustav Klimt')
        db.get_artist('Katsushika Hokusai')

        print(" \n -----------  Get painting by artist ------------")
        painting_list = db.get_paintings_by_artist('Artemisia Gentileschi')
        print(painting_list)

        print(" \n ------------- All Genres -------------")
        db.get_genres()

        print(" \n ---------  Get painting by artist ----------")
        painting_list = db.get_painting_by_genre("battle painting")
        print(painting_list)

    # ----------- #
    #    Delete   #
    # ----------- #

    if delete:
        db.drop_everything()
        print('All tables has been dropped')

    
    # ----------- #
    #    CRUD    #
    # ----------- #
    
    if CRUD_operations:
        print('======================= Create and Update Query examples ======================')
        print(" \n ---------  Add an artist to the corresponding table ---------")
        # -- Create artist 
        print('-- Create --')
        db.add_artist(Name="Lucile Senicourt", Nationality="French", Style=['AI-art'], Painting_count=1)
        # -- read artist 
        print('-- Read --')
        db.get_artist('Lucile Senicourt')
        # -- update artist
        print('-- Update --')
        db.update_artist("Lucile Senicourt",'Painting_count', 2)
        # -- delete artist 
        print('-- Delete --')
        db.delete_artist("Lucile Senicourt")
        db.close_all_connection()








