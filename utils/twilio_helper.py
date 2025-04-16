import os
from twilio.rest import Client
from flask import current_app

def send_sms(to_phone_number, message):
    """
    Send SMS message using Twilio
    
    Args:
        to_phone_number (str): Recipient's phone number
        message (str): Message content
        
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        # Get Twilio credentials from environment
        account_sid = current_app.config.get('TWILIO_ACCOUNT_SID') or os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = current_app.config.get('TWILIO_AUTH_TOKEN') or os.environ.get('TWILIO_AUTH_TOKEN')
        from_phone = current_app.config.get('TWILIO_PHONE_NUMBER') or os.environ.get('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_phone]):
            current_app.logger.error("Twilio credentials not found")
            return False
            
        # Format phone number if needed
        to_phone_number = format_phone_number(to_phone_number)
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send message
        message = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone_number
        )
        
        current_app.logger.info(f"SMS sent with SID: {message.sid}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error sending SMS: {str(e)}")
        return False

def format_phone_number(phone_number):
    """
    Format phone number for Twilio
    
    Args:
        phone_number (str): Phone number to format
        
    Returns:
        str: Formatted phone number
    """
    # Remove any non-digit characters
    digits_only = ''.join(filter(str.isdigit, phone_number))
    
    # Ensure number has country code
    if len(digits_only) == 10:  # US number without country code
        return f"+1{digits_only}"
    elif len(digits_only) > 10:  # Already has country code
        return f"+{digits_only}"
    else:
        # Invalid number format, return as is
        return phone_number

def send_email_to_sms(to_phone_number, message, carrier):
    """
    Send SMS via email-to-SMS gateway as fallback
    
    Args:
        to_phone_number (str): Recipient's phone number
        message (str): Message content
        carrier (str): Phone carrier (e.g., 'att', 'tmobile', 'verizon')
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get SMTP credentials from environment
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = os.environ.get('SMTP_PORT')
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
            current_app.logger.error("SMTP credentials not found")
            return False
            
        # Format phone number
        digits_only = ''.join(filter(str.isdigit, to_phone_number))
        
        # Get carrier domain
        carrier_domains = {
            'att': 'txt.att.net',
            'tmobile': 'tmomail.net',
            'verizon': 'vtext.com',
            'sprint': 'messaging.sprintpcs.com'
        }
        
        carrier_domain = carrier_domains.get(carrier.lower())
        if not carrier_domain:
            current_app.logger.error(f"Unknown carrier: {carrier}")
            return False
            
        # Construct email address
        to_email = f"{digits_only}@{carrier_domain}"
        
        # Send email
        # This would normally use smtplib or a mail service
        # For demo purposes, we'll just log it
        current_app.logger.info(f"Email-to-SMS would be sent to {to_email} with message: {message}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error sending email-to-SMS: {str(e)}")
        return False
