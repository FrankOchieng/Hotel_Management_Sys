from app import app, db
from sqlalchemy import text

if __name__ == '__main__':
    with app.app_context():
        try:
            # Force MySQL to add the missing column to the existing table
            db.session.execute(text('ALTER TABLE services ADD COLUMN image_url VARCHAR(255);'))
            db.session.commit()
            print("✅ Successfully patched the database: image_url column added!")
        except Exception as e:
            print(f"⚠️ Notice: {e}")