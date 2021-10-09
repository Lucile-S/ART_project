from flask_admin.contrib.sqla import ModelView
from project.models_db import User, Connection

from flask import Blueprint, redirect, url_for
from build_app import db, admin
from flask_login import current_user, AnonymousUserMixin

class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.username = 'user'

admin_blueprint = Blueprint(name='admin_bp',  import_name=__name__, template_folder=None)


# Prevent administration of Users unless the currently logged-in user has the "admin" role
class UserModelView(ModelView):
    # if current_user.is_authenticated:
    #     role =print(current_user.role)
    #         print('--------------')

    
    def is_accessible(self):
        #print('-------------', current_user.has_role('admin'))
        return (current_user.is_authenticated and current_user.is_active and current_user.role == 'admin')
        
    def _handle_view(self, name):
        if not self.is_accessible():
            # redirect to login page if user doesn't have access
            return redirect(url_for('home.welcome'))
        

admin.add_view(UserModelView(User, db.session))
admin.add_view(UserModelView(Connection, db.session))
