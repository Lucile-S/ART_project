
# -- Import the packages
from flask import Flask, render_template, jsonify
from build_app import create_app


app, db =create_app()
if __name__ == "__main__":
    app.run(host='0.0.0.0')
#   app.run(host='0.0.0.0', debug=True)