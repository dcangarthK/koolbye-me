import base64
import io
import os
import cv2

import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from base64 import b64encode
import imageio


app = Flask(__name__)

# Set up MongoDB connection
client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['picture_database']
collection = db['pictures']

# Add custom Jinja2 filter
app.jinja_env.filters['b64encode'] = b64encode

# Set up database path
app.config['picture_database'] = '/opt/homebrew/var/mongodb/'

@app.route('/')
def index():
    pictures = list(collection.find())
    return render_template('index.html', pictures=pictures)


@app.route('/add_picture', methods=['POST'])
def add_picture():
    # Get picture data from form
    picture = request.files['picture']
    print(picture)
    description = request.form['description']
    category = request.form['category']
    if not picture.filename.endswith(('.jpg', '.jpeg', '.png')):
      return 'Invalid file format'

    # Insert picture data into MongoDB
    collection.insert_one({
        'picture': picture.read(),
        'description': description,
        'category': category
    })

    return redirect(url_for('index'))


@app.route('/search_picture', methods=['POST'])
def search_picture():
    # get uploaded image
    img = request.files['picture']
    nparr = np.fromstring(img.read(), np.uint8)

    # convert image to grayscale numpy array
    img_np = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    print(img_np)

    # convert grayscale image to RGB
    img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2RGB)

    # search for matching images in database
    matches = []
    MIN_MATCH_COUNT = 10

    for db_img in collection.find():
        db_img_data = db_img['picture']
        db_img_array = imageio.imread(io.BytesIO(db_img_data), as_gray=True)

        # convert grayscale image to RGB
        db_img_array = cv2.cvtColor(db_img_array, cv2.COLOR_GRAY2RGB)

        # match images using ORB feature detection and description
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img_np, None)
        kp2, des2 = orb.detectAndCompute(db_img_array, None)

        # check descriptor type and shape
        if des1.dtype != np.float32:
            des1 = des1.astype(np.float32)
        if des2.dtype != np.float32:
            des2 = des2.astype(np.float32)
        if des1.shape[1] != des2.shape[1]:
            des1 = des1[:, :des2.shape[1]]
        if des2.shape[1] != des1.shape[1]:
            des2 = des2[:, :des1.shape[1]]

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        if len(matches) > MIN_MATCH_COUNT:
            matchesMask = None
            draw_params = dict(matchColor=(0, 255, 0),
                               singlePointColor=None,
                               matchesMask=matchesMask,
                               flags=2)
            img3 = cv2.drawMatches(cv2.convertScaleAbs(img_np), kp1, cv2.convertScaleAbs(db_img_array), kp2, matches[:MIN_MATCH_COUNT], None, **draw_params)
            matches.append((img3, db_img['description']))
    
    # return matching images
    return render_template('search.html', matches=matches)

if __name__ == '__main__':
    app.run(debug=True)
