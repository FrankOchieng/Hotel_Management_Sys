# admin.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta
from models import db, User, Room, Booking, Payment, RoomType, RoomStatus, BookingStatus, PaymentStatus, UserRole, Service, ReportType
from utils import admin_required, send_email # Assuming utils.py for helpers and decorators

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@login_required
@admin_required
def get_dashboard_stats():
    """
    FUNCTION getDashboardStats():
        totalBookings = COUNT bookings this month
        totalRevenue = SUM payments this month
        occupancyRate = (occupied rooms / total rooms) * 100
        pendingBookings = COUNT bookings WHERE status = 'pending'
        RETURN dashboard metrics
    """
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month_start = (current_month_start + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # totalBookings = COUNT bookings this month
    total_bookings_this_month = Booking.query.filter(
        Booking.created_at >= current_month_start,
        Booking.created_at < next_month_start
    ).count()

    # totalRevenue = SUM payments this month
    total_revenue_this_month = db.session.query(func.sum(Payment.amount)).filter(
        Payment.created_at >= current_month_start,
        Payment.created_at < next_month_start,
        Payment.payment_status == PaymentStatus.PAID
    ).scalar() or 0

    # occupancyRate = (occupied rooms / total rooms) * 100
    total_rooms = Room.query.count()
    # Count rooms that are currently occupied (check-in date <= today < check-out date, and confirmed)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    occupied_rooms_count = db.session.query(Room).join(Booking).filter(
        Booking.booking_status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]),
        Booking.check_in_date <= today,
        Booking.check_out_date > today
    ).distinct().count()

    occupancy_rate = (occupied_rooms_count / total_rooms * 100) if total_rooms > 0 else 0

    # pendingBookings = COUNT bookings WHERE status = 'pending'
    pending_bookings_count = Booking.query.filter_by(booking_status=BookingStatus.PENDING).count()

    return jsonify({
        "total_bookings_this_month": total_bookings_this_month,
        "total_revenue_this_month": str(total_revenue_this_month),
        "occupancy_rate": f"{occupancy_rate:.2f}%",
        "pending_bookings_count": pending_bookings_count,
        "current_occupied_rooms": occupied_rooms_count,
        "total_rooms": total_rooms
    }), 200

@admin_bp.route('/rooms', methods=['GET'])
@login_required
@admin_required
def get_all_rooms():
    """
    GET /admin/rooms
    """
    rooms = Room.query.all()
    result = []
    for room in rooms:
        result.append({
            "id": room.id,
            "room_number": room.room_number,
            "room_type": room.room_type.value,
            "capacity": room.capacity,
            "price_per_night": str(room.price_per_night),
            "description": room.description,
            "amenities": room.amenities,
            "status": room.status.value,
            "images": room.images
        })
    return jsonify(result), 200

@admin_bp.route('/rooms', methods=['POST'])
@login_required
@admin_required
def create_room():
    """
    FUNCTION manageRoom(action, roomData): CASE 'create':
        VALIDATE room data
        CREATE room record
    """
    data = request.get_json()
    room_number = data.get('room_number')
    room_type = data.get('room_type')
    capacity = data.get('capacity')
    price_per_night = data.get('price_per_night')
    description = data.get('description')
    amenities = data.get('amenities')
    status = data.get('status', RoomStatus.AVAILABLE.value) # Default to available
    images = data.get('images')

    # VALIDATE room data
    if not all([room_number, room_type, capacity, price_per_night]):
        return jsonify({"error": "Missing required room data"}), 400
    if Room.query.filter_by(room_number=room_number).first():
        return jsonify({"error": "Room number already exists"}), 409
    try:
        RoomType(room_type)
        RoomStatus(status)
    except ValueError:
        return jsonify({"error": "Invalid room_type or status"}), 400
    if not isinstance(capacity, int) or capacity <= 0:
        return jsonify({"error": "Capacity must be a positive integer"}), 400
    if not isinstance(price_per_night, (int, float)) or price_per_night <= 0:
        return jsonify({"error": "Price per night must be a positive number"}), 400

    try:
        # CREATE room record
        new_room = Room(
            room_number=room_number,
            room_type=RoomType(room_type),
            capacity=capacity,
            price_per_night=price_per_night,
            description=description,
            amenities=amenities,
            status=RoomStatus(status),
            images=images
        )
        db.session.add(new_room)
        db.session.commit()
        return jsonify({"message": "Room created successfully", "room_id": new_room.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create room: {str(e)}"}), 500

@admin_bp.route('/rooms/<room_id>', methods=['PUT'])
@login_required
@admin_required
def update_room(room_id):
    """
    FUNCTION manageRoom(action, roomData): CASE 'update':
        VALIDATE changes don't conflict with existing bookings
        UPDATE room record
    """
    room = Room.query.get(room_id)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    data = request.get_json()
    new_room_number = data.get('room_number', room.room_number)
    new_room_type = data.get('room_type', room.room_type.value)
    new_capacity = data.get('capacity', room.capacity)
    new_price_per_night = data.get('price_per_night', room.price_per_night)
    new_description = data.get('description', room.description)
    new_amenities = data.get('amenities', room.amenities)
    new_status = data.get('status', room.status.value)
    new_images = data.get('images', room.images)

    # VALIDATE changes
    if new_room_number != room.room_number and Room.query.filter_by(room_number=new_room_number).first():
        return jsonify({"error": "New room number already exists"}), 409
    try:
        RoomType(new_room_type)
        RoomStatus(new_status)
    except ValueError:
        return jsonify({"error": "Invalid room_type or status"}), 400
    if not isinstance(new_capacity, int) or new_capacity <= 0:
        return jsonify({"error": "Capacity must be a positive integer"}), 400
    if not isinstance(new_price_per_night, (int, float)) or new_price_per_night <= 0:
        return jsonify({"error": "Price per night must be a positive number"}), 400

    # VALIDATE changes don't conflict with existing bookings
    # If room status is changed to 'maintenance' or 'occupied'
    # Or if capacity is reduced below current bookings' guests, this needs careful handling.
    # For simplicity, we'll check if there are any *active* confirmed bookings for this room.
    if new_status in [RoomStatus.MAINTENANCE.value, RoomStatus.OCCUPIED.value] and room.status == RoomStatus.AVAILABLE.value:
        active_bookings = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.booking_status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]),
            Booking.check_out_date > datetime.now() # Future or current active bookings
        ).first()
        if active_bookings:
            return jsonify({"error": "Cannot change room status to maintenance/occupied while active bookings exist"}), 409

    try:
        # UPDATE room record
        room.room_number = new_room_number
        room.room_type = RoomType(new_room_type)
        room.capacity = new_capacity
        room.price_per_night = new_price_per_night
        room.description = new_description
        room.amenities = new_amenities
        room.status = RoomStatus(new_status)
        room.images = new_images

        db.session.commit()
        return jsonify({"message": "Room updated successfully", "room_id": room.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update room: {str(e)}"}), 500

@admin_bp.route('/rooms/<room_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_room(room_id):
    """
    FUNCTION manageRoom(action, roomData): CASE 'delete':
        CHECK no future bookings exist
        SOFT DELETE room record (or hard delete if policy allows)
    """
    room = Room.query.get(room_id)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    # CHECK no future bookings exist
    future_bookings = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.check_out_date > datetime.now(),
        Booking.booking_status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN])
    ).first()

    if future_bookings:
        return jsonify({"error": "Cannot delete room with existing future or active bookings"}), 409

    try:
        # SOFT DELETE room record (by changing status or adding a 'deleted' flag)
        # Here, we'll change status to 'maintenance' and add a note, or truly delete.
        # For simplicity, let's change status to maintenance and make it unavailable.
        room.status = RoomStatus.MAINTENANCE # Mark as unavailable for new bookings
        room.description = (room.description or "") + "\n[DELETED - No longer available for booking]"
        db.session.commit()
        # If a hard delete is required, use db.session.delete(room) and db.session.commit()
        # but ensure all related records (bookings, payments) are handled (e.g., cascade delete or manual cleanup).

        return jsonify({"message": "Room soft-deleted (marked as maintenance) successfully", "room_id": room.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete room: {str(e)}"}), 500

@admin_bp.route('/bookings', methods=['GET'])
@login_required
@admin_required
def get_all_bookings():
    """
    GET /admin/bookings
    """
    bookings = Booking.query.all()
    result = []
    for booking in bookings:
        result.append({
            "id": booking.id,
            "user_email": booking.user.email,
            "room_number": booking.room.room_number,
            "check_in_date": booking.check_in_date.isoformat(),
            "check_out_date": booking.check_out_date.isoformat(),
            "total_amount": str(booking.total_amount),
            "booking_status": booking.booking_status.value,
            "payment_status": booking.payment_status.value,
            "created_at": booking.created_at.isoformat()
        })
    return jsonify(result), 200

@admin_bp.route('/bookings/<booking_id>/status', methods=['PUT'])
@login_required
@admin_required
def update_booking_status(booking_id):
    """
    PUT /admin/bookings/:id/status
    """
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    data = request.get_json()
    new_status = data.get('status')

    if not new_status:
        return jsonify({"error": "New status is required"}), 400

    try:
        # Validate new status against Enum
        valid_status = BookingStatus(new_status)
    except ValueError:
        return jsonify({"error": f"Invalid booking status: {new_status}"}), 400

    try:
        booking.booking_status = valid_status
        db.session.commit()
        # Optionally, send email notification about status change
        # send_email(booking.user.email, "Booking Status Update", f"Your booking {booking.id} status has been updated to {new_status}.")
        return jsonify({"message": "Booking status updated successfully", "booking_id": booking.id, "new_status": new_status}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update booking status: {str(e)}"}), 500

@admin_bp.route('/reports/<report_type>', methods=['GET'])
@login_required
@admin_required
def generate_reports(report_type):
    """
    FUNCTION generateReports(reportType, dateRange):
        SWITCH reportType:
            CASE 'revenue':
                RETURN revenue breakdown by room type, services
            CASE 'occupancy':
                RETURN occupancy rates by date, room type
            CASE 'customer':
                RETURN customer booking patterns, preferences
    """
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not all([start_date_str, end_date_str]):
        return jsonify({"error": "start_date and end_date are required for reports"}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    if start_date >= end_date:
        return jsonify({"error": "End date must be after start date"}), 400

    report_data = {}

    try:
        if report_type == ReportType.REVENUE.value:
            # Revenue breakdown by room type, services
            # Total revenue from confirmed/paid bookings within the date range
            total_revenue_query = db.session.query(func.sum(Booking.total_amount)).filter(
                Booking.check_in_date >= start_date,
                Booking.check_in_date <= end_date,
                Booking.payment_status == PaymentStatus.PAID
            ).scalar() or 0
 
            # Revenue by room type
            revenue_by_room_type = db.session.query(
                Room.room_type,
                func.sum(Booking.total_amount)
            ).join(Booking).filter(
                Booking.check_in_date >= start_date,
                Booking.check_in_date <= end_date,
                Booking.payment_status == PaymentStatus.PAID
            ).group_by(Room.room_type).all()

            room_type_revenue = {rt.value: str(amount) for rt, amount in revenue_by_room_type}

            # Revenue by services (sum of total_price from BookingService)
            revenue_by_service = db.session.query(
                Service.name,
                func.sum(BookingService.total_price)
            ).join(BookingService).join(Booking).filter(
                Booking.check_in_date >= start_date,
                Booking.check_in_date <= end_date,
                Booking.payment_status == PaymentStatus.PAID
            ).group_by(Service.name).all()

            service_revenue = {name: str(amount) for name, amount in revenue_by_service}

            report_data = {
                "report_type": "revenue",
                "date_range": f"{start_date_str} to {end_date_str}",
                "total_revenue": str(total_revenue_query),
                "revenue_by_room_type": room_type_revenue,
                "revenue_by_service": service_revenue
            }

        elif report_type == ReportType.OCCUPANCY.value:
            # Occupancy rates by date, room type
            # This is more complex and usually involves calculating nights booked per room per day.
            # For simplicity, let's get daily occupancy rate for the range.
            daily_occupancy = []
            current_day = start_date
            while current_day <= end_date:
                # Count occupied rooms for the current day
                occupied_rooms_today = db.session.query(Room).join(Booking).filter(
                    Booking.booking_status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]),
                    Booking.check_in_date <= current_day,
                    Booking.check_out_date > current_day # Check-out day is not occupied
                ).distinct().count()
                total_rooms = Room.query.count()
                daily_rate = (occupied_rooms_today / total_rooms * 100) if total_rooms > 0 else 0
                daily_occupancy.append({
                    "date": current_day.isoformat().split('T')[0],
                    "occupied_rooms": occupied_rooms_today,
                    "total_rooms": total_rooms,
                    "occupancy_rate": f"{daily_rate:.2f}%"
                })
                current_day += timedelta(days=1)

            report_data = {
                "report_type": "occupancy",
                "date_range": f"{start_date_str} to {end_date_str}",
                "daily_occupancy": daily_occupancy
            }

        elif report_type == ReportType.CUSTOMER.value:
            # Customer booking patterns, preferences
            # Top customers by number of bookings
            top_customers_by_bookings = db.session.query(
                User.first_name,
                User.last_name,
                User.email,
                func.count(Booking.id).label('booking_count')
            ).join(Booking).filter(
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            ).group_by(User.id).order_by(func.count(Booking.id).desc()).limit(10).all()

            customer_booking_patterns = []
            for first_name, last_name, email, count in top_customers_by_bookings:
                customer_booking_patterns.append({
                    "name": f"{first_name} {last_name}",
                    "email": email,
                    "booking_count": count
                })

            # Most booked room types
            most_booked_room_types = db.session.query(
                Room.room_type,
                func.count(Booking.id).label('booking_count')
            ).join(Booking).filter(
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            ).group_by(Room.room_type).order_by(func.count(Booking.id).desc()).all()

            room_type_popularity = {rt.value: count for rt, count in most_booked_room_types}

            report_data = {
                "report_type": "customer",
                "date_range": f"{start_date_str} to {end_date_str}",
                "top_customers_by_bookings": customer_booking_patterns,
                "most_booked_room_types": room_type_popularity
            }

        else:
            return jsonify({"error": "Invalid report type"}), 400

        return jsonify(report_data), 200

    except Exception as e:
        return jsonify({"error": f"Failed to generate report: {str(e)}"}), 500

