# -- Import the packages -- #
from flask import Flask, render_template, jsonify
from flask_migrate import Migrate
from flask_mail import Mail
import os
# -- for swagger documentation
#from project.api_spec import spec
# -- config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
# --logging
import logging
import logging.config
from config import logger_config, Config
from logging.handlers import SMTPHandler
from logging.config import dictConfig
# -- Admin interface 
from flask_admin import Admin
# -- dashboard
import flask_monitoringdashboard as dashboard
from werkzeug.exceptions import HTTPException
import socket
socket.setdefaulttimeout(20)

# ============================================================================ #

# --  Flask extension instances
db = SQLAlchemy()
bcrypt = Bcrypt()
login = LoginManager()
db_migration = Migrate()
mail = Mail()
admin = Admin()

# -- login -- #
login.login_view = "users.login"
login.login_message_category = 'info'

######################################
#### Application Factory Function ####
######################################




def create_app(testing=False):
    # -- Create the Flask application
    app = Flask(__name__)
    with app.app_context():
        # -- app config it contains database config also 
        if testing:
            app.config.from_object('config.TestingConfig') 
            print('testing')
        else:
            app.config.from_object('config.Config') 
            print('No testing')  
            # # -- swagger
            # @app.route("/api/swagger.json")
            # def create_swagger_spec():
            #     """
            #     Swagger API definition.
            #     """
            #     return jsonify(spec.to_dict())
        #app.config.from_envvar('APP_SETTINGS') # need to export before export APP_SETTINGS=/path/to/settings.cfg in terminal

        # -- add extensions 
        initialize_extensions(app, testing=testing)
        # -- register blueprint
        register_blueprints(app)
        # # -- register error 404
        for cls in HTTPException.__subclasses__():
            register_error_pages(app)
        # register_page_not_found(app)
        # -- dashboard
        dashboard.config.init_from(file=Config.DASHBOARD_FILE)
        dashboard.bind(app) 
        # --logging
        dictConfig(logger_config)
        logger = logging.getLogger('werkzeug')
        logger.info("logger configured")

        #if app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_ADMIN'], app.config['MAIL_PASSWORD_ADMIN'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler =  logging.handlers.SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_ADMIN'],
                toaddrs=[app.config['MAIL_ADMIN']],
                subject='IART Failure',
                credentials=auth, secure=secure,  timeout=10.0)

            mail_handler.setLevel(logging.ERROR)
            #mail_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
            logger.addHandler(mail_handler)
            app.logger.addHandler(mail_handler)
    
        # mail_handler.setLevel(logging.ERROR)
        # mail_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))

    return app, db



########################
### Helper Functions ###
########################
def register_error_pages(app):
    @app.errorhandler(Exception)
    def handle_error(e):
        code = 500
        if e.code == 404:
            app.logger.error('Server Error')
            return render_template('404.html'), 404
        else : 
            if isinstance(e, HTTPException):
                code = e.code
                app.logger.error('Server Error')
            return render_template('error.html', error=str(e)), code


def register_blueprints(app):
    # -- Import the blueprints
    from blueprints.home.home_blueprint import home_blueprint
    from blueprints.users.users_blueprint import users_blueprint
    from blueprints.gan.gan_blueprint import gan_blueprint
    from blueprints.gallery.gallery_blueprint import gallery_blueprint
    from blueprints.style_transfer.style_transfer_blueprint import style_transfer_blueprint
    from blueprints.admin import admin_blueprint
    #from blueprints.swagger import swagger_ui_blueprint, SWAGGER_URL
    # -- Since the application instance is now created, register each Blueprint 
    # -- with the Flask application instance (app)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(gallery_blueprint)
    app.register_blueprint(style_transfer_blueprint)
    app.register_blueprint(gan_blueprint)
    app.register_blueprint(admin_blueprint) # Add the admin panel
    #app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)




def initialize_extensions(app, testing=False):
    # Since the application instance is now created, pass it to each Flask
    # extension instance to bind it to the Flask application instance (app)
    db.init_app(app)
    bcrypt.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    admin.init_app(app)
    
    #  -- Flask-Login configuration
    from project.models_db import User, Connection

    if not testing:
        db_migration.init_app(app,db)
        db.create_all() # create table if not existing already 
        db.session.commit()  

    @login.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()

        






		

    




