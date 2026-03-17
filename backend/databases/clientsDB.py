from logic.models import db, User, UserRole
from sqlalchemy.exc import SQLAlchemyError

def get_user_by_email(email):
    """Fetch a user by their email address for authentication."""
    try:
        return User.query.filter_by(email=email).first()
    except SQLAlchemyError as e:
        print(f"Database error fetching user by email: {e}")
        return None

def get_user_by_id(user_id):
    """Fetch a user by their UUID."""
    try:
        return User.query.get(user_id)
    except SQLAlchemyError as e:
        print(f"Database error fetching user by ID: {e}")
        return None

def create_client(email, hashed_password, first_name, last_name, phone=""):
    """Register a new customer securely."""
    try:
        # Verify email uniqueness before inserting
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return False, "Email already registered."

        new_user = User(
            email=email,
            password_hash=hashed_password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=UserRole.CUSTOMER
        )
        db.session.add(new_user)
        db.session.commit()
        return True, new_user
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error creating client: {e}")
        return False, str(e)

def update_client_profile(user_id, update_data):
    """Update customer details (name, phone, etc.)."""
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "User not found."

        if 'first_name' in update_data:
            user.first_name = update_data['first_name']
        if 'last_name' in update_data:
            user.last_name = update_data['last_name']
        if 'phone' in update_data:
            user.phone = update_data['phone']

        db.session.commit()
        return True, user
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error updating client profile: {e}")
        return False, str(e)