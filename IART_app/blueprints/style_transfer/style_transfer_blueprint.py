"""
The "style_transfer" blueprint handles neural style transfer.
"""
import os 
import torch
from flask import request, Blueprint,  flash , redirect, url_for #flash for message flashing;  url_for dynamic url
from flask import render_template, send_from_directory
from flask import current_app # to import app from app
from blueprints.style_transfer.style_transfer import  run_style_transfer_app
from werkzeug.utils import secure_filename
import time
from build_app import db, mail
from flask_mail import Message, Mail
style_transfer_blueprint = Blueprint(name='style_transfer',  import_name=__name__, template_folder=None)

# ----------------- #
#    parameters     #
# ----------------- #
# -- current directory
DIR = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(DIR,'images')
OUTPUT_FOLDER = os.path.join(DIR,'images','output')

# -- Function to add time component to an image name
def add_time(filename):
    img_name = filename.rsplit('.')[0]
    img_suffix = filename.rsplit('.')[1]
    filename = str(time.time()).replace('.','_') +'.'+img_suffix
    return filename

# -- Function to check if uploaded file has an acceptable extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#@style_blueprint.route('/style_transfer/')
#def hello_world():
#    return 'Hello, This is the style transfer page!'


@style_transfer_blueprint.route('/style_transfer/')
def index():
    return render_template('style_transfer_index.html')




def send_email_to_admin(body='None'):
    print(current_app.config['MAIL_ADMIN'])
    msg = Message(subject='Flask App IART | Neural Style transfer loading issue',
                sender="admin@IART.com",
                recipients=[current_app.config['MAIL_ADMIN']])
    msg.body = body
    print(msg)
    mail.send(msg)



@style_transfer_blueprint.route('/style_transfer/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # -- check if the post request has the file part
        if 'content' not in request.files:
            flash('No content file part')
            return redirect(request.url)
        if 'style' not in request.files:
            flash('No style file part')
            return redirect(request.url)
            
        global content_filename, style_filename, num_steps
        content_file = request.files['content']
        style_file = request.files['style']
        num_steps = request.form.get("steps", type=int)


        # -- If the user does not select a file, the browser submits an empty file without a filename.
        if content_file.filename == '':
            flash('No selected content file')
            return redirect(request.url)
        if content_file.filename == '':
            flash('No selected style file')
            return redirect(request.url)

        # -- Check extension
        if content_file and allowed_file(content_file.filename):
            # -- To prevent browser caching, add current time to image name
            #content_filename = add_time(content_file.filename)
            content_filename = secure_filename(content_file.filename)
            content_file.save(os.path.join(UPLOAD_FOLDER,'content',content_filename))
            print(f'content file : {content_filename}')
        else:
            send_email_to_admin(body="file extension issue for content image {secure_filename(content_file.filename)}")
            flash('Check file extension (only PNG, JPEG, JPG allowed)')
            return redirect(url_for('style_transfer.index'))
 
        if style_file and allowed_file(style_file.filename):
            # -- To prevent browser caching, add current time to image name
            #style_filename = add_time(style_file.filename)
            style_filename = secure_filename(style_file.filename)
            style_file.save(os.path.join(UPLOAD_FOLDER,'style',style_filename))
            print(f'style file {style_filename}')
        else:
            send_email_to_admin(body=f"file extension issue for style image {secure_filename(style_file.filename)}")
            flash('Check file extension (only PNG, JPEG, JPG allowed)')
            return redirect(url_for('style_transfer.index'))

        return render_template('style_transfer_upload.html', content=content_filename, style=style_filename)



@style_transfer_blueprint.route('/style_transfer/upload/content/<filename>') # <filename> is a variable here content or style
def send_content_image(filename):
	return send_from_directory(os.path.join(UPLOAD_FOLDER,'content'), filename)

@style_transfer_blueprint.route('/style_transfer/upload/style/<filename>') # <filename> is a variable here content or style
def send_style_image(filename):
	return send_from_directory(os.path.join(UPLOAD_FOLDER,'style') ,filename)

@style_transfer_blueprint.route('/style_transfer/result/<filename>', methods = ['GET', 'POST']) # <filename> is a variable here content or style
def send_output_image(filename):
	return send_from_directory(os.path.join(OUTPUT_FOLDER), filename)


# Route where style transfer results will be displayed
@style_transfer_blueprint.route('/style_transfer/result/<content_filename>/<style_filename>', methods=['GET', 'POST'])
def run_style_transfer(content_filename,style_filename):
    if request.method=='POST':
        output_dir = os.path.join(OUTPUT_FOLDER)
        content_path  =os.path.join(UPLOAD_FOLDER,'content',content_filename)
        style_path  =os.path.join(UPLOAD_FOLDER,'style',style_filename)
        output_filename = run_style_transfer_app(content_path,style_path,output_dir,num_steps=num_steps)
        print(f'Output Filename: {output_filename}')
        return render_template('style_transfer_result.html', content_image = content_filename, style_image = style_filename,output_image=output_filename)

