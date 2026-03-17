# backend/logic/seed_services.py
from app import app, db
from models import Service, ServiceCategory

with app.app_context():
    s1 = Service(name="Gourmet Breakfast", description="Enjoy a world-class breakfast delivered to your room.", price=45.00, category=ServiceCategory.FOOD, image_url="./images/breakfast.jpeg")
    s2 = Service(name="Deep Tissue Massage", description="60-minute full body massage at our luxury spa.", price=120.00, category=ServiceCategory.SPA, image_url="./images/massage.jpeg")
    s3 = Service(name="Airport Transfer", description="Private luxury SUV pickup from the main terminal.", price=85.00, category=ServiceCategory.TRANSPORT, image_url="./images/airportUber.jpeg")

    db.session.add_all([s1, s2, s3])
    db.session.commit()
    print("Services added successfully!")