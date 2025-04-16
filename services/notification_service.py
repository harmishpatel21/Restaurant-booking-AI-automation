import os
import json
from flask import current_app
from utils.twilio_helper import send_sms
from services.audit_service import log_action

def send_booking_confirmation(booking):
    """
    Send booking confirmation SMS to customer
    
    Args:
        booking (Booking): Booking object with customer information
        
    Returns:
        bool: True if SMS was sent successfully, False otherwise
    """
    try:
        if not booking or not booking.customer_phone:
            current_app.logger.error("Cannot send SMS: Invalid booking or missing phone number")
            return False
            
        # Prepare message text
        message = f"Hello {booking.customer_name}, your reservation at Demo Restaurant is confirmed for {booking.booking_date.strftime('%A, %B %d')} at {booking.booking_time} for {booking.party_size} people. Reference #: {booking.id}. Thank you!"
        
        # Send SMS via Twilio
        success = send_sms(booking.customer_phone, message)
        
        if success:
            # Log the SMS notification
            log_action(
                'sms_notification',
                'booking',
                booking.id,
                f"SMS confirmation sent to {booking.customer_phone}",
                json.dumps({
                    'booking_id': booking.id,
                    'phone': booking.customer_phone,
                    'message': message
                })
            )
            
            current_app.logger.info(f"SMS confirmation sent to {booking.customer_phone}")
            return True
        else:
            current_app.logger.error(f"Failed to send SMS to {booking.customer_phone}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"Error in send_booking_confirmation: {str(e)}")
        return False

def send_booking_reminder(booking):
    """
    Send booking reminder SMS to customer
    
    Args:
        booking (Booking): Booking object with customer information
        
    Returns:
        bool: True if SMS was sent successfully, False otherwise
    """
    try:
        if not booking or not booking.customer_phone:
            current_app.logger.error("Cannot send reminder: Invalid booking or missing phone number")
            return False
            
        # Prepare message text
        message = f"Hello {booking.customer_name}, this is a reminder about your reservation at Demo Restaurant tomorrow ({booking.booking_date.strftime('%A, %B %d')}) at {booking.booking_time} for {booking.party_size} people. We look forward to seeing you!"
        
        # Send SMS via Twilio
        success = send_sms(booking.customer_phone, message)
        
        if success:
            # Log the SMS reminder
            log_action(
                'sms_reminder',
                'booking',
                booking.id,
                f"SMS reminder sent to {booking.customer_phone}",
                json.dumps({
                    'booking_id': booking.id,
                    'phone': booking.customer_phone,
                    'message': message
                })
            )
            
            current_app.logger.info(f"SMS reminder sent to {booking.customer_phone}")
            return True
        else:
            current_app.logger.error(f"Failed to send SMS reminder to {booking.customer_phone}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"Error in send_booking_reminder: {str(e)}")
        return False

def send_booking_cancellation(booking):
    """
    Send booking cancellation SMS to customer
    
    Args:
        booking (Booking): Booking object with customer information
        
    Returns:
        bool: True if SMS was sent successfully, False otherwise
    """
    try:
        if not booking or not booking.customer_phone:
            current_app.logger.error("Cannot send cancellation: Invalid booking or missing phone number")
            return False
            
        # Prepare message text
        message = f"Hello {booking.customer_name}, your reservation at Demo Restaurant for {booking.booking_date.strftime('%A, %B %d')} at {booking.booking_time} has been cancelled. If this was a mistake, please call us at {os.environ.get('RESTAURANT_PHONE', '123-456-7890')}."
        
        # Send SMS via Twilio
        success = send_sms(booking.customer_phone, message)
        
        if success:
            # Log the SMS cancellation
            log_action(
                'sms_cancellation',
                'booking',
                booking.id,
                f"SMS cancellation sent to {booking.customer_phone}",
                json.dumps({
                    'booking_id': booking.id,
                    'phone': booking.customer_phone,
                    'message': message
                })
            )
            
            current_app.logger.info(f"SMS cancellation sent to {booking.customer_phone}")
            return True
        else:
            current_app.logger.error(f"Failed to send SMS cancellation to {booking.customer_phone}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"Error in send_booking_cancellation: {str(e)}")
        return False
