from models import RoomType, RoomStatus, Room, db

def get_available_rooms(room_type=None, capacity=None):
    """
    Function to get available rooms based on room type and capacity.
    If no filters are provided, it returns all available rooms.
    """
    query = Room.query.filter(Room.status == RoomStatus.AVAILABLE)

    if room_type:
        query = query.filter(Room.room_type == room_type)
    
    if capacity:
        query = query.filter(Room.capacity >= capacity)

    return query.all()

def get_room_by_id(room_id):
    """
    Function to get a room by its ID.
    Returns None if the room does not exist.
    """
    return Room.query.get(room_id)

def add_room(room_data):
    """
    Function to add a new room.
    Expects room_data to be a dictionary with room details.
    Returns the created Room object or None if creation failed.
    """
    try:
        new_room = Room(
            room_number=room_data['room_number'],
            room_type=room_data['room_type'],
            capacity=room_data['capacity'],
            price_per_night=room_data['price_per_night'],
            description=room_data.get('description', ''),
            amenities=room_data.get('amenities', []),
            status=RoomStatus.AVAILABLE,
            images=room_data.get('images', [])
        )
        db.session.add(new_room)
        db.session.commit()
        return new_room
    except Exception as e:
        print(f"Error adding room: {e}")
        db.session.rollback()
        return None
    
def update_room(room_id, room_data):
    """
    Function to update an existing room.
    Expects room_data to be a dictionary with updated room details.
    Returns the updated Room object or None if update failed.
    """
    room = Room.query.get(room_id)
    if not room:
        return None
    
    try:
        room.room_number = room_data.get('room_number', room.room_number)
        room.room_type = room_data.get('room_type', room.room_type)
        room.capacity = room_data.get('capacity', room.capacity)
        room.price_per_night = room_data.get('price_per_night', room.price_per_night)
        room.description = room_data.get('description', room.description)
        room.amenities = room_data.get('amenities', room.amenities)
        room.status = RoomStatus(room_data.get('status', RoomStatus.AVAILABLE))
        room.images = room_data.get('images', room.images)

        db.session.commit()
        return room
    except Exception as e:
        print(f"Error updating room: {e}")
        db.session.rollback()
        return None
    
def delete_room(room_id):
    """
    Function to delete a room by its ID.
    Returns True if deletion was successful, False otherwise.
    """
    room = Room.query.get(room_id)
    if not room:
        return False
    
    try:
        db.session.delete(room)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error deleting room: {e}")
        db.session.rollback()
        return False
    
def get_all_rooms():
    """
    Function to get all rooms in the system.
    Returns a list of Room objects.
    """
    return Room.query.all()

def get_rooms_by_type(room_type):
    """
    Function to get rooms by their type.
    Returns a list of Room objects matching the specified room type.
    """
    return Room.query.filter(Room.room_type == room_type).all()

def get_rooms_by_status(status):
    """
    Function to get rooms by their status.
    Returns a list of Room objects matching the specified status.
    """
    return Room.query.filter(Room.status == status).all()

def get_rooms_by_capacity(capacity):
    """
    Function to get rooms by their capacity.
    Returns a list of Room objects that can accommodate the specified capacity.
    """
    return Room.query.filter(Room.capacity >= capacity).all()

def get_rooms_by_price_range(min_price, max_price):
    """
    Function to get rooms within a specified price range.
    Returns a list of Room objects that fall within the given price range.
    """
    return Room.query.filter(Room.price_per_night.between(min_price, max_price)).all()

def get_rooms_by_amenities(amenities):
    """
    Function to get rooms that have specific amenities.
    Expects amenities to be a list of amenity names.
    Returns a list of Room objects that match the specified amenities.
    """
    query = Room.query
    for amenity in amenities:
        query = query.filter(Room.amenities.contains(amenity))
    return query.all()

def get_dashboard_stats():
    """
    Function to get dashboard statistics.
    Returns a dictionary with various statistics like total rooms, available rooms, etc.
    """
    total_rooms = Room.query.count()
    available_rooms = Room.query.filter(Room.status == RoomStatus.AVAILABLE).count()
    booked_rooms = total_rooms - available_rooms

    return {
        "total_rooms": total_rooms,
        "available_rooms": available_rooms,
        "booked_rooms": booked_rooms
    }

def generate_room_report():
    """
    Function to generate a report of all rooms.
    Returns a list of dictionaries with room details.
    """
    rooms = Room.query.all()
    report = []
    for room in rooms:
        report.append({
            "room_number": room.room_number,
            "room_type": room.room_type,
            "capacity": room.capacity,
            "price_per_night": str(room.price_per_night),
            "status": room.status,
            "amenities": room.amenities,
            "images": room.images
        })
    return report

def search_rooms(query):
    """
    Function to search for rooms based on a query string.
    The query can match room number, type, or amenities.
    Returns a list of Room objects that match the search criteria.
    """
    return Room.query.filter(
        (Room.room_number.ilike(f'%{query}%')) |
        (Room.room_type.ilike(f'%{query}%')) |
        (Room.amenities.contains(query))
    ).all()

def get_room_types():
    """
    Function to get all available room types.
    Returns a list of unique room types from the Room model.
    """
    return db.session.query(Room.room_type).distinct().all()

