from logic.models import db, Booking, Room, RoomStatus, BookingStatus, PaymentStatus
from sqlalchemy.exc import SQLAlchemyError

def create_booking(user_id, room_id, check_in, check_out, total_nights, total_amount, special_requests=""):
    """Creates a booking and safely updates the room status in a single transaction."""
    try:
        # Check if room exists and is available
        room = Room.query.get(room_id)
        if not room or room.status != RoomStatus.AVAILABLE:
            return False, "Room is not available for booking."

        # Create the booking record
        new_booking = Booking(
            user_id=user_id,
            room_id=room_id,
            check_in_date=check_in,
            check_out_date=check_out,
            total_nights=total_nights,
            total_amount=total_amount,
            booking_status=BookingStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            special_requests=special_requests
        )
        
        # Mark room as occupied/reserved
        room.status = RoomStatus.OCCUPIED

        db.session.add(new_booking)
        db.session.commit()
        return True, new_booking
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error during booking creation: {e}")
        return False, str(e)

def get_user_bookings(user_id):
    """Fetch all bookings for a specific client."""
    try:
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
        return bookings
    except SQLAlchemyError as e:
        print(f"Database error fetching user bookings: {e}")
        return []

def update_booking_status(booking_id, status):
    """Update the status of a booking (e.g., CONFIRMED, CANCELLED)."""
    try:
        booking = Booking.query.get(booking_id)
        if booking:
            booking.booking_status = status
            
            # If cancelled, free up the room
            if status == BookingStatus.CANCELLED:
                room = Room.query.get(booking.room_id)
                if room:
                    room.status = RoomStatus.AVAILABLE
                    
            db.session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error updating booking: {e}")
        return False