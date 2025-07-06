-- Table: serv_table (from services.sql)
-- serv_name varchar (50) not null,
-- category varchar(30) not null,
-- serv_description varchar (1000) not null,
-- serv_price double not null,
-- availability bool not null

-- 1. INSERT (Add a new service)
INSERT INTO serv_table (serv_name, category, serv_description, serv_price, availability)
VALUES ('Spa Massage', 'spa', 'Relaxing full body massage', 80.00, TRUE);

-- 2. SELECT (Get Services, Get Services by Category)
-- Get all services
SELECT serv_name, category, serv_description, serv_price, availability
FROM serv_table;

-- Get services by category
SELECT serv_name, category, serv_description, serv_price, availability
FROM serv_table
WHERE category = 'food';

-- 3. UPDATE (Modify Service details)
UPDATE serv_table
SET
    serv_price = 85.00,
    availability = FALSE
WHERE serv_name = 'Spa Massage';

-- 4. DELETE (Remove a service - Admin)
DELETE FROM serv_table
WHERE serv_name = 'Spa Massage';
```python
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
print("\n--- Services INSERT ---")
insert_sql = "INSERT INTO serv_table (serv_name, category, serv_description, serv_price, availability) VALUES (%s, %s, %s, %s, %s)"
execute_sql(insert_sql, ('Laundry Service', 'other', 'Standard laundry service per kg', 15.00, True))
print("Service inserted.")

# SELECT Example (Get all services)
print("\n--- Services SELECT ---")
select_sql = "SELECT serv_name, category, serv_description, serv_price, availability FROM serv_table"
services_data = execute_sql(select_sql, fetch=True)
if services_data:
    print("All services:", services_data)

# UPDATE Example
print("\n--- Services UPDATE ---")
update_sql = "UPDATE serv_table SET serv_price = %s, availability = %s WHERE serv_name = %s"
execute_sql(update_sql, (18.00, False, 'Laundry Service'))
print("Service updated.")

# DELETE Example
print("\n--- Services DELETE ---")
delete_sql = "DELETE FROM serv_table WHERE serv_name = %s"
execute_sql(delete_sql, ('Laundry Service',))
print("Service deleted.")
