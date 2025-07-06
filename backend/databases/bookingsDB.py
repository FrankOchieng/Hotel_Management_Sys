-- Table: bookings (from booking.sql)
-- id int auto_increment primary key not null,
-- guest_name varchar(50) not null,
-- id_number int not null,
-- room_no varchar(10) not null,
-- booking_status varchar(15) not null,
-- checkin_date varchar(10) not null, -- YYYY-MM-DD
-- checkin_time varchar(10) not null, -- HH:MM
-- checkout_date varchar(10) not null,
-- checkout_time varchar(10) not null,
-- total_nights int not null,
-- room_charges double not null,
-- services_offered varchar(3000),    -- Note: Single string for services
-- service_charge double,
-- total_charges double,
-- payment_method varchar(10),
-- payment_status varchar(15),
-- payment_date varchar(10)

-- 1. INSERT (Create Booking)
-- This assumes you've already calculated total_nights, room_charges, service_charge, total_charges.
-- And services_offered is a comma-separated string or JSON string.
INSERT INTO bookings (
    guest_name, id_number, room_no, booking_status,
    checkin_date, checkin_time, checkout_date, checkout_time,
    total_nights, room_charges, services_offered, service_charge,
    total_charges, payment_method, payment_status, payment_date
) VALUES (
    'Alice Smith', 123456, '101', 'pending',
    '2025-08-01', '15:00', '2025-08-05', '11:00',
    4, 400.00, 'Breakfast, WiFi', 50.00,
    450.00, 'card', 'pending', '2025-07-06'
);

-- 2. SELECT (Get User's Bookings, Get Booking Details, Check Room Availability for conflicts)
-- Get all bookings for a specific guest (by name and ID number, or just ID number if unique)
SELECT *
FROM bookings
WHERE guest_name = 'Alice Smith' AND id_number = 123456;

-- Get Booking Details by ID
SELECT *
FROM bookings
WHERE id = 1; -- Replace 1 with actual booking ID

-- Check Room Availability for Conflicts (SQL logic for overlapping dates)
-- This is a complex query due to date/time stored as VARCHAR and need to check overlaps.
-- It would be much simpler if checkin_date/checkout_date were DATETIME types.
-- Example for room '101' between '2025-08-03' and '2025-08-07'
SELECT COUNT(*)
FROM bookings
WHERE room_no = '101'
  AND booking_status NOT IN ('cancelled')
  AND (
        -- New check-in is within existing booking
        ('2025-08-03' BETWEEN checkin_date AND checkout_date AND '2025-08-03' != checkout_date)
        OR
        -- New check-out is within existing booking
        ('2025-08-07' BETWEEN checkin_date AND checkout_date AND '2025-08-07' != checkin_date)
        OR
        -- Existing booking is fully within new dates
        (checkin_date >= '2025-08-03' AND checkout_date <= '2025-08-07')
        OR
        -- New dates are fully within existing booking
        ('2025-08-03' <= checkin_date AND '2025-08-07' >= checkout_date)
      );

-- 3. UPDATE (Modify Booking, Cancel Booking, Update Booking Status - Admin)
-- Modify Booking (e.g., change dates, services, recalculate totals)
UPDATE bookings
SET
    checkin_date = '2025-08-10',
    checkout_date = '2025-08-12',
    total_nights = 2,
    room_charges = 200.00,
    services_offered = 'Breakfast',
    service_charge = 25.00,
    total_charges = 225.00
WHERE id = 1; -- Replace 1 with actual booking ID

-- Cancel Booking (Update status to 'cancelled')
UPDATE bookings
SET
    booking_status = 'cancelled',
    payment_status = 'refunded' -- If a refund is processed
WHERE id = 1; -- Replace 1 with actual booking ID

-- Update Booking Status (Admin)
UPDATE bookings
SET booking_status = 'checked_in'
WHERE id = 1; -- Replace 1 with actual booking ID

```python
import mysql.connector
from datetime import datetime

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
print("\n--- Bookings INSERT ---")
insert_sql = """
INSERT INTO bookings (
    guest_name, id_number, room_no, booking_status,
    checkin_date, checkin_time, checkout_date, checkout_time,
    total_nights, room_charges, services_offered, service_charge,
    total_charges, payment_method, payment_status, payment_date
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
booking_params = (
    'Bob Johnson', 789012, '102', 'pending',
    '2025-09-01', '14:00', '2025-09-03', '11:00',
    2, 300.00, 'Room Service', 30.00,
    330.00, 'card', 'pending', datetime.now().strftime('%Y-%m-%d')
)
booking_id = execute_sql(insert_sql, booking_params)
if booking_id:
    print(f"Booking inserted with ID: {booking_id}")

# SELECT Example (Get Booking Details)
print("\n--- Bookings SELECT ---")
select_sql = "SELECT * FROM bookings WHERE id = %s"
booking_data = execute_sql(select_sql, (booking_id,), fetch=True)
if booking_data:
    print("Found booking:", booking_data[0])

# UPDATE Example (Modify Booking)
print("\n--- Bookings UPDATE (Modify) ---")
update_sql = """
UPDATE bookings
SET
    checkin_date = %s,
    checkout_date = %s,
    total_nights = %s,
    total_charges = %s
WHERE id = %s
"""
execute_sql(update_sql, ('2025-09-05', '2025-09-07', 2, 350.00, booking_id))
print("Booking modified.")

# UPDATE Example (Cancel Booking)
print("\n--- Bookings UPDATE (Cancel) ---")
cancel_sql = "UPDATE bookings SET booking_status = %s, payment_status = %s WHERE id = %s"
execute_sql(cancel_sql, ('cancelled', 'refunded', booking_id))
print("Booking cancelled and payment status updated.")
