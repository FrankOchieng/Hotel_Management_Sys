# app.py

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from models import db, User,  Room# Import db and User model

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
 
# Initialize extensions
db.init_app(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' # Specify the login view

@login_manager.user_loader
def load_user(user_id):
    """
    Callback function for Flask-Login to load a user from the database.
    """
    return User.query.get(user_id)

# Import and register blueprints
# These will be created in the subsequent files
from auth import auth_bp
from rooms import rooms_bp
from bookings import bookings_bp
from payments import payments_bp
from admin import admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(rooms_bp, url_prefix='/rooms')
app.register_blueprint(bookings_bp, url_prefix='/bookings')
app.register_blueprint(payments_bp, url_prefix='/payments')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def index():
    """
    Basic route for the homepage.
    """
    return jsonify({"message": "Welcome to the Hotel Booking API!"})

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    rooms = db.session.query(Room).all()
    return jsonify([room.to_dict() for room in rooms])

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        print("Database tables created/checked.")
    app.run(debug=True)

