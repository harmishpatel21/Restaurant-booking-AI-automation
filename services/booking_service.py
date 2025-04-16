import re
import json
import datetime
from flask import current_app
from app import db
from models import Booking, Restaurant
from services.audit_service import log_action
from utils.calendly_helper import create_calendly_event, get_available_slots

def create_booking(booking_data):
    """
    Create a new booking record
    
    Args:
        booking_data (dict): Dictionary containing booking information
        
    Returns:
        tuple: (Booking object, success boolean, message string)
    """
    try:
        # Validate data
        if not all(key in booking_data for key in ['customer_name', 'customer_phone', 'party_size', 'booking_date', 'booking_time', 'restaurant_id']):
            return None, False, "Missing required booking information"
            
        # Check if restaurant exists
        restaurant = Restaurant.query.get(booking_data['restaurant_id'])
        if not restaurant:
            # For demo purposes, create a default restaurant if it doesn't exist
            restaurant = Restaurant(
                id=1,
                name="Demo Restaurant",
                phone_number="123-456-7890",
                address="123 Main St, Anytown, USA",
                opening_time="11:00",
                closing_time="22:00",
                capacity=50
            )
            db.session.add(restaurant)
            db.session.commit()
            
        # Check if slot is available using Calendly API
        # For demo, we'll assume it's available
        available = True
        
        if available:
            # Create booking in the database
            booking = Booking(
                restaurant_id=booking_data['restaurant_id'],
                customer_name=booking_data['customer_name'],
                customer_phone=booking_data['customer_phone'],
                customer_email=booking_data.get('customer_email', ''),
                party_size=booking_data['party_size'],
                booking_date=booking_data['booking_date'],
                booking_time=booking_data['booking_time'],
                special_requests=booking_data.get('special_requests', ''),
                status='confirmed'
            )
            
            db.session.add(booking)
            db.session.commit()
            
            # Log the booking creation
            log_action(
                'create_booking',
                'booking',
                booking.id,
                f"Booking created for {booking.customer_name} on {booking.booking_date} at {booking.booking_time}",
                json.dumps(booking_data, default=str)
            )
            
            # Create Calendly event (would happen here)
            # calendly_event_id = create_calendly_event(booking)
            # booking.calendly_event_id = calendly_event_id
            # db.session.commit()
            
            return booking, True, "Booking created successfully"
        else:
            return None, False, "The requested time slot is not available"
            
    except Exception as e:
        current_app.logger.error(f"Error in create_booking: {str(e)}")
        return None, False, f"An error occurred: {str(e)}"

def update_booking_status(booking, status):
    """
    Update the status of a booking
    
    Args:
        booking (Booking): Booking object to update
        status (str): New status ('confirmed', 'canceled', 'completed')
        
    Returns:
        tuple: (success boolean, message string)
    """
    try:
        if status not in ['confirmed', 'canceled', 'completed']:
            return False, "Invalid status"
            
        old_status = booking.status
        booking.status = status
        booking.updated_at = datetime.datetime.utcnow()
        
        db.session.commit()
        
        # Log the status update
        log_action(
            f'update_booking_status_{status}',
            'booking',
            booking.id,
            f"Booking status updated from {old_status} to {status}",
            json.dumps({
                'booking_id': booking.id,
                'old_status': old_status,
                'new_status': status
            })
        )
        
        return True, f"Booking status updated to {status}"
        
    except Exception as e:
        current_app.logger.error(f"Error in update_booking_status: {str(e)}")
        return False, f"An error occurred: {str(e)}"

def extract_booking_info(transcript):
    """
    Extract booking information from voice transcript
    
    Args:
        transcript (str): Transcribed text from user's speech
        
    Returns:
        tuple: (booking_data dict, response_text string)
    """
    # For a real implementation, this would use a more sophisticated NLP approach
    # Here we'll use basic regex patterns for demo purposes
    
    booking_data = {}
    
    # Extract name (assuming format like "my name is John Smith" or "this is John Smith")
    name_match = re.search(r"(?:my name is|this is) ([A-Za-z\s]+)", transcript, re.IGNORECASE)
    if name_match:
        booking_data['customer_name'] = name_match.group(1).strip()
    
    # Extract phone number
    phone_match = re.search(r"(?:my phone|my number|phone number|call me at) (?:is )?(?:1-)?(\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4})", transcript, re.IGNORECASE)
    if phone_match:
        booking_data['customer_phone'] = phone_match.group(1).strip()
    
    # Extract party size
    party_match = re.search(r"((?:a )?table for|party of|group of|we are) (\d+|one|two|three|four|five|six|seven|eight|nine|ten)", transcript, re.IGNORECASE)
    if party_match:
        party_size_str = party_match.group(2).strip().lower()
        # Convert word numbers to digits
        word_to_num = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        
        if party_size_str in word_to_num:
            booking_data['party_size'] = word_to_num[party_size_str]
        else:
            try:
                booking_data['party_size'] = int(party_size_str)
            except ValueError:
                pass
    
    # Extract date
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    if re.search(r"(?:today|tonight)", transcript, re.IGNORECASE):
        booking_data['booking_date'] = today
    elif re.search(r"(?:tomorrow)", transcript, re.IGNORECASE):
        booking_data['booking_date'] = tomorrow
    else:
        # Try to parse specific date formats
        date_match = re.search(r"(?:on|for) (?:the )?(\d{1,2})(?:st|nd|rd|th)? (?:of )?(January|February|March|April|May|June|July|August|September|October|November|December)", transcript, re.IGNORECASE)
        if date_match:
            day = int(date_match.group(1))
            month_str = date_match.group(2).lower()
            month_to_num = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
                'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
            }
            month = month_to_num.get(month_str, 1)
            
            # Assume current year or next year if the date is in the past
            year = today.year
            potential_date = datetime.date(year, month, day)
            if potential_date < today:
                year += 1
                potential_date = datetime.date(year, month, day)
                
            booking_data['booking_date'] = potential_date
    
    # Extract time
    time_match = re.search(r"(?:at|around) (\d{1,2})(?::(\d{2}))? ?(am|pm|a\.m\.|p\.m\.)?", transcript, re.IGNORECASE)
    if time_match:
        hour = int(time_match.group(1))
        minute = time_match.group(2)
        minute = int(minute) if minute else 0
        
        # Handle AM/PM
        ampm = time_match.group(3)
        if ampm and ('p' in ampm.lower()) and hour < 12:
            hour += 12
        elif ampm and ('a' in ampm.lower()) and hour == 12:
            hour = 0
            
        # Format time as HH:MM
        booking_data['booking_time'] = f"{hour:02d}:{minute:02d}"
    
    # Generate response text based on extracted information
    response_text = "Thank you for your booking request. "
    
    if 'customer_name' in booking_data:
        response_text += f"I have your name as {booking_data['customer_name']}. "
    else:
        response_text += "I didn't catch your name. Could you please provide it? "
    
    if 'party_size' in booking_data:
        response_text += f"You're looking for a table for {booking_data['party_size']}. "
    else:
        response_text += "How many people will be in your party? "
    
    if 'booking_date' in booking_data:
        date_str = booking_data['booking_date'].strftime("%A, %B %d")
        response_text += f"The reservation would be for {date_str}. "
    else:
        response_text += "What date would you like to book? "
    
    if 'booking_time' in booking_data:
        response_text += f"At {booking_data['booking_time']}. "
    else:
        response_text += "What time would you prefer? "
    
    if 'customer_phone' in booking_data:
        response_text += f"I have your contact number as {booking_data['customer_phone']}. "
    else:
        response_text += "Could you please provide a contact phone number? "
    
    # Check if we have all required information
    required_fields = ['customer_name', 'customer_phone', 'party_size', 'booking_date', 'booking_time']
    missing_fields = [field for field in required_fields if field not in booking_data]
    
    if not missing_fields:
        response_text += "I have all the information needed to complete your booking. "
        
        # Convert date object to string for JSON serialization
        if 'booking_date' in booking_data:
            booking_data['booking_date'] = booking_data['booking_date'].strftime('%Y-%m-%d')
            
        response_text += "Your booking is confirmed. "
    else:
        response_text += "I still need the following information to complete your booking: "
        response_text += ", ".join([field.replace('_', ' ') for field in missing_fields]) + ". "
    
    return booking_data, response_text
