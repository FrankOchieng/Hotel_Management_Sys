# models.py 

import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON, Text, Enum as SAEnum, DECIMAL as Decimal
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Define East Africa Time (UTC+3)
EAT = timezone(timedelta(hours=3))

def get_eat_time():
    """Returns the current time in EAT."""
    return datetime.now(EAT)

# Define Enums for various fields 
class UserRole(Enum):
    CUSTOMER = 'customer'
    ADMIN = 'admin'

class RoomType(Enum):
    SINGLE = 'single'
    DOUBLE = 'double'
    SUITE = 'suite'
    DELUXE = 'deluxe'

class RoomStatus(Enum):
    AVAILABLE = 'available'
    OCCUPIED = 'occupied'
    MAINTENANCE = 'maintenance'

class BookingStatus(Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CHECKED_IN = 'checked_in'
    CHECKED_OUT = 'checked_out'
    CANCELLED = 'cancelled'

class PaymentStatus(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    REFUNDED = 'refunded'
    FAILED = 'failed'

class PaymentMethod(Enum):
    CARD = 'card'
    CASH = 'cash'
    BANK_TRANSFER = 'bank_transfer'

class ServiceCategory(Enum):
    FOOD = 'food'
    SPA = 'spa'
    TRANSPORT = 'transport'
    ENTERTAINMENT = 'entertainment'

class ReportType(Enum):
    REVENUE = 'revenue'
    OCCUPANCY = 'occupancy'
    CUSTOMER = 'customer'

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SAEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    created_at = Column(DateTime, default=get_eat_time)

    bookings = relationship('Booking', back_populates='user')

    # Flask-Login requires the ID to be a string for session cookies
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.email}>'
class Room(db.Model):
    __tablename__ = 'rooms'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    room_number = Column(String(20), unique=True, nullable=False)
    room_type = Column(SAEnum(RoomType), nullable=False)
    capacity = Column(Integer, nullable=False)
    price_per_night = Column(Decimal(10, 2), nullable=False)
    description = Column(Text, nullable=True)
    amenities = Column(JSON, nullable=True) 
    status = Column(SAEnum(RoomStatus), default=RoomStatus.AVAILABLE, nullable=False)
    images = Column(JSON, nullable=True) 

    bookings = relationship('Booking', back_populates='room')

    def __repr__(self):
        return f'<Room {self.room_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'room_number': self.room_number,
            'room_type': self.room_type.value if self.room_type else None,
            'capacity': self.capacity,
            'price_per_night': float(self.price_per_night) if self.price_per_night else 0.0,
            'description': self.description,
            'amenities': self.amenities,
            'status': self.status.value if self.status else None,
            'images': self.images
        }

class Service(db.Model):
    __tablename__ = 'services'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Decimal(10, 2), nullable=False)
    category = Column(SAEnum(ServiceCategory), nullable=False)
    availability = Column(Boolean, default=True, nullable=False)
    image_url = Column(String(255), nullable=True)
    booking_services = relationship('BookingService', back_populates='service')

    def __repr__(self):
        return f'<Service {self.name}>'

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Fixed: Matches the new Integer ID from the Users table
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    room_id = Column(String(36), ForeignKey('rooms.id'), nullable=False)
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    total_nights = Column(Integer, nullable=False)
    total_amount = Column(Decimal(10, 2), nullable=False)
    booking_status = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    special_requests = Column(Text, nullable=True)
    # Fixed: Uses EAT time
    created_at = Column(DateTime, default=get_eat_time)

    user = relationship('User', back_populates='bookings')
    room = relationship('Room', back_populates='bookings')
    payments = relationship('Payment', back_populates='booking')
    booking_services = relationship('BookingService', back_populates='booking')

    def __repr__(self):
        return f'<Booking {self.id} for Room {self.room_id}>'

class BookingService(db.Model):
    __tablename__ = 'booking_services'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String(36), ForeignKey('bookings.id'), nullable=False)
    service_id = Column(String(36), ForeignKey('services.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Decimal(10, 2), nullable=False) 

    booking = relationship('Booking', back_populates='booking_services')
    service = relationship('Service', back_populates='booking_services')

    def __repr__(self):
        return f'<BookingService {self.id} for Booking {self.booking_id} Service {self.service_id}>'

class Payment(db.Model):
    __tablename__ = 'payments'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String(36), ForeignKey('bookings.id'), nullable=False)
    amount = Column(Decimal(10, 2), nullable=False)
    payment_method = Column(SAEnum(PaymentMethod), nullable=False)
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    stripe_payment_id = Column(String(255), nullable=True) 
    # Fixed: Uses EAT time
    created_at = Column(DateTime, default=get_eat_time)

    booking = relationship('Booking', back_populates='payments')

    def __repr__(self):
        return f'<Payment {self.id} for Booking {self.booking_id}>'