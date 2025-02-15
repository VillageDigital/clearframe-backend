import os
from flask import Flask, request, jsonify, send_from_directory, render_template

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route: Gallery page to list images
@app.route('/gallery')
def gallery():
    files = os.listdir(UPLOAD_FOLDER)  # Get all uploaded images
    image_urls = [f"/uploads/{file}" for file in files if file.endswith(tuple(ALLOWED_EXTENSIONS))]
    return render_template('gallery.html', images=image_urls)

if __name__ == "__main__":
    app.run(debug=True)
