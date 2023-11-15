from flask import Flask, render_template, request,redirect, url_for
import os
import face_recognition
import cv2
import numpy as np

app = Flask(__name__)

# Configure file uploads
app.config["UPLOADED_PHOTOS_DEST"] = "uploads"
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_uploaded_photo(img):
    uploaded_img = face_recognition.load_image_file(img)
    uploaded_img = cv2.cvtColor(uploaded_img, cv2.COLOR_BGR2RGB)

    # Create an empty list to store results for each test image
    results_list = []

    # Specify the directory containing the test images
    test_images_dir = 'images'

    # Loop through each file in the test images directory
    for test_image_filename in os.listdir(test_images_dir):
        if test_image_filename.endswith('.jpg') or test_image_filename.endswith('.jpeg'):
            # Load the test image
            test_img = face_recognition.load_image_file(os.path.join(test_images_dir, test_image_filename))
            test_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB)

            # Detect faces in the images
            face_loc_uploaded = face_recognition.face_locations(uploaded_img)[0]
            encode_uploaded = face_recognition.face_encodings(uploaded_img)[0]

            face_loc_test = face_recognition.face_locations(test_img)[0]
            encode_test = face_recognition.face_encodings(test_img)[0]

            # Compare faces
            results = face_recognition.compare_faces([encode_uploaded], encode_test)
            face_distance = face_recognition.face_distance([encode_uploaded], encode_test)

            # Store results for the current test image
            results_list.append({'filename': test_image_filename, 'match': results[0], 'distance': face_distance[0]})

    # Display results
    for result in results_list:
        print(f"Image: {result['filename']}, Match: {result['match']}, Distance: {round(result['distance'], 2)}")


    matching_images = [result['filename'] for result in results_list if result['match']]

    return matching_images

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    if 'photo' not in request.files:
        return redirect(request.url)

    photo = request.files['photo']

    if photo.filename == '':
        return redirect(request.url)

    if photo and allowed_file(photo.filename):
        photo_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], photo.filename)
        photo.save(photo_path)

        matching_images = process_uploaded_photo(photo_path)

        return render_template('result.html', photo_path=photo_path, matching_images=matching_images)

    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
