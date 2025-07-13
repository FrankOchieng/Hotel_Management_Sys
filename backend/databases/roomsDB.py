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
print("\n--- Rooms INSERT ---")
insert_sql = "INSERT INTO rooms (room_no, room_type, decription, room_capacity, price_pa_night, room_status) VALUES (%s, %s, %s, %s, %s, %s)"
room_id = execute_sql(insert_sql, ('102', 'double', 'Spacious double room', 2, 150.00, 'available'))
if room_id:
    print(f"Room inserted with ID: {room_id}")

# SELECT Example (Get Room Details)
print("\n--- Rooms SELECT ---")
select_sql = "SELECT id, room_no, room_type, decription, room_capacity, price_pa_night, room_status FROM rooms WHERE room_no = %s"
room_data = execute_sql(select_sql, ('102',), fetch=True)
if room_data:
    print("Found room:", room_data[0])

# UPDATE Example
print("\n--- Rooms UPDATE ---")
update_sql = "UPDATE rooms SET room_status = %s, price_pa_night = %s WHERE room_no = %s"
execute_sql(update_sql, ('occupied', 160.00, '102'))
print("Room updated.")

# DELETE Example (Soft Delete)
print("\n--- Rooms Soft DELETE ---")
soft_delete_sql = "UPDATE rooms SET room_status = %s WHERE room_no = %s"
execute_sql(soft_delete_sql, ('maintenance', '102'))
print("Room soft-deleted (status changed to maintenance).")
