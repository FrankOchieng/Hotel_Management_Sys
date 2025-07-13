
def adminReg():
    print("--- ADMIN REGISTRATION ---")
    insert_sql = "INSERT INTO admins(reg_NO, passwd, department) VALUES (%s,%s,%s)"
    client_id = execute_sql(insert_sql, (123578,'password','forensics'))
    if admin_id:
        print(f"Admin inserted with ID: {admin_id}")

def deleteAdmin():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("\tSelect from the choices below\n\t1.Mark as inactive\n\t2.Delete Admin Records")
    choice = input("Enter selection: ")
    if choice=='1':
        entry = input("Enter Admin ID to mark as inactive: ")
        query = "INSERT INTO clients (status) VALUES('inactive') WHERE id=%s"
        try:
            cursor.execute(query,(entry,))
            if cursor.rowcount > 0:
                print(f"Admin with ID {entry} marked as inactive.")
        except mysql.connector.Error as e:
            print(f"Request failed due to '{e}'")
    elif choice=='2':
        entry = input("Enter Admin ID to delete: ")
        query = "DELETE FROM admins WHERE id=%s"
        try:
            cursor.execute(query,(entry,))
            if cursor.rowcount > 0:
                print(f"Admin with ID {entry} successfully deleted.")
        except mysql.connector.Error as e:
            print(f"Request failed due to '{e}'")

def getAdmin():
    pass