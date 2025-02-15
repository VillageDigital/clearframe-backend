import os
app = Flask(__name__)

@app.route('/')
def home():
    return "ClearFrame Backend is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, World! ClearFrame is live! 🚀"

if __name__ == "__main__":
    import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

