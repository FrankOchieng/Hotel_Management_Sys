# auth.py 
 
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from passlib.hash import pbkdf2_sha256
import jwt
from datetime import datetime, timedelta
from models import db, User, UserRole
from config import Config
from utils import send_email # Assuming a utils.py for email sending

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register_user():
    """
    FUNCTION registerUser(email, password, firstName, lastName, phone):
        VALIDATE input data
        CHECK if email already exists
        HASH password
        CREATE user in database with role 'customer'
        SEND confirmation email
        RETURN success/error message
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = data.get('phone')

    # 1. VALIDATE input data
    if not all([email, password, first_name, last_name]):
        return jsonify({"error": "Missing required fields"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    try:
        # 2. CHECK if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409

        # 3. HASH password
        password_hash = pbkdf2_sha256.hash(password)

        # 4. CREATE user in database with role 'customer'
        new_user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=UserRole.CUSTOMER
        )
        db.session.add(new_user)
        db.session.commit()

        # 5. SEND confirmation email (placeholder)
        # send_email(email, "Welcome to Our Hotel!", "Thank you for registering!")

        # 6. RETURN success message
        return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login_user_route():
    """
    FUNCTION loginUser(email, password):
        VALIDATE credentials
        CHECK user exists and password matches
        CREATE session token
        REDIRECT based on user role
        RETURN user data and token
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # 1. VALIDATE credentials
    if not all([email, password]):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    # 2. CHECK user exists and password matches
    if user and pbkdf2_sha256.verify(password, user.password_hash):
        # Using Flask-Login to manage session
        login_user(user)

        # 3. CREATE session token (JWT)
        # This token can be used for API authentication on subsequent requests
        token_payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(hours=24) # Token expires in 24 hours
        }
        token = jwt.encode(token_payload, Config.SECRET_KEY, algorithm='HS256')

        # 4. REDIRECT based on user role (client-side decision usually)
        # 5. RETURN user data and token
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value
            },
            "token": token
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required # Requires a logged-in user to perform logout
def logout_user_route():
    """
    FUNCTION logoutUser():
        INVALIDATE session token
        CLEAR user data from storage
        REDIRECT to homepage (client-side)
    """
    logout_user() # Flask-Login handles session invalidation
    # For JWT, the client-side is responsible for deleting the token.
    # We can optionally blacklist tokens on the server for more robust invalidation.
    return jsonify({"message": "Logged out successfully"}), 200

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_user_profile():
    """
    GET /auth/profile
    """
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "role": current_user.role.value,
        "created_at": current_user.created_at.isoformat()
    }
    return jsonify(user_data), 200

