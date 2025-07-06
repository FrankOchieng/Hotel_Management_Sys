# payments.py

from flask import Blueprint, request, jsonify
import stripe
from models import db, Booking, Payment, PaymentStatus, BookingStatus, PaymentMethod
from config import Config
from utils import send_email # Assuming send_email utility

payments_bp = Blueprint('payments', __name__)

# Configure  Stripe API key
stripe.api_key = Config.STRIPE_SECRET_KEY

def process_payment_function(booking_id, amount, payment_method):
    """
    FUNCTION processPayment(bookingId, amount, paymentMethod):
        CREATE payment record with status 'pending'
        SWITCH paymentMethod:
            CASE 'card':
                CREATE Stripe checkout session
                RETURN checkout URL
            CASE 'cash':
                MARK as pending for front desk processing
            CASE 'bank_transfer':
                GENERATE payment instructions
        RETURN payment details
    """
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return {"success": False, "error": "Booking not found"}

        # CREATE payment record with status 'pending'
        new_payment = Payment(
            booking_id=booking_id,
            amount=amount,
            payment_method=PaymentMethod(payment_method), # Ensure enum conversion
            payment_status=PaymentStatus.PENDING
        )
        db.session.add(new_payment)
        db.session.flush() # Flush to get payment ID if needed for Stripe metadata

        if payment_method == 'card':
            try:
                # CREATE Stripe checkout session
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd', # Or your preferred currency
                                'product_data': {
                                    'name': f'Booking #{booking.id} - Room {booking.room.room_number}',
                                    'description': f'Check-in: {booking.check_in_date.strftime("%Y-%m-%d")}, Check-out: {booking.check_out_date.strftime("%Y-%m-%d")}',
                                },
                                'unit_amount': int(amount * 100), # Amount in cents
                            },
                            'quantity': 1,
                        },
                    ],
                    mode='payment',
                    success_url='http://localhost:5000/payments/success?session_id={CHECKOUT_SESSION_ID}', # Replace with your actual success URL
                    cancel_url='http://localhost:5000/payments/cancel', # Replace with your actual cancel URL
                    metadata={
                        'booking_id': booking.id,
                        'payment_id': new_payment.id # Link Stripe session to our internal payment record
                    }
                )
                new_payment.stripe_payment_id = checkout_session.id # Store session ID for webhook
                db.session.commit()
                return {
                    "success": True,
                    "payment_details": {
                        "payment_id": new_payment.id,
                        "status": new_payment.payment_status.value
                    },
                    "checkout_url": checkout_session.url
                }
            except stripe.error.StripeError as e:
                db.session.rollback()
                return {"success": False, "error": f"Stripe error: {str(e)}"}
            except Exception as e:
                db.session.rollback()
                return {"success": False, "error": f"Error creating Stripe checkout session: {str(e)}"}

        elif payment_method == 'cash':
            # MARK as pending for front desk processing
            # For cash, payment is considered 'paid' when recorded at front desk
            new_payment.payment_status = PaymentStatus.PENDING # Or could be 'awaiting_cash'
            booking.payment_status = PaymentStatus.PENDING
            db.session.commit()
            return {
                "success": True,
                "payment_details": {
                    "payment_id": new_payment.id,
                    "status": new_payment.payment_status.value,
                    "message": "Payment pending cash collection at front desk."
                }
            }

        elif payment_method == 'bank_transfer':
            # GENERATE payment instructions
            new_payment.payment_status = PaymentStatus.PENDING # Or 'awaiting_transfer'
            booking.payment_status = PaymentStatus.PENDING
            db.session.commit()
            return {
                "success": True,
                "payment_details": {
                    "payment_id": new_payment.id,
                    "status": new_payment.payment_status.value,
                    "instructions": "Please transfer the amount to Bank Account: XXX-YYY-ZZZ, Account Name: Hotel XYZ. Use booking ID as reference."
                }
            }
        else:
            db.session.rollback()
            return {"success": False, "error": "Invalid payment method"}

    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": f"Payment processing failed: {str(e)}"}

def refund_payment(stripe_payment_id, amount):
    """
    Helper function to process refunds via Stripe.
    Assumes stripe_payment_id is the ID of a Stripe PaymentIntent or Charge.
    """
    try:
        # Retrieve the PaymentIntent
        payment_intent = stripe.PaymentIntent.retrieve(stripe_payment_id)

        # Create a refund
        refund = stripe.Refund.create(
            payment_intent=payment_intent.id,
            amount=int(amount * 100), # Amount in cents
        )
        return {"success": True, "refund_id": refund.id, "status": refund.status}
    except stripe.error.StripeError as e:
        return {"success": False, "error": f"Stripe refund error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Refund failed: {str(e)}"}


@payments_bp.route('/webhook', methods=['POST'])
def handle_payment_webhook():
    """
    FUNCTION handlePaymentWebhook(stripeEvent):
        SWITCH event.type:
            CASE 'checkout.session.completed':
                UPDATE payment status to 'completed'
                UPDATE booking status to 'confirmed'
                SEND booking confirmation email
            CASE 'payment_intent.payment_failed':
                UPDATE payment status to 'failed'
                CANCEL booking if no retry
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking_id = session.metadata.get('booking_id')
        payment_id = session.metadata.get('payment_id') # Our internal payment ID

        if booking_id and payment_id:
            booking = Booking.query.get(booking_id)
            payment = Payment.query.get(payment_id)

            if booking and payment:
                try:
                    # UPDATE payment status to 'completed'
                    payment.payment_status = PaymentStatus.PAID
                    payment.stripe_payment_id = session.payment_intent # Store PaymentIntent ID

                    # UPDATE booking status to 'confirmed'
                    booking.payment_status = PaymentStatus.PAID
                    booking.booking_status = BookingStatus.CONFIRMED

                    db.session.commit()

                    # SEND booking confirmation email
                    # Assuming user email can be fetched from booking.user.email
                    # send_email(booking.user.email, "Booking Confirmed!", f"Your booking {booking.id} is now confirmed and paid.")
                    print(f"Webhook: Booking {booking.id} confirmed and paid.")
                except Exception as e:
                    db.session.rollback()
                    print(f"Webhook error processing checkout.session.completed for booking {booking_id}: {str(e)}")
                    return jsonify({'error': 'Internal server error'}), 500
            else:
                print(f"Webhook: Booking or Payment not found for session {session.id}")
        else:
            print(f"Webhook: Missing booking_id or payment_id in session metadata for session {session.id}")

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        # You might need to link this PaymentIntent back to a booking/payment
        # For example, if you stored the booking_id in the PaymentIntent's metadata
        booking_id = payment_intent.metadata.get('booking_id')
        payment_id = payment_intent.metadata.get('payment_id')

        if booking_id and payment_id:
            booking = Booking.query.get(booking_id)
            payment = Payment.query.get(payment_id)

            if booking and payment:
                try:
                    # UPDATE payment status to 'failed'
                    payment.payment_status = PaymentStatus.FAILED
                    booking.payment_status = PaymentStatus.FAILED
                    db.session.commit()

                    # CANCEL booking if no retry (based on your policy)
                    # For simplicity, let's auto-cancel if payment fails
                    if booking.booking_status != BookingStatus.CANCELLED:
                        booking.booking_status = BookingStatus.CANCELLED
                        db.session.commit()
                        # send_email(booking.user.email, "Booking Cancelled - Payment Failed", f"Your booking {booking.id} has been cancelled due to failed payment.")
                        print(f"Webhook: Booking {booking.id} cancelled due to failed payment.")
                except Exception as e:
                    db.session.rollback()
                    print(f"Webhook error processing payment_intent.payment_failed for booking {booking_id}: {str(e)}")
                    return jsonify({'error': 'Internal server error'}), 500

    # Return a 200 response to acknowledge receipt of the event
    return jsonify({'status': 'success'}), 200

@payments_bp.route('/<booking_id>', methods=['GET'])
def get_payment_details(booking_id):
    """
    GET /payments/:bookingId
    """
    payments = Payment.query.filter_by(booking_id=booking_id).all()
    if not payments:
        return jsonify({"error": "No payments found for this booking"}), 404

    result = []
    for payment in payments:
        result.append({
            "id": payment.id,
            "amount": str(payment.amount),
            "payment_method": payment.payment_method.value,
            "payment_status": payment.payment_status.value,
            "stripe_payment_id": payment.stripe_payment_id,
            "created_at": payment.created_at.isoformat()
        })
    return jsonify(result), 200

