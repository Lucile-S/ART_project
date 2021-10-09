#!/usr/bin/python
import os 
import csv 
import configparser
import pandas as pd
import sqlalchemy
import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, ForeignKeyConstraint,UniqueConstraint
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy_utils.functions import database_exists
from sqlalchemy.dialects import postgresql
from ast import literal_eval


# -- pandas displaying options 
pd.set_option('max_colwidth', None)
pd.set_option("max_columns", None) # show all cols
pd.set_option('max_colwidth', None) # show full width of showing cols
pd.set_option("expand_frame_repr", False) # print cols side by side as it's supposed to be

# -- MODELS  With SQL Alchemy -- #
Base = declarative_base()

class PAINTING(Base):
    __tablename__ = 'painting'
    __table_args__ = (ForeignKeyConstraint(['Artist'], ['artist.Name']), UniqueConstraint('Name'))
    id = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, unique=True, nullable=False, primary_key=True)
    Artist = Column(String, ForeignKey("artist.Name", ondelete='CASCADE'), nullable=False) 
    Date = Column(Date)
    Genre = Column(String)
    Style = Column(String)
    Tags = Column(postgresql.ARRAY(String))
    Filename = Column(String)


    def __repr__(self):
        return "<Painting(Id = '{}', Name='{}', Artist='{}', Date={}, Genre={}, Style={}, Tags={}, Filename={})>"\
                .format(self.id, self.Name, self.Artist, self.Date, self.Genre, self.Style, self.Tags, self.Filename)

class ARTIST(Base):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, primary_key=True)
    Nationality = Column(String)
    Style = Column(postgresql.ARRAY(String))
    Painting_count = Column(Integer)
    painting = relationship("PAINTING", backref ='artist', cascade="all, delete")

    def __repr__(self):
        return "<Painting(Id ='{}', Name='{}', Style='{}', Painting_count='{}', Nationality='{}'))>"\
                .format(self.id, self.Name, self.Style, self.Painting_count, self.Nationality)


# -- PSQL CLASS -- #
class PSQL:
    def __init__(self):
        # -- Settings database variable from arg_parser
        """Set database configuration """
        self.DIR = os.path.dirname(os.path.abspath(__file__)) # path du dossier contenant le fichier config.py ie. /home/lucile/Miniprojets/Semaine7/template-flask-without-nginx-master/src 
        self.DATABASE_DIR = os.path.join(self.DIR,'..', 'database') # /home/lucile/Miniprojets/Semaine7/template-flask-without-nginx-master/src/../data
        config = configparser.ConfigParser()
        config.read(os.path.join(self.DATABASE_DIR,'databases.ini')) #path of your .ini file
        self.DATABASE_NAME = config.get("postgresql","database")
        # Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"
        USERNAME = config.get("postgresql","user")
        PASSWORD = config.get("postgresql","password")
        IP_ADDRESS = config.get("postgresql","host")
        PORT = config.get("postgresql","port")
        self.DATABASE_URI = f'postgresql+psycopg2://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:{PORT}/{self.DATABASE_NAME}'
        self.engine = self.connect_to_db()
        Session = scoped_session(sessionmaker(bind=self.engine))
        self.session = Session()

    # -------------------------- #
    #         Connection         #
    # -------------------------- #

    def connect_to_db(self):
        """ Connect to the Database"""
        engine = create_engine(self.DATABASE_URI)
        return engine

    def close_connection(self):
        """close session"""
        self.session.close()

    def close_all_connection(self):
        """close all opened sessions"""
        self.session.close_all()

    # -------------------------- #
    #         Creation           #
    # -------------------------- #

    def create_database(self):
        """ create database if not existing"""
        # -- Create database if it does not exist.
        if not database_exists(self.engine.url): 
            print('Database creation.')
            Base.metadata.create_all(self.engine)  #  echo=True to have log INFO printed on the terminal 
        else:
            # -- Connect the database if exists.
            print('Database already existing.')
            self.engine.connect()




    def add_data_from_csv(self, CSV_PATH_list:list, TABLE_NAME_list:list,if_exists="replace"):
        """ ADD data to table(s) from csv file(s)"""
        for CSV_PATH, TABLE_NAME in zip(CSV_PATH_list, TABLE_NAME_list):
            print(f'Add data from {CSV_PATH} to {TABLE_NAME} Table...')
            with open(CSV_PATH, "r") as f:
                # -- to detect delimiter
                sniffer = csv.Sniffer()
                sample_bytes = 32
                dialect= sniffer.sniff(f.read(sample_bytes))
            df = pd.read_csv(CSV_PATH, sep=dialect.delimiter, dtype={'Date': 'Int64'})
            if  TABLE_NAME=="artist":
                df['Style'] =  df['Style'].apply(literal_eval)
                df['Style']= df['Style'].apply(lambda x: None if len(x)==0 else x)
                df.to_sql(TABLE_NAME, con=self.engine, if_exists=if_exists, index=False, dtype={'Style':postgresql.ARRAY(sqlalchemy.types.String)})
            if  TABLE_NAME=="painting":
                df['Tags'] = df['Tags'].apply(literal_eval)
                df['Tags']= df['Tags'].apply(lambda x: None if len(x)==0 else x)
                df.to_sql(TABLE_NAME, con=self.engine, if_exists=if_exists, index=False, dtype={'Tags':postgresql.ARRAY(sqlalchemy.types.String)})
            print('-----')
            # -- push the dataframe to sql 
            self.session.commit()
    
    def add_data_from_json(self, JSON_PATH_list:list, TABLE_NAME_list:list,if_exists="replace"):
        for JSON_PATH, TABLE_NAME in zip(JSON_PATH_list, TABLE_NAME_list):
            data=json.loads(open(JSON_PATH).read())
            # -- if 2 level json file 
            if len(data.values()) ==1:
                data=list(data.values())[0]
            if  TABLE_NAME=="artist":
                self.session.merge(ARTIST(**data))
            if  TABLE_NAME=="painting":
                self.session.merge(PAINTING(**data))
            
            print(f'New data  from {JSON_PATH} has been added to the table {TABLE_NAME}')
            self.session.commit()

    
    def add_artist(self, Name=None, Nationality=None, Style=[], Painting_count=0):
        artist = ARTIST(Name=Name, Nationality=Nationality, Style=Style, Painting_count=Painting_count)  
        self.session.merge(artist)  
        self.session.commit()
        print(f'New artist has been added to the table: \n {artist}')

        
    def add_painting(self, Name=None, Artist=None, Date=None, Genre=None, Style=None, Tags=[], Filename=None):
        painting = PAINTING(Name=Name, Artist=Artist, Date=Date, Genre=Genre, Style=Style, Tags=Tags, Filename=Filename)  
        self.session.add(painting)  
        self.session.commit()
        print(f'New painting has been added to the table: \n {painting}')


    # -------------------------- #
    #           Read             #
    # -------------------------- #

    def show_painting_table(self):
        print(self.session.query(PAINTING).all())

    def show_artist_table(self):
        print(self.session.query(ARTIST).all())

    def get_all_table_schema(self):
        inspector = inspect(self.engine)
        for table_name in inspector.get_table_names():
            print(f'Table names: {table_name}')
            for column in inspector.get_columns(table_name):
                print("Column: %s" % column['name'])
            print('------')

    def get_first_row(self):
        print(self.session.query(ARTIST).first())
        print(self.session.query(PAINTING).first())
        

    def get_artist_names(self):
        """ get all artist names present in the table"""
        artists = self.session.query(ARTIST.Name).all()
        for artist in artists:  
            print(artist[0])

    def get_artist(self,name):
        """ get all information for an artist """
        result =  self.session.query(ARTIST).filter_by(Name=name).all()
        print(result)
    

    def get_painting(self,name):
        """ get all information for an artist """
        result =  self.session.query(PAINTING).filter_by(Name=name).all()
        print(result)

    def get_paintings_by_artist(self, artist_name, limit=None):
        """ get the list of paintings by artist Name"""
        if limit:
            paintings = list(self.session.query(PAINTING).filter_by(Artist=artist_name).limit().all())
        else:
            paintings = list(self.session.query(PAINTING).filter_by(Artist=artist_name).all())
            print(f'There are {len(paintings)} paintings for {artist_name}')
        return paintings

    def get_genres(self):
        """ get all painting genre"""
        genres = self.session.query(PAINTING.Genre).distinct()
        for genre in genres: 
            print(genre[0])

    def get_painting_by_genre(self, Genre, limit=None):
        if limit :
            paintings = self.session.query(PAINTING.Artist,PAINTING.Filename).filter_by(Genre=Genre).all()
        else :
            paintings = self.session.query(PAINTING.Artist,PAINTING.Filename).filter_by(Genre=Genre).limit(limit).all()
        print(f'There are {len(paintings)} paintings for the genre {Genre}')
        return paintings
 
    # -------------------------- #
    #           Update           #
    # -------------------------- #

    def update_artist(self, name, column, new_value):
        artist= self.session.query(ARTIST).filter_by(Name=name).first()
        setattr(artist, column, new_value)
        print(artist)
    
    # -------------------------- #
    #           delete           #
    # -------------------------- #

    def delete_artist(self,name):
        artist = self.session.query(ARTIST).filter_by(Name=name).first()
        self.session.delete(artist)
        self.session.commit() 
        print(f"{name} has been removed from the table ")

    def delete_all_paintings_by_artist(self,artist_name):
        self.session.query(PAINTING).filter_by(Name=artist_name).delete(synchronize_session=False)
        self.session.commit() 
        print(f"All paintings from {artist_name} has been removed from the table ")

    def drop_everything(self):
        """(On a live db) drops all foreign key constraints before dropping all tables.
        Workaround for SQLAlchemy not doing DROP ## CASCADE for drop_all()
        (https://github.com/pallets/flask-sqlalchemy/issues/722)
        """
        from sqlalchemy.engine.reflection import Inspector
        from sqlalchemy.schema import DropConstraint, DropTable, MetaData, Table

        con = self.engine.connect()
        trans = con.begin()
        inspector = Inspector.from_engine(self.engine)

        # We need to re-create a minimal metadata with only the required things to
        # successfully emit drop constraints and tables commands for postgres (based
        # on the actual schema of the running instance)
        meta = MetaData()
        tables = []
        all_fkeys = []

        for table_name in inspector.get_table_names():
            fkeys = []

            for fkey in inspector.get_foreign_keys(table_name):
                if not fkey["name"]:
                    continue

                fkeys.append(ForeignKeyConstraint((), (), name=fkey["name"]))

            tables.append(Table(table_name, meta, *fkeys))
            all_fkeys.extend(fkeys)

        for fkey in all_fkeys:
            con.execute(DropConstraint(fkey))

        for table in tables:
            con.execute(DropTable(table))

        trans.commit()



