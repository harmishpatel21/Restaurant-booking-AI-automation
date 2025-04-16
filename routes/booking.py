import json
from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from models import Booking, AuditLog
from services.booking_service import create_booking, update_booking_status
from services.notification_service import send_booking_confirmation
from services.audit_service import log_action

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/booking', methods=['GET'])
def booking_page():
    """Render the booking page"""
    return render_template('booking.html')

@booking_bp.route('/booking/create', methods=['POST'])
def create_booking_route():
    """Create a new booking"""
    try:
        # Extract form data
        customer_name = request.form.get('customer_name')
        customer_phone = request.form.get('customer_phone')
        customer_email = request.form.get('customer_email', '')
        party_size = request.form.get('party_size')
        booking_date_str = request.form.get('booking_date')
        booking_time = request.form.get('booking_time')
        special_requests = request.form.get('special_requests', '')
        send_sms = bool(request.form.get('send_sms'))
        
        # Validate required fields
        if not all([customer_name, customer_phone, party_size, booking_date_str, booking_time]):
            return jsonify({'success': False, 'message': 'All required fields must be filled'}), 400
        
        # Convert string data to proper types
        try:
            party_size = int(party_size)
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid data format'}), 400
        
        # Validate date (no past dates)
        if booking_date < date.today():
            return jsonify({'success': False, 'message': 'Booking date cannot be in the past'}), 400
        
        # Create booking using service
        booking_data = {
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'customer_email': customer_email,
            'party_size': party_size,
            'booking_date': booking_date,
            'booking_time': booking_time,
            'special_requests': special_requests,
            'restaurant_id': 1  # Default restaurant ID, would normally come from auth context
        }
        
        booking, success, message = create_booking(booking_data)
        
        if success:
            # Send SMS confirmation if requested
            if send_sms and booking:
                send_booking_confirmation(booking)
                
            return jsonify({'success': True, 'booking_id': booking.id, 'message': 'Booking created successfully'})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        # Log the error
        log_action(
            'booking_error',
            'booking',
            None,
            f"Error creating booking: {str(e)}",
            json.dumps(request.form, default=str)
        )
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

@booking_bp.route('/booking/<int:booking_id>', methods=['GET'])
def view_booking(booking_id):
    """View a single booking"""
    booking = Booking.query.get_or_404(booking_id)
    return render_template('booking_detail.html', booking=booking)

@booking_bp.route('/booking/<action>/<int:booking_id>', methods=['POST'])
def booking_action(action, booking_id):
    """Handle booking actions (cancel, confirm, complete)"""
    booking = Booking.query.get_or_404(booking_id)
    
    if action == 'cancel':
        status = 'canceled'
    elif action == 'confirm':
        status = 'confirmed'
    elif action == 'complete':
        status = 'completed'
    else:
        return jsonify({'success': False, 'message': 'Invalid action'}), 400
    
    success, message = update_booking_status(booking, status)
    
    if success:
        return jsonify({'success': True, 'message': f'Booking {action}ed successfully'})
    else:
        return jsonify({'success': False, 'message': message}), 400
