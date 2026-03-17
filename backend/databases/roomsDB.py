from logic.models import db, Room, RoomStatus
from sqlalchemy.exc import SQLAlchemyError

def get_all_rooms():
    """Fetch all rooms from the database."""
    try:
        rooms = Room.query.all()
        return [room.to_dict() for room in rooms] if hasattr(Room, 'to_dict') else rooms
    except SQLAlchemyError as e:
        print(f"Database error fetching rooms: {e}")
        return []

def get_available_rooms():
    """Fetch only currently available rooms."""
    try:
        rooms = Room.query.filter_by(status=RoomStatus.AVAILABLE).all()
        return [room.to_dict() for room in rooms] if hasattr(Room, 'to_dict') else rooms
    except SQLAlchemyError as e:
        print(f"Database error fetching available rooms: {e}")
        return []

def get_room_by_id(room_id):
    """Fetch a specific room by its UUID."""
    try:
        return Room.query.get(room_id)
    except SQLAlchemyError as e:
        print(f"Database error fetching room {room_id}: {e}")
        return None

def create_room(room_data):
    """Create a new room securely using ORM."""
    try:
        new_room = Room(
            room_number=room_data['room_number'],
            room_type=room_data['room_type'],
            capacity=room_data['capacity'],
            price_per_night=room_data['price_per_night'],
            description=room_data.get('description', ''),
            amenities=room_data.get('amenities', []),
            images=room_data.get('images', []),
            status=room_data.get('status', RoomStatus.AVAILABLE)
        )
        db.session.add(new_room)
        db.session.commit()
        return True, new_room
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error creating room: {e}")
        return False, str(e)

def update_room_status(room_id, new_status):
    """Update a room's availability status."""
    try:
        room = Room.query.get(room_id)
        if room:
            room.status = new_status
            db.session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error updating room status: {e}")
        return False