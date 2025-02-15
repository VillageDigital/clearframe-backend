import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from PIL import Image

# Initialize Flask app
app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
THUMBNAIL_FOLDER = 'uploads/thumbnails'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure necessary folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to create a thumbnail
def create_thumbnail(image_path, thumbnail_path):
    size = (200, 200)  # Set thumbnail size
    with Image.open(image_path) as img:
        img.thumbnail(size)
        img.save(thumbnail_path)

# Route: Home
@app.route("/")
def home():
    return "Hello, World! ClearFrame is live! 🚀"

# Route: Serve Uploaded Files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route: Upload File
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Generate thumbnail
        thumbnail_path = os.path.join(app.config["THUMBNAIL_FOLDER"], filename)
        create_thumbnail(file_path, thumbnail_path)

        return jsonify({"message": "File uploaded successfully!", "filename": filename}), 200

    return jsonify({"error": "File type not allowed"}), 400

# Route: Gallery page
@app.route('/gallery')
def gallery():
    files = os.listdir(UPLOAD_FOLDER)  # Get all uploaded images
    image_urls = [f"/uploads/{file}" for file in files if file.endswith(tuple(ALLOWED_EXTENSIONS))]
    return render_template('gallery.html', images=image_urls)

if __name__ == "__main__":
    app.run(debug=True)
