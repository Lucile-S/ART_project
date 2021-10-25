
### config.py ###
import os
import configparser
import logging
import click
from logging.handlers import SMTPHandler
    
DIR = os.path.abspath(os.path.dirname(__file__))


class RemoveColorFilter(logging.Filter):
    def filter(self, record):
        if record and record.msg and isinstance(record.msg, str):
            record.msg = click.unstyle(record.msg) 
        return True


# ------------ #
## App config ##
# ------------ #
class Config(object):
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    APP_ROOT = os.path.join(DIR,'..')
    SESSION_TYPE = 'filesystem'
    ## Set database configuration ##
    DATABASE_DIR = os.path.join(DIR,'..', 'db') 
    config = configparser.ConfigParser()
    config.read(os.path.join(DATABASE_DIR,'databases.ini')) #path of your .ini file
    DATABASE_NAME = config.get("postgresql","database")
    TABLE_NAME = ['artists','paintings','users','track']
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"
    USERNAME = config.get("postgresql","user")
    PASSWORD = config.get("postgresql","password")
    IP_ADDRESS = config.get("postgresql","host")
    PORT = config.get("postgresql","port")
    SQLALCHEMY_DATABASE_URI= f'postgresql+psycopg2://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:{PORT}/{DATABASE_NAME}'
    GALLERY_ROOT_DIR =  os.path.join(APP_ROOT, 'static', 'gallery','Data')  
    # -- logging
    DEFAULT_LOGGER_NAME = 'IART_logger'
    # -- flask-mail config 
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL= True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    MAIL_PASSWORD_ADMIN =  os.environ.get('EMAIL_PASSWORD')
    MAIL_ADMIN = os.environ.get('EMAIL_ADMIN')
    DASHBOARD_FILE= os.path.join('dashboard.cfg') 



class TestingConfig(object):
    # Enable the TESTING flag to disable the error catching during request handling
    # so that you get better error reports when performing test requests against the application.
    TESTING = True
    DEBUG = True
    # Disable CSRF tokens in the Forms (only valid for testing purposes!)
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED =  True
    SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    APP_ROOT = os.path.join(DIR,'..')
    # Bcrypt algorithm hashing rounds (reduced for testing purposes only!)
    BCRYPT_LOG_ROUNDS = 4
    ## Set database configuration ##
    DATABASE_DIR = os.path.join(DIR,'..', 'db') 
    config = configparser.ConfigParser()
    config.read(os.path.join(DATABASE_DIR,'databases_test.ini')) #path of your .ini file
    DATABASE_NAME = config.get("postgresql","database")
    TABLE_NAME = ['artists','paintings','users','track']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"
    USERNAME = config.get("postgresql","user")
    PASSWORD = config.get("postgresql","password")
    IP_ADDRESS = config.get("postgresql","host")
    PORT = config.get("postgresql","port")
    SQLALCHEMY_DATABASE_URI= f'postgresql+psycopg2://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:{PORT}/{DATABASE_NAME}'


class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


# ------------------- #
## POSTGRESQL config ##
# ------------------- #
class PSQLConfig(object):
    """Set database configuration """
    DATABASE_DIR = os.path.join(DIR,'..', 'db') 
    config = configparser.ConfigParser()
    config.read(os.path.join(DATABASE_DIR,'databases.ini')) #path of your .ini file
    DATABASE_NAME = config.get("postgresql","database")
    TABLE_NAME = ["artists",'paintings','users','track']
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"
    USERNAME = config.get("postgresql","user")
    PASSWORD = config.get("postgresql","password")
    IP_ADDRESS = config.get("postgresql","host")
    PORT = config.get("postgresql","port")
    SQLALCHEMY_DATABASE_URI= f'postgresql+psycopg2://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:{PORT}/{DATABASE_NAME}'


# ----------------- #
##     logging      ##
# ----------------- #
logger_config = {
    'version': 1,
    'disable_existing_loggers':False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] :: %(levelname)s :: %(threadName)s :: %(module)s ::%(message)s'
            },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'log_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "./logs/IART_app-2.log",
            "formatter" : 'default',

        },
    },
    'root': {
        'level': "INFO",
        'handlers': ['console', 'log_file']
    },
}


