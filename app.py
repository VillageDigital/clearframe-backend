import os
import json
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS

# Initialize Flask app
app = Flask(__name__)

# Define upload folders
UPLOAD_FOLDER = "uploads"
THUMBNAIL_FOLDER = os.path.join(UPLOAD_FOLDER, "thumbnails")
METADATA_FILE = "metadata.json"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Ensure necessary folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["THUMBNAIL_FOLDER"] = THUMBNAIL_FOLDER

# Load or initialize metadata storage
if os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "r") as f:
        metadata_store = json.load(f)
else:
    metadata_store = {}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_metadata(filepath):
    """Extract metadata from an image file."""
    metadata = {}
    try:
        with Image.open(filepath) as img:
            metadata["format"] = img.format
            metadata["size"] = img.size  # (width, height)
            metadata["mode"] = img.mode

            # Extract EXIF metadata
            exif_data = img._getexif()
            if exif_data:
                exif_metadata = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
                metadata.update(exif_metadata)

    except Exception as e:
        metadata["error"] = str(e)
    
    return metadata


@app.route("/")
def home():
    return "Hello, World! ClearFrame is live! 🚀"


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "GET":
        return render_template("upload.html")

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Extract metadata
        metadata = extract_metadata(filepath)
        metadata_store[filename] = metadata

        # Save metadata to file
        with open(METADATA_FILE, "w") as f:
            json.dump(metadata_store, f, indent=4)

        return jsonify({"message": "File uploaded successfully!", "filename": filename, "metadata": metadata}), 200

    return jsonify({"error": "File type not allowed"}), 400


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/metadata/<filename>")
def get_metadata(filename):
    """Fetch metadata for a specific image."""
    if filename in metadata_store:
        return jsonify(metadata_store[filename])
    return jsonify({"error": "Metadata not found"}), 404


@app.route("/gallery")
def gallery():
    """Display all uploaded images."""
    image_files = [f for f in os.listdir(app.config["UPLOAD_FOLDER"]) if allowed_file(f)]
    return render_template("gallery.html", images=image_files)


if __name__ == "__main__":
    app.run(debug=True)
