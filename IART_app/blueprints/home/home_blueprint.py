"""
The "home" blueprint handles home page.
"""
from flask import Blueprint
from flask import render_template, abort,jsonify


home_blueprint = Blueprint(name='home',  import_name=__name__, template_folder=None)

# @home_blueprint.route('/')
# def hello_world():
#     """
#     """
#     return 'Hello, This is the home page!'

@home_blueprint.route('/', methods=['GET'])
@home_blueprint.route('/home', methods=['GET'])
def welcome():
    """
    ---
    get:
      description:  hello message 
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: Hello
      tags:
          - testing
    """
    output = {"hello": "Welcome"}
    return render_template("home_page.html")