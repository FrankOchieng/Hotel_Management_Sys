# bookings.py

from decimal import Decimal
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
from models import Payment, PaymentMethod, db, Booking, Room, Service, BookingService, BookingStatus, PaymentStatus, UserRole
from paymentsHandlers import process_payment_function, refund_payment # Assuming these are functions from payments.py
from utils import calculate_total_price, send_email, is_admin # Assuming utils.py for helpers

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/', methods=['POST'])
@login_required
def create_booking():
    """
    FUNCTION createBooking(userId, roomId, checkIn, checkOut, services, paymentMethod):
        BEGIN TRANSACTION
        VALIDATE dates (checkIn < checkOut, checkIn >= today)
        CHECK room availability for dates
        CALCULATE total amount
        CREATE booking record with status 'pending'
        IF services provided:
            FOR each service:
                CREATE booking_service record
        INITIATE payment process
        IF payment successful:
            UPDATE booking status to 'confirmed'
            UPDATE payment status to 'paid'
            SEND confirmation email
        ELSE:
            ROLLBACK transaction
            RETURN payment error
        COMMIT TRANSACTION
        RETURN booking confirmation
    """
    data = request.get_json()
    room_id = data.get('room_id')
    check_in_str = data.get('check_in_date')
    check_out_str = data.get('check_out_date')
    services_data = data.get('services', []) # List of {'service_id': 'uuid', 'quantity': int}
    payment_method = data.get('payment_method')
    special_requests = data.get('special_requests')

    if not all([room_id, check_in_str, check_out_str, payment_method]):
        return jsonify({"error": "Missing required booking details"}), 400

    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d')
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # BOOKING RULES VALIDATION
    if check_in >= check_out:
        return jsonify({"error": "Check-out date must be after check-in date"}), 400
    if check_in < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
        return jsonify({"error": "Check-in date cannot be in the past"}), 400
    if (check_out - check_in).days > 30:
        return jsonify({"error": "Maximum booking duration is 30 days"}), 400
    if (check_in - datetime.now()).total_seconds() / 3600 < 2:
        return jsonify({"error": "Minimum advance booking is 2 hours"}), 400

    room = Room.query.get(room_id)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    # CHECK room availability for dates
    # Re-using the helper from rooms.py
    from roomMngt import check_room_availability
    if not check_room_availability(room_id, check_in, check_out):
        return jsonify({"error": "Room is not available for the selected dates"}), 409

    # CALCULATE total amount
    total_nights = (check_out - check_in).days
    calculated_total_amount = calculate_total_price(room, total_nights, services_data)

    # BEGIN TRANSACTION
    try:
        # CREATE booking record with status 'pending'
        new_booking = Booking(
            user_id=current_user.id,
            room_id=room_id,
            check_in_date=check_in,
            check_out_date=check_out,
            total_nights=total_nights,
            total_amount=calculated_total_amount,
            booking_status=BookingStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            special_requests=special_requests
        )
        db.session.add(new_booking)
        db.session.flush() # Flush to get booking.id for booking_services and payment

        # IF services provided: FOR each service: CREATE booking_service record
        for service_item in services_data:
            service = Service.query.get(service_item['service_id'])
            if not service or not service.availability:
                raise ValueError(f"Service {service_item['service_id']} not found or unavailable.")
            quantity = service_item.get('quantity', 1)
            service_total_price = service.price * quantity
            new_booking_service = BookingService(
                booking_id=new_booking.id,
                service_id=service.id,
                quantity=quantity,
                total_price=service_total_price
            )
            db.session.add(new_booking_service)

        # INITIATE payment process
        payment_response = process_payment_function(
            booking_id=new_booking.id,
            amount=calculated_total_amount,
            payment_method=payment_method
        )

        if payment_response.get('success'):
            # UPDATE booking status to 'confirmed'
            # UPDATE payment status to 'paid' (or pending if external gateway)
            # Note: For card payments, status will be updated by webhook.
            # For cash/bank transfer, it remains pending until manually confirmed.
            if payment_method == 'card':
                # For card, payment_status will be updated via webhook
                new_booking.payment_status = PaymentStatus.PENDING # Awaiting webhook
            else:
                new_booking.payment_status = PaymentStatus.PAID # Assuming immediate for cash/bank_transfer
                new_booking.booking_status = BookingStatus.CONFIRMED # Assuming immediate for cash/bank_transfer

            db.session.commit()

            # SEND confirmation email
            # send_email(current_user.email, "Booking Confirmation", f"Your booking {new_booking.id} is confirmed!")

            # RETURN booking confirmation
            return jsonify({
                "message": "Booking created successfully",
                "booking_id": new_booking.id,
                "payment_details": payment_response.get('payment_details'),
                "checkout_url": payment_response.get('checkout_url')
            }), 201
        else:
            # ROLLBACK transaction
            db.session.rollback()
            # RETURN payment error
            return jsonify({"error": f"Payment initiation failed: {payment_response.get('error')}"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Booking creation failed: {str(e)}"}), 500

@bookings_bp.route('/', methods=['GET'])
@login_required
def get_user_bookings():
    """
    GET /bookings (user's bookings)
    """
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    result = []
    for booking in bookings:
        result.append({
            "id": booking.id,
            "room_number": booking.room.room_number,
            "check_in_date": booking.check_in_date.isoformat(),
            "check_out_date": booking.check_out_date.isoformat(),
            "total_amount": str(booking.total_amount),
            "booking_status": booking.booking_status.value,
            "payment_status": booking.payment_status.value,
            "created_at": booking.created_at.isoformat()
        })
    return jsonify(result), 200

@bookings_bp.route('/<booking_id>', methods=['GET'])
@login_required
def get_booking_details(booking_id):
    """
    GET /bookings/:id
    """
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    # VALIDATE user owns booking OR user is admin
    if booking.user_id != current_user.id and not is_admin(current_user):
        return jsonify({"error": "Unauthorized access to booking"}), 403

    booking_services_data = []
    for bs in booking.booking_services:
        booking_services_data.append({
            "service_name": bs.service.name,
            "quantity": bs.quantity,
            "total_price": str(bs.total_price)
        })

    return jsonify({
        "id": booking.id,
        "user_id": booking.user_id,
        "room_id": booking.room_id,
        "room_number": booking.room.room_number,
        "check_in_date": booking.check_in_date.isoformat(),
        "check_out_date": booking.check_out_date.isoformat(),
        "total_nights": booking.total_nights,
        "total_amount": str(booking.total_amount),
        "booking_status": booking.booking_status.value,
        "payment_status": booking.payment_status.value,
        "special_requests": booking.special_requests,
        "created_at": booking.created_at.isoformat(),
        "services": booking_services_data
    }), 200

@bookings_bp.route('/<booking_id>', methods=['PUT'])
@login_required
def modify_booking(booking_id):
    """
    FUNCTION modifyBooking(bookingId, newDates, newServices):
        VALIDATE modification is allowed
        CHECK new dates availability
        CALCULATE price difference
        IF additional payment needed:
            PROCESS additional payment
        ELSE IF refund due:
            PROCESS partial refund
        UPDATE booking details
        SEND modification confirmation
    """
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    # VALIDATE user owns booking OR user is admin
    if booking.user_id != current_user.id and not is_admin(current_user):
        return jsonify({"error": "Unauthorized to modify this booking"}), 403

    # VALIDATE modification is allowed (e.g., not too close to check-in)
    # This rule is not explicitly in pseudocode but is good practice.
    # Let's say, no modification within 24 hours of check-in
    if (booking.check_in_date - datetime.now()).total_seconds() / 3600 < 24:
        return jsonify({"error": "Booking cannot be modified within 24 hours of check-in"}), 400
    if booking.booking_status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
        return jsonify({"error": f"Booking status '{booking.booking_status.value}' does not allow modification"}), 400


    data = request.get_json()
    new_check_in_str = data.get('new_check_in_date', booking.check_in_date.isoformat().split('T')[0])
    new_check_out_str = data.get('new_check_out_date', booking.check_out_date.isoformat().split('T')[0])
    new_services_data = data.get('new_services', []) # List of {'service_id': 'uuid', 'quantity': int}

    try:
        new_check_in = datetime.strptime(new_check_in_str, '%Y-%m-%d')
        new_check_out = datetime.strptime(new_check_out_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format for new dates. Use YYYY-MM-DD"}), 400

    # Date validation for new dates
    if new_check_in >= new_check_out:
        return jsonify({"error": "New check-out date must be after new check-in date"}), 400
    if (new_check_out - new_check_in).days > 30:
        return jsonify({"error": "Maximum booking duration is 30 days"}), 400

    original_total_amount = booking.total_amount
    room = booking.room

    # CHECK new dates availability (excluding current booking from conflict check)
    # Temporarily set current booking status to cancelled for availability check
    original_booking_status = booking.booking_status
    booking.booking_status = BookingStatus.CANCELLED_TEMP # A temporary status for check
    db.session.flush() # Ensure this change is visible for the query

    from roomMngt import check_room_availability
    if not check_room_availability(booking.room_id, new_check_in, new_check_out):
        booking.booking_status = original_booking_status # Revert status
        db.session.rollback() # Rollback the flush
        return jsonify({"error": "Room is not available for the new dates"}), 409

    booking.booking_status = original_booking_status # Revert status if check passes

    # CALCULATE new total amount
    new_total_nights = (new_check_out - new_check_in).days
    # Fetch current services for the booking to recalculate if new_services_data is empty
    current_services_for_calc = []
    if not new_services_data: # If no new services provided, assume existing services
        for bs in booking.booking_services:
            current_services_for_calc.append({'service_id': bs.service_id, 'quantity': bs.quantity})
        new_calculated_total_amount = calculate_total_price(room, new_total_nights, current_services_for_calc)
    else:
        new_calculated_total_amount = calculate_total_price(room, new_total_nights, new_services_data)


    price_difference = new_calculated_total_amount - original_total_amount

    try:
        # IF additional payment needed: PROCESS additional payment
        if price_difference > 0:
            payment_response = process_payment_function(
                booking_id=booking.id,
                amount=price_difference,
                payment_method=booking.payments[0].payment_method if booking.payments else PaymentMethod.CARD # Use original method or default
            )
            if not payment_response.get('success'):
                raise Exception(f"Additional payment failed: {payment_response.get('error')}")
            # Note: For card, webhook will update. For cash/bank, assume immediate success.
            if booking.payments and booking.payments[0].payment_method != PaymentMethod.CARD:
                booking.payment_status = PaymentStatus.PAID # If additional payment is cash/bank
        # ELSE IF refund due: PROCESS partial refund
        elif price_difference < 0:
            refund_amount = abs(price_difference)
            refund_response = refund_payment(booking.payments[0].stripe_payment_id, refund_amount) # Assumes Stripe
            if not refund_response.get('success'):
                raise Exception(f"Partial refund failed: {refund_response.get('error')}")
            booking.payment_status = PaymentStatus.REFUNDED # Or partially refunded status

        # UPDATE booking details
        booking.check_in_date = new_check_in
        booking.check_out_date = new_check_out
        booking.total_nights = new_total_nights
        booking.total_amount = new_calculated_total_amount

        # Update services if new_services_data is provided
        if new_services_data:
            # Delete existing booking services
            db.session.query(BookingService).filter_by(booking_id=booking.id).delete()
            # Add new booking services
            for service_item in new_services_data:
                service = Service.query.get(service_item['service_id'])
                if not service or not service.availability:
                    raise ValueError(f"Service {service_item['service_id']} not found or unavailable.")
                quantity = service_item.get('quantity', 1)
                service_total_price = service.price * quantity
                new_booking_service = BookingService(
                    booking_id=booking.id,
                    service_id=service.id,
                    quantity=quantity,
                    total_price=service_total_price
                )
                db.session.add(new_booking_service)

        db.session.commit()

        # SEND modification confirmation
        # send_email(current_user.email, "Booking Modified", f"Your booking {booking.id} has been modified.")

        return jsonify({"message": "Booking modified successfully", "booking_id": booking.id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Booking modification failed: {str(e)}"}), 500

@bookings_bp.route('/<booking_id>', methods=['DELETE'])
@login_required
def cancel_booking(booking_id):
    """
    FUNCTION cancelBooking(bookingId, userId):
        VALIDATE user owns booking OR user is admin
        CHECK booking status allows cancellation
        CALCULATE refund amount based on cancellation policy
        UPDATE booking status to 'cancelled'
        IF refund > 0:
            PROCESS refund through payment gateway
            UPDATE payment status to 'refunded'
        SEND cancellation confirmation email
        RETURN cancellation details
    """
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    # VALIDATE user owns booking OR user is admin
    if booking.user_id != current_user.id and not is_admin(current_user):
        return jsonify({"error": "Unauthorized to cancel this booking"}), 403

    # CHECK booking status allows cancellation
    if booking.booking_status == BookingStatus.CANCELLED:
        return jsonify({"message": "Booking is already cancelled"}), 200
    if booking.booking_status in [BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT]:
        return jsonify({"error": "Cannot cancel a checked-in or checked-out booking"}), 400

    # CANCELLATION POLICY:  allowed up to 24 hours before check-in
    time_until_check_in = (booking.check_in_date - datetime.now()).total_seconds() / 3600
    if time_until_check_in < 24 and not is_admin(current_user):
        return jsonify({"error": "Cancellation not allowed within 24 hours of check-in"}), 400

    # CALCULATE refund amount based on cancellation policy
    refund_amount = 0
    if time_until_check_in >= 48:
        refund_amount = booking.total_amount # 100% refund
    elif 24 <= time_until_check_in < 48:
        refund_amount = booking.total_amount * Decimal('0.50') # 50% refund
    # Else 0% refund if < 24 hours

    try:
        # UPDATE booking status to 'cancelled'
        booking.booking_status = BookingStatus.CANCELLED
        db.session.add(booking)

        # IF refund > 0: PROCESS refund through payment gateway
        if refund_amount > 0 and booking.payment_status == PaymentStatus.PAID:
            # Find the primary payment for this booking
            main_payment = Payment.query.filter_by(
                booking_id=booking.id,
                payment_status=PaymentStatus.PAID
            ).first()

            if main_payment and main_payment.stripe_payment_id:
                refund_response = refund_payment(main_payment.stripe_payment_id, refund_amount)
                if refund_response.get('success'):
                    # UPDATE payment status to 'refunded'
                    booking.payment_status = PaymentStatus.REFUNDED
                    db.session.add(booking)
                else:
                    raise Exception(f"Refund failed: {refund_response.get('error')}")
            else:
                # If no Stripe ID or payment not fully paid, cannot process automatic refund
                print(f"Warning: No Stripe payment ID found for booking {booking.id} or payment not paid. Manual refund may be needed.")
                # Still mark booking as cancelled, but payment status remains 'paid' or 'pending'
                # A more robust system would have a 'partially_refunded' status.

        db.session.commit()

        # SEND cancellation confirmation email
        # send_email(current_user.email, "Booking Cancelled", f"Your booking {booking.id} has been cancelled. Refund amount: {refund_amount}")

        # RETURN cancellation details
        return jsonify({
            "message": "Booking cancelled successfully",
            "booking_id": booking.id,
            "refund_amount": str(refund_amount),
            "new_booking_status": booking.booking_status.value,
            "new_payment_status": booking.payment_status.value
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Booking cancellation failed: {str(e)}"}), 500

