# utils.py

from flask_mail import Message
from flask_login import current_user
from functools import wraps
from flask import jsonify
from models import UserRole, Room, Service
from app import mail # Import  the mail instance from app.py

def send_email(to_email, subject, body):
    """
    Helper function to send emails.
    """
    try:
        msg = Message(subject, recipients=[to_email])
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False

def is_admin(user):
    """
    Helper function to check if a user has admin role.
    """
    return user and user.is_authenticated and user.role == UserRole.ADMIN

def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

def calculate_total_price(room, total_nights, services_data):
    """
    FUNCTION calculateTotalPrice(roomId, checkIn, checkOut, services):
        GET room price per night
        CALCULATE nights = checkOut - checkIn
        roomTotal = room.price * nights
        servicesTotal = 0
        FOR each service in services:
            servicesTotal += service.price * service.quantity
        RETURN roomTotal + servicesTotal
    """
    room_total = room.price_per_night * total_nights

    services_total = 0
    for service_item in services_data:
        service = Service.query.get(service_item['service_id'])
        if service:
            quantity = service_item.get('quantity', 1)
            services_total += service.price * quantity
    return room_total + services_total

