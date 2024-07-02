import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from datetime import datetime
import glob
import shutil


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File uploaded successfully')
            return redirect(url_for('run_yolo', filename=filename))
        else:
            flash('Invalid file format. Allowed formats: png, jpg, jpeg')
    return redirect(request.url)

import cv2
@app.route('/run_yolo/<filename>')
def run_yolo(filename):
    try:
        model = YOLO('model.pt')
        source_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # Process the uploaded image
        result = model.predict(source=source_image_path, imgsz=640, conf=0.5,save = True)
        # Define the parent directory
        parent_directory = 'runs\detect'
        # Get all subdirectories in the parent directory
        subdirectories = [d for d in glob.glob(os.path.join(parent_directory, '*/')) if os.path.isdir(d)]
        # Find the newest directory based on creation time
        newest_directory = max(subdirectories, key=os.path.getctime)
        files = os.listdir(newest_directory)
        # image_filename = next((f for f in files if f.endswith('.jpg') or f.endswith('.png')), None)
        full_path = os.path.join(newest_directory,files[0])
        # Source and destination paths
        source_path = full_path
        destination_path = r'static'
        
        # Move the file from source to destination
        shutil.move(source_path, destination_path)
        return render_template('result.html',filename = files[0])

    except Exception as e:
        flash(f'Error processing image: {str(e)}')
        return redirect(url_for('index'))
    

if __name__ == '__main__':
    app.run(debug=True)
