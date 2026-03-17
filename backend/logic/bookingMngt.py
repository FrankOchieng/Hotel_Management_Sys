# backend/logic/bookingMngt.py

from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime
from models import db, Booking, Room, RoomStatus, BookingStatus, PaymentStatus
from config import Config

bookings_bp = Blueprint('bookings', __name__)

def get_current_user_id(req):
    """Extract and decode the user_id from the frontend's JWT Bearer token."""
    auth_header = req.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            return payload.get('user_id')
        except:
            return None
    return None

@bookings_bp.route('', methods=['GET'])
def get_user_bookings():
    """Fetch all existing bookings for the currently logged-in user."""
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({"error": "Unauthorized: Please log in again."}), 401

    try:
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
        booking_list = []
        for b in bookings:
            room = Room.query.get(b.room_id)
            booking_list.append({
                "id": b.id,
                "room_number": room.room_number if room else "Unknown",
                "room_id": b.room_id,
                "check_in_date": b.check_in_date.isoformat(),
                "check_out_date": b.check_out_date.isoformat(),
                "total_amount": float(b.total_amount),
                "booking_status": b.booking_status.value,
                "payment_status": b.payment_status.value
            })
        return jsonify(booking_list), 200
    except Exception as e:
        print(f"Fetch Error: {e}")
        return jsonify({"error": "Server error while fetching bookings."}), 500

@bookings_bp.route('', methods=['POST'])
def create_new_booking():
    """Create a new booking, calculate costs, and lock the room."""
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({"error": "Unauthorized: Session expired, please log in."}), 401

    data = request.get_json()
    
    try:
        # 1. Parse Dates and Calculate Total Nights
        check_in = datetime.strptime(data['check_in_date'], '%Y-%m-%d')
        check_out = datetime.strptime(data['check_out_date'], '%Y-%m-%d')
        total_nights = (check_out - check_in).days
        
        if total_nights <= 0:
            return jsonify({"error": "Check-out must be at least 1 day after check-in."}), 400

        # 2. Verify Room Availability
        room = Room.query.get(data['room_id'])
        if not room:
            return jsonify({"error": "Room not found in database."}), 404
            
        if room.status != RoomStatus.AVAILABLE:
            return jsonify({"error": "Sorry, this room is currently occupied."}), 400

        # 3. Calculate Final Cost
        total_amount = float(room.price_per_night) * total_nights

        # 4. Save to Database
        new_booking = Booking(
            user_id=user_id,
            room_id=room.id,
            check_in_date=check_in,
            check_out_date=check_out,
            total_nights=total_nights,
            total_amount=total_amount,
            booking_status=BookingStatus.CONFIRMED,
            payment_status=PaymentStatus.PENDING,
            special_requests=data.get('special_requests', '')
        )
        
        # 5. Lock the room so no one else can book it!
        room.status = RoomStatus.OCCUPIED

        db.session.add(new_booking)
        db.session.commit()
        
        return jsonify({"message": "Booking successful!", "booking_id": new_booking.id}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Booking Creation Error: {e}")
        return jsonify({"error": str(e)}), 500

@bookings_bp.route('/<booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    """Cancel a booking and free up the room."""
    user_id = get_current_user_id(request)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        booking = Booking.query.get(booking_id)
        if not booking or booking.user_id != user_id:
            return jsonify({"error": "Booking not found."}), 404
            
        # Free up the room for others
        room = Room.query.get(booking.room_id)
        if room:
            room.status = RoomStatus.AVAILABLE
            
        booking.booking_status = BookingStatus.CANCELLED
        db.session.commit()
        return jsonify({"message": "Booking cancelled."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to cancel booking."}), 500

@bookings_bp.route('/<booking_id>', methods=['GET'])
def get_booking_details(booking_id):
    """Get details for the pop-up modal."""
    user_id = get_current_user_id(request)
    if not user_id:
         return jsonify({"error": "Unauthorized"}), 401
    try:
         booking = Booking.query.get(booking_id)
         if not booking or booking.user_id != user_id:
              return jsonify({"error": "Booking not found."}), 404
         room = Room.query.get(booking.room_id)
         
         return jsonify({
              "id": booking.id,
              "user_id": booking.user_id,
              "room_number": room.room_number if room else "N/A",
              "room_id": booking.room_id,
              "check_in_date": booking.check_in_date.isoformat(),
              "check_out_date": booking.check_out_date.isoformat(),
              "total_nights": booking.total_nights,
              "total_amount": float(booking.total_amount),
              "booking_status": booking.booking_status.value,
              "payment_status": booking.payment_status.value,
              "special_requests": booking.special_requests,
              "created_at": booking.created_at.isoformat()
         }), 200
    except Exception as e:
         return jsonify({"error": "Error fetching details."}), 500