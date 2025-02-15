from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, World! ClearFrame is live! 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use the PORT environment variable from Railway
    app.run(host="0.0.0.0", port=port)

