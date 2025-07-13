"""
-- Table: clients (from clients.sql)
-- id int auto_increment primary key,
-- email varchar (60) UNIQUE not null,
-- first_name varchar (25) not null,
-- last_name varchar (25) not null,
-- contact varchar (13)

-- 1. INSERT (Register User)
-- Note: This schema does not include password or role, which are in the Python User model.
INSERT INTO clients (email, first_name, last_name, contact)
VALUES ('john.doe@example.com', 'John', 'Doe', '254712345678');

-- 2. SELECT (Login User - by email, Get Profile)
-- To check if a user exists by email for login
SELECT id, email, first_name, last_name, contact
FROM clients
WHERE email = 'john.doe@example.com';

-- To get a user's profile by ID
SELECT id, email, first_name, last_name, contact
FROM clients
WHERE id = 1; -- Replace 1 with actual client ID

-- 3. UPDATE (Modify User Profile)
UPDATE clients
SET
    first_name = 'Jonathan',
    contact = '254798765432'
WHERE id = 1; -- Replace 1 with actual client ID

-- 4. DELETE (Not explicitly in pseudocode, but common for admin)
-- Consider soft delete (e.g., adding an 'is_active' column) instead of hard delete
-- if you need to retain historical data or prevent foreign key issues.
DELETE FROM clients
WHERE id = 1; -- Replace 1 with actual client ID

```python
"""

import mysql.connector

# Database connection details (replace with your actual credentials)
db_config = {
    'host': 'localhost',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'hoteldb'
}

def execute_sql(sql_query, params=None, fetch=False):
    """Helper function to execute SQL queries."""
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True) # dictionary=True for dict results
        cursor.execute(sql_query, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid # For INSERT operations
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

def add_Client():
    print("--- Clients INSERT ---")
    insert_sql = "INSERT INTO clients (email, first_name, last_name, contact, status) VALUES (%s, %s, %s, %s,%s)"
    client_id = execute_sql(insert_sql, ('jane.doe@example.com', 'Jane', 'Doe', '254700112233'))
    if client_id:
        print(f"Client inserted with ID: {client_id}")

# SELECT Example

def get_client():
    print("\n--- Clients SELECT ---")
    select_sql = "SELECT id, email, first_name, last_name, contact FROM clients WHERE email = %s"
    client_data = execute_sql(select_sql, ('jane.doe@example.com',), fetch=True)
    if client_data:
        print("Found client:", client_data[0])

# UPDATE Example
def update_Client():
    print("\n--- Clients UPDATE ---")
    update_sql = "UPDATE clients SET first_name = %s WHERE email = %s"
    execute_sql(update_sql, ('Janet', 'jane.doe@example.com'))
    print("Client updated.")

# DELETE Example (use with caution)
# print("\n--- Clients DELETE ---")
# delete_sql = "DELETE FROM clients WHERE email = %s"
# execute_sql(delete_sql, ('jane.doe@example.com',))
# print("Client deleted.")
def delete_Client():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("\tSelect from the choices below\n\t1.Mark as inactive\n\t2.Delete Client Data")
    choice = input("Enter selection: ")
    if choice=='1':
        entry = input("Enter Client ID to mark as inactive: ")
        query = "INSERT INTO clients (status) VALUES('inactive') WHERE id=%s"
        try:
            cursor.execute(query,(entry,))
            if cursor.rowcount > 0:
                print(f"Client with ID {entry} marked as inactive.")
        except mysql.connector.Error as e:
            print(f"Request failed due to '{e}'")
    elif choice=='2':
        entry = input("Enter Client ID to delete: ")
        query = "DELETE FROM clients WHERE id=%s"
        try:
            cursor.execute(query,(entry,))
            if cursor.rowcount > 0:
                print(f"Client with ID {entry} successfully deleted.")
        except mysql.connector.Error as e:
            print(f"Request failed due to '{e}'")