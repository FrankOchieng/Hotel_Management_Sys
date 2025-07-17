"""
-- Table: rooms (from rooms.sql)
-- id int auto_increment primary key not null,
-- room_no varchar (10) unique not null,
-- room_type varchar(25) not null,
-- decription varchar(1000) not null, -- Note: Typo 'decription'
-- room_capacity int,
-- price_pa_night double not null,    -- Note: 'price_pa_night'
-- room_status varchar(25)

-- 1. INSERT (Create Room - Admin)
INSERT INTO rooms (room_no, room_type, decription, room_capacity, price_pa_night, room_status)
VALUES ('101', 'single', 'Cozy single room with city view', 1, 100.00, 'available');

-- 2. SELECT (Search Available Rooms, Get Room Details, Check Room Availability)
-- Search Available Rooms (simplified for SQL schema)
-- This would require complex logic to check for conflicting bookings in SQL.
-- The Python `rooms.py` handles this more robustly.
SELECT id, room_no, room_type, decription, room_capacity, price_pa_night, room_status
FROM rooms
WHERE room_capacity >= 1 AND room_status = 'available' AND room_type = 'single'
AND price_pa_night BETWEEN 50.00 AND 150.00;

-- Get Room Details by ID
SELECT id, room_no, room_type, decription, room_capacity, price_pa_night, room_status
FROM rooms
WHERE id = 1; -- Replace 1 with actual room ID

-- Check Room Availability (simplified - just room status)
-- Full availability check requires joining with bookings table and date logic.
SELECT room_status
FROM rooms
WHERE room_no = '101';

-- 3. UPDATE (Manage Room - Update Status, Price, etc. - Admin)
UPDATE rooms
SET
    room_status = 'maintenance',
    price_pa_night = 120.00,
    decription = 'Updated description for room 101'
WHERE room_no = '101';

-- 4. DELETE (Soft Delete Room - Admin)
-- Change status to 'maintenance' or 'unavailable' instead of actual deletion
UPDATE rooms
SET room_status = 'maintenance'
WHERE room_no = '101';

-- Hard delete (use with extreme caution, especially if foreign keys exist)
DELETE FROM rooms
WHERE room_no = '101';
```python
"""

import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'hoteldb'
}

def execute_sql(sql_query, params=None, fetch=False):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Examples using the helper ---

# INSERT Example
def create_room():
    try:
        print("\n--- Rooms INSERT ---")
        insert_sql = "INSERT INTO rooms (room_no, room_type, decription, room_capacity, price_pa_night, room_status) VALUES (%s, %s, %s, %s, %s, %s)"
        room_id = execute_sql(insert_sql, ('101', 'single', 'Cozy single room with city view', 1, 100.00, 'available'))
        if room_id:
            print(f"Room inserted with ID: {room_id}")
    except Exception as e:
        print(f"Encountered {e}")  


# SELECT Example (Get Room Details)
def select_room():
    print("\n--- Rooms SELECT ---")
    select_sql = "SELECT id, room_no, room_type, decription, room_capacity, price_pa_night, room_status FROM rooms WHERE room_no = %s"
    room_data = execute_sql(select_sql, ('101',), fetch=True)
    if room_data:
        print("Found room:", room_data[0])
    else:
        print("No room found with the specified number.")


# UPDATE Example
def update_room():
    try:
        print("\n--- Rooms UPDATE ---")
        update_sql = "UPDATE rooms SET room_status = %s, price_pa_night = %s WHERE room_no = %s"
        execute_sql(update_sql, ('occupied', 150.00, '101'))
        print("Room updated.")
    except Exception as e:
        print(f"Encountered {e}")
        

# DELETE Example (Soft Delete)
def delete_room():
    print("\n--- Rooms DELETE ---")
    delete_sql = "UPDATE rooms SET room_status = %s WHERE room_no = %s"
    execute_sql(delete_sql, ('maintenance', '101'))
    print("Room soft-deleted (status changed to maintenance).")


def get_rooms_by_type(room_type):
    """
    Function to get rooms by their type.
    Returns a list of Room objects matching the specified room type.
    """
    select_sql = "SELECT * FROM rooms WHERE room_type = %s"
    return execute_sql(select_sql, (room_type,), fetch=True)

def get_rooms_by_status(status):
    """
    Function to get rooms by their status.
    Returns a list of Room objects matching the specified status.
    """
    select_sql = "SELECT * FROM rooms WHERE room_status = %s"
    return execute_sql(select_sql, (status,), fetch=True)

def get_all_rooms():
    """
    Function to get all rooms in the system.
    Returns a list of Room objects.
    """
    select_sql = "SELECT * FROM rooms"
    return execute_sql(select_sql, fetch=True)
    return Room.query.filter(Room.status == status).all()

def get_room_by_id(room_id):
    """
    Function to get a room by its ID.
    Returns a Room object or None if not found.
    """
    select_sql = "SELECT * FROM rooms WHERE id = %s"
    result = execute_sql(select_sql, (room_id,), fetch=True)
    return result[0] if result else None

def update_room(room_id, room_data):
    """
    Function to update a room's details.
    Returns the updated Room object or None if update failed.
    """
    room = get_room_by_id(room_id)
    if not room:
        return None
    
    try:
        update_sql = """
        UPDATE rooms 
        SET room_no = %s, room_type = %s, decription = %s, 
            room_capacity = %s, price_pa_night = %s, room_status = %s
        WHERE id = %s
        """
        execute_sql(update_sql, (
            room_data.get('room_no', room['room_no']),
            room_data.get('room_type', room['room_type']),
            room_data.get('decription', room['decription']),
            room_data.get('room_capacity', room['room_capacity']),
            room_data.get('price_pa_night', room['price_pa_night']),
            room_data.get('room_status', room['room_status']),
            room_id
        ))
        return get_room_by_id(room_id)
    except Exception as e:
        print(f"Error updating room: {e}")
        return None
    
def delete_room(room_id):
    """
    Function to delete a room by its ID.
    Returns True if deletion was successful, False otherwise.
    """
    room = get_room_by_id(room_id)
    if not room:
        return False
    
    try:
        delete_sql = "DELETE FROM rooms WHERE id = %s"
        execute_sql(delete_sql, (room_id,))
        return True
    except Exception as e:
        print(f"Error deleting room: {e}")
        return False
    
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
        insert_sql = """
        INSERT INTO rooms (room_no, room_type, decription, room_capacity, price_pa_night, room_status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        room_id = execute_sql(insert_sql, (
            new_room.room_number,
            new_room.room_type,
            new_room.description,
            new_room.capacity,
            new_room.price_per_night,
            new_room.status.value
        ))
        if room_id:
            new_room.id = room_id
            return new_room
        return None
    except Exception as e:
        print(f"Error adding room: {e}")
        return None
    db.session.rollback()





