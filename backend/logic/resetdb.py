# backend/logic/reset_db.py

from app import app, db

if __name__ == '__main__':
    with app.app_context():
        print("Dropping old tables to clear schema conflicts...")
        db.drop_all()
        
        print("Creating fresh tables with the updated schema...")
        db.create_all()
        
        print("Database reset successful! You are ready to go.")