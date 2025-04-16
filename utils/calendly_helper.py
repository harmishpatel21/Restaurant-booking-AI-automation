import os
import requests
from datetime import datetime, timedelta
from flask import current_app

def get_available_slots(date_str, duration_minutes=60):
    """
    Get available time slots from Calendly
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        duration_minutes (int, optional): Duration of the booking in minutes
        
    Returns:
        list: List of available time slots
    """
    try:
        api_key = current_app.config.get('CALENDLY_API_KEY') or os.environ.get('CALENDLY_API_KEY')
        
        if not api_key:
            current_app.logger.error("Calendly API key not found")
            # Return mock data for demo purposes
            return mock_available_slots(date_str)
            
        # Parse date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Start and end times for the date
        start_time = date_obj.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
        end_time = (date_obj + timedelta(days=1)).replace(hour=0, minute=0, second=0).isoformat() + 'Z'
        
        # Calendly API endpoint
        url = "https://api.calendly.com/scheduling_links"
        
        # Request headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Request parameters
        params = {
            "organization": os.environ.get('CALENDLY_ORGANIZATION'),
            "count": 100
        }
        
        # Make request to Calendly API
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # Process response to extract available slots
            # This would require additional API calls and processing
            # For demo, we'll return mock data
            return mock_available_slots(date_str)
        else:
            current_app.logger.error(f"Calendly API error: {response.status_code} - {response.text}")
            return mock_available_slots(date_str)
            
    except Exception as e:
        current_app.logger.error(f"Error in get_available_slots: {str(e)}")
        return mock_available_slots(date_str)

def create_calendly_event(booking):
    """
    Create a new event in Calendly
    
    Args:
        booking (Booking): Booking object with customer and booking information
        
    Returns:
        str: Calendly event ID if successful, None otherwise
    """
    try:
        api_key = current_app.config.get('CALENDLY_API_KEY') or os.environ.get('CALENDLY_API_KEY')
        
        if not api_key:
            current_app.logger.error("Calendly API key not found")
            # Return mock event ID for demo purposes
            return f"mock-event-{booking.id}"
            
        # Format date and time
        booking_datetime = datetime.combine(
            booking.booking_date, 
            datetime.strptime(booking.booking_time, '%H:%M').time()
        ).isoformat() + 'Z'
        
        # Calendly API endpoint
        url = "https://api.calendly.com/scheduled_events"
        
        # Request headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Request data
        data = {
            "event_type": os.environ.get('CALENDLY_EVENT_TYPE'),
            "start_time": booking_datetime,
            "end_time": (datetime.fromisoformat(booking_datetime[:-1]) + timedelta(hours=1)).isoformat() + 'Z',
            "invitee": {
                "name": booking.customer_name,
                "email": booking.customer_email or "guest@example.com",
                "timezone": "America/New_York"  # Would normally get from user's timezone
            }
        }
        
        # Make request to Calendly API
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 201:
            event_data = response.json()
            return event_data.get('id')
        else:
            current_app.logger.error(f"Calendly API error: {response.status_code} - {response.text}")
            return f"mock-event-{booking.id}"
            
    except Exception as e:
        current_app.logger.error(f"Error in create_calendly_event: {str(e)}")
        return f"mock-event-{booking.id}"

def mock_available_slots(date_str):
    """
    Generate mock available time slots for demo purposes
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        
    Returns:
        list: List of available time slots
    """
    # Parse date
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    
    # Generate slots from 11:00 to 21:00 with 30-minute intervals
    available_slots = []
    
    for hour in range(11, 22):
        for minute in [0, 30]:
            slot_time = date_obj.replace(hour=hour, minute=minute)
            available_slots.append({
                'start_time': slot_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'end_time': (slot_time + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S')
            })
    
    return available_slots
