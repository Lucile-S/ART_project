#!/usr/bin/python
import os 
import csv 
import configparser
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, ARRAY, ForeignKeyConstraint,UniqueConstraint
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy_utils.functions import database_exists
from sqlalchemy.ext.compiler import compiles
from build_app import db, bcrypt
from datetime import datetime
from sqlalchemy import null
from flask import current_app 
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class PAINTING(db.Model):
    __tablename__ = 'painting'
    __table_args__ = (db.ForeignKeyConstraint(['Artist'], ['artist.Name']), db.UniqueConstraint('Name'))
    Name = db.Column(db.String, primary_key=True)
    Artist = db.Column(db.String, db.ForeignKey("artist.Name", ondelete='CASCADE'), nullable=False) 
    Date = db.Column(db.Date)
    Genre =db. Column(db.String)
    Style = db.Column(db.String)
    Tags = db.Column(db.ARRAY(db.String))
    Filename = db.Column(db.String)

    def __init__(self, Name, Artist, Date, Genre,Style, Tags, Filename):
        self.Name = Name
        self.Artist = Artist 
        self.Date = Date
        self.Genre = Genre
        self.Style = Style
        self.Tags = Tags
        self.Filename = Filename

    def __repr__(self):
        return "<Painting(Name='{}', Artist='{}', Date={}, Genre={}, Style={}, Tags={}, Filename={})>"\
                .format(self.Name, self.Artist, self.Date, self.Genre, self.Style, self.Tags, self.Filename)


class ARTIST(db.Model):
    __tablename__ = 'artist'
    Name = db.Column(db.String, primary_key=True)
    Nationality = db.Column(String)
    Style = db.Column(ARRAY(String))
    Painting_count = db.Column(Integer)
    paintings = db.relationship("PAINTING", backref = 'artist', cascade="all, delete", passive_deletes=True)

    def __init__(self, Name, Nationality, Style,Painting_count,paintings):
        self.Name = Name
        self.Nationality =Nationality 
        self.Style = Style 
        self.Genre = Painting_count
        self.paintings= paintings

    def __repr__(self):
        return "<Painting(Name='{}', Movement='{}', Painting_count='{}', Nationality='{}'))>"\
                .format(self.Name, self.Movement, self.Painting_count, self.Nationality)


class User(db.Model,UserMixin):
    """
    Class that represents a user of the application

    The following attributes of a user are stored in this table:
        * email - email address of the user
        * hashed password - hashed password (using Flask-Bcrypt)
        * registered_on - date & time that the user registered

    REMEMBER: Never store the plaintext password in a database!
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, primary_key=True, nullable=False)
    username  = db.Column(db.String(30), unique=True, nullable=False)
    hashed_password = db.Column(db.String(60), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String, default='user')
    #connections = db.relationship("Connection", backref ='users', cascade="all, delete", passive_deletes=True)


    def __init__(self, email, username, plaintext_password, role='user'):
        """Create a new User object using the email address and hashing the
        plaintext password using Bcrypt.
        """
        self.email = email
        self.username = username
        self.hashed_password = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')
        self.registered_on = datetime.now()
        self.role = role

    def is_correct_password(self, plaintext_password: str):
        return bcrypt.check_password_hash(self.hashed_password, plaintext_password)

    def set_password(self, plaintext_password):
        self.hashed_password = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')


    def get_reset_token(self, expires_sec = 1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id, 'user_mail':self.email}).decode('utf-8')

    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        print('s',s.loads(token))
        try:
            user_id = s.loads(token)['user_id']
            user_email= s.loads(token)['user_mail']
        except:
            return None
        return User.query.get((user_id,user_email))

    @property
    def is_authenticated(self):
        """Return True if the user has been successfully registered."""
        return True

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        """Return the user ID as a unicode string (`str`)."""
        return str(self.id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"





class Connection(db.Model):
    """
    Class that represents connexion to the application
    The following attributes of an connection are stored in this table:
        * email - email address of the user
        * connected_on - date & time that the user log in
        * connected_on - date & time that the user log out 
    """
    __tablename__ = 'track'
    #__table_args__ = (db.ForeignKeyConstraint(['email'], ['users.email']), db.UniqueConstraint('id'))
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False) 
    connected_on = db.Column(db.DateTime,nullable=True)
    connected_off = db.Column(db.DateTime,nullable=True)
    ForeignKeyConstraint(['email'], ['user.email'])

    def __init__(self, email, connected_on= null(), connected_off= null()):
        self.email = email
        self.connected_on = connected_on
        self.connected_off = connected_off
    
    def __repr__(self):
        return f"<Connection('{self.email}', '{self.connected_on}','{self.connected_off}')"

