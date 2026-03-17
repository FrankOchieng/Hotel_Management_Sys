# app.py

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from models import db, User, Room

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# --- SECURITY FEATURES ---
# 1. CORS: Restrict cross-origin resource sharing to your specific frontend domains
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5000"}})

# 2. Talisman: Force HTTPS and set strict HTTP security headers
csp = {
    'default-src': [
        '\'self\'',
        'https://cdn.tailwindcss.com',
        'https://cdnjs.cloudflare.com'
    ]
}
Talisman(app, content_security_policy=csp, force_https=False) # Set force_https=True in production

# 3. Rate Limiting: Prevent brute-force and DoS attacks
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://" # Use Redis in production
)

# Initialize extensions
db.init_app(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Import and register blueprints
from authSys import auth_bp
from roomMngt import rooms_bp
from bookingMngt import bookings_bp
from paymentsHandlers import payments_bp
from adminControl import admin_bp

# Apply strict rate limits to authentication routes
limiter.limit("5 per minute")(auth_bp)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(rooms_bp, url_prefix='/rooms')
app.register_blueprint(bookings_bp, url_prefix='/bookings')
app.register_blueprint(payments_bp, url_prefix='/payments')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def index():
    return jsonify({"message": "Secure Hotel API Online."})

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    rooms = db.session.query(Room).all()
    return jsonify([room.to_dict() for room in rooms])

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Debug=False is critical for security in deployment
    app.run(debug=True, port=5000)