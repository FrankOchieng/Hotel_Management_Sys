# backend/logic/seed_db.py
from app import app, db
from models import Room, RoomType, RoomStatus

with app.app_context():
    if Room.query.count() == 0:
        room1 = Room(
            room_number="101",
            room_type=RoomType.DELUXE,
            capacity=2,
            price_per_night=250.00,
            description="Spacious deluxe room with high-speed Wi-Fi, ergonomic workspace, and city views.",
            amenities=["Queen Bed", "High-Speed Wi-Fi", "Complimentary Coffee"],
            images=["./images/deluxe3.jpg"]
        )
        room2 = Room(
            room_number="505",
            room_type=RoomType.SUITE,
            capacity=4,
            price_per_night=950.00,
            description="Indulge in unparalleled luxury within our grand Suite, offering panoramic ocean views and bespoke services.",
            amenities=["King Bed", "Jacuzzi", "Valet Parking"],
            images=["./images/Presidential-Suite-Master-Bedroom.jpg"]
        )
        db.session.add_all([room1, room2])
        db.session.commit()
        print("✅ Success! Sample rooms added to the database.")
    else:
        print("Rooms already exist.")