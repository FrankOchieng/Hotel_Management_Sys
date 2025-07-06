-- Table: payments (from payments.sql)
-- id int auto_increment primary key,
-- booking_id int,
-- amount double,
-- method varchar(10),
-- pay_status varchar (15),
-- date_time timestamp not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP

-- 1. INSERT (Process Payment - initial record)
INSERT INTO payments (booking_id, amount, method, pay_status)
VALUES (1, 450.00, 'card', 'pending'); -- Replace 1 with actual booking ID

-- 2. SELECT (Get Payment Details by Booking ID)
SELECT id, booking_id, amount, method, pay_status, date_time
FROM payments
WHERE booking_id = 1; -- Replace 1 with actual booking ID

-- 3. UPDATE (Handle Payment Webhook - update status)
UPDATE payments
SET pay_status = 'completed'
WHERE id = 1; -- Replace 1 with actual payment ID

-- To update based on booking_id and current status
UPDATE payments
SET pay_status = 'completed'
WHERE booking_id = 1 AND pay_status = 'pending';

-- 4. DELETE (Not explicitly in pseudocode, but common for admin/cleanup)
DELETE FROM payments
WHERE id = 1; -- Replace 1 with actual payment ID
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
print("\n--- Payments INSERT ---")
insert_sql = "INSERT INTO payments (booking_id, amount, method, pay_status) VALUES (%s, %s, %s, %s)"
payment_id = execute_sql(insert_sql, (2, 330.00, 'card', 'pending')) # Assuming booking_id 2 exists
if payment_id:
    print(f"Payment inserted with ID: {payment_id}")

# SELECT Example (Get Payment Details by Booking ID)
print("\n--- Payments SELECT ---")
select_sql = "SELECT id, booking_id, amount, method, pay_status, date_time FROM payments WHERE booking_id = %s"
payments_data = execute_sql(select_sql, (2,), fetch=True)
if payments_data:
    print("Payments for booking 2:", payments_data)

# UPDATE Example (Update Payment Status)
print("\n--- Payments UPDATE ---")
update_sql = "UPDATE payments SET pay_status = %s WHERE id = %s"
execute_sql(update_sql, ('completed', payment_id))
print("Payment status updated.")

# DELETE Example
# print("\n--- Payments DELETE ---")
# delete_sql = "DELETE FROM payments WHERE id = %s"
# execute_sql(delete_sql, (payment_id,))
# print("Payment deleted.")
