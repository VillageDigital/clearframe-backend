import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ExifTags

# Initialize Flask app
app = Flask(__name__)

# Firebase setup
cred = credentials.Certificate("firebase_credentials.json")  # Replace with actual Firebase credentials
firebase_admin.initialize_app(cred)
db = firestore.client()

# Define directories
UPLOAD_FOLDER = "uploads"
THUMBNAIL_FOLDER = os.path.join(UPLOAD_FOLDER, "thumbnails")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# Ensure necessary folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["THUMBNAIL_FOLDER"] = THUMBNAIL_FOLDER

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def auto_convert_image(filepath):
    """Convert any image to a standard JPEG format."""
    try:
        with Image.open(filepath) as img:
            img = img.convert("RGB")  # Ensure compatibility
            new_filepath = filepath.rsplit(".", 1)[0] + ".jpg"  # Change extension to .jpg
            img.save(new_filepath, format="JPEG", quality=90)
            os.remove(filepath)  # Remove the original file
            return new_filepath
    except Exception as e:
        print(f"❌ Image conversion failed: {e}")
        return None

def extract_metadata(filepath):
    """Extract metadata from an image file and ensure it's JSON serializable."""
    metadata = {}
    try:
        with Image.open(filepath) as img:
            metadata["format"] = img.format
            metadata["size"] = img.size  # (width, height)
            metadata["mode"] = img.mode

            # Extract EXIF metadata
            exif_data = img._getexif()
            if exif_data:
                exif_metadata = {}
                for tag, value in exif_data.items():
                    key = ExifTags.TAGS.get(tag, tag)
                    if isinstance(value, bytes):
                        try:
                            value = value.decode("utf-8", "ignore")  # Convert bytes to string
                        except UnicodeDecodeError:
                            value = str(value)  # Ensure JSON compatibility
                    exif_metadata[key] = value
                metadata.update(exif_metadata)
    except Exception as e:
        metadata["error"] = str(e)
    return metadata

def create_thumbnail(filepath, filename, max_size=(200, 200)):
    """Generate a thumbnail while maintaining aspect ratio."""
    try:
        with Image.open(filepath) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            thumb_path = os.path.join(app.config["THUMBNAIL_FOLDER"], filename)
            os.makedirs(app.config["THUMBNAIL_FOLDER"], exist_ok=True)
            img.save(thumb_path, format="JPEG", quality=85)
            return thumb_path
    except Exception as e:
        print(f"❌ Thumbnail creation failed for {filename}: {e}")
        return None

@app.route("/")
def home():
    return "Hello, World! ClearFrame is live! 🚀"

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    """Handle file uploads and generate thumbnails."""
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

        # Auto-convert image if necessary
        converted_filepath = auto_convert_image(filepath)
        if converted_filepath:
            filename = os.path.basename(converted_filepath)
            filepath = converted_filepath

        # Extract metadata
        metadata = extract_metadata(filepath)
        db.collection("images").document(filename).set(metadata)

        # Create thumbnail
        thumb_path = create_thumbnail(filepath, filename)

        return jsonify({"message": "File uploaded successfully!", "filename": filename, "metadata": metadata}), 200

    return jsonify({"error": "File type not allowed"}), 400

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/thumbnails/<filename>")
def uploaded_thumbnail(filename):
    """Serve thumbnails."""
    return send_from_directory(app.config["THUMBNAIL_FOLDER"], filename)

@app.route("/gallery")
def gallery():
    """Display all uploaded images with thumbnails."""
    image_files = [f for f in os.listdir(app.config["UPLOAD_FOLDER"]) if allowed_file(f)]
    return render_template("gallery.html", images=image_files)

if __name__ == "__main__":
    app.run(debug=True)


