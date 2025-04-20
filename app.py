from flask import Flask
from flask_cors import CORS
from routes import user_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix="/user")
@app.route("/")
def home():
    return "Backend is live and Working!"

if __name__ == "__main__":
    app.run(debug=True)
