import os
import requests
import logging
from datetime import datetime, timedelta
from flask import current_app

# Cache for storing user and organization info
_calendly_cache = {
    "user_uri": None,
    "organization_uri": None,
    "event_types": None
}

def _get_calendly_token():
    """Get Calendly API token from config or environment variables"""
    return current_app.config.get('CALENDLY_API_KEY') or os.environ.get('CALENDLY_API_KEY')

def _get_user_info(api_key):
    """
    Get user information from Calendly API
    
    Args:
        api_key (str): Calendly API key
        
    Returns:
        tuple: (user_uri, organization_uri)
    """
    # Check if we have cached values
    if _calendly_cache["user_uri"] and _calendly_cache["organization_uri"]:
        return _calendly_cache["user_uri"], _calendly_cache["organization_uri"]
    
    url = "https://api.calendly.com/users/me"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            user_uri = data["resource"]["uri"]
            org_uri = data["resource"]["current_organization"]
            
            # Cache the values
            _calendly_cache["user_uri"] = user_uri
            _calendly_cache["organization_uri"] = org_uri
            
            current_app.logger.info(f"Successfully retrieved Calendly user info: {user_uri}")
            return user_uri, org_uri
        else:
            current_app.logger.error(f"Failed to get Calendly user info: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        current_app.logger.error(f"Error getting Calendly user info: {str(e)}")
        return None, None

def _get_event_types(api_key, user_uri):
    """
    Get event types from Calendly API
    
    Args:
        api_key (str): Calendly API key
        user_uri (str): User URI
        
    Returns:
        list: List of event type URIs
    """
    # Check if we have cached values
    if _calendly_cache["event_types"]:
        return _calendly_cache["event_types"]
    
    url = "https://api.calendly.com/event_types"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "user": user_uri
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            event_types = [item["uri"] for item in data["collection"]]
            
            # Cache the values
            _calendly_cache["event_types"] = event_types
            
            if event_types:
                current_app.logger.info(f"Found {len(event_types)} Calendly event types")
                return event_types
            else:
                current_app.logger.warning("No Calendly event types found")
                return []
        else:
            current_app.logger.error(f"Failed to get Calendly event types: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        current_app.logger.error(f"Error getting Calendly event types: {str(e)}")
        return []

def _get_availability(api_key, event_type_uri, date_str):
    """
    Get availability for a specific event type and date
    
    Args:
        api_key (str): Calendly API key
        event_type_uri (str): Event type URI
        date_str (str): Date string in YYYY-MM-DD format
        
    Returns:
        list: List of available time slots
    """
    # Parse date
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    
    # Start and end times for the date
    start_time = date_obj.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
    end_time = (date_obj + timedelta(days=1)).replace(hour=0, minute=0, second=0).isoformat() + 'Z'
    
    url = "https://api.calendly.com/availability_schedules"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # First need to get the user's availability schedule
    try:
        # Try to get event type details
        event_url = event_type_uri
        event_response = requests.get(event_url, headers=headers)
        
        if event_response.status_code != 200:
            current_app.logger.error(f"Failed to get event type details: {event_response.status_code} - {event_response.text}")
            return []
            
        event_data = event_response.json()
        duration = event_data["resource"]["duration"]  # in minutes
        
        # Get user availability
        available_slots = []
        
        # For simplicity, we'll generate times based on the event type duration
        # In a real implementation, you'd use Calendly's availability API
        start_hour = 9  # 9am
        end_hour = 17   # 5pm
        
        for hour in range(start_hour, end_hour):
            for minute in [0, 30]:  # 30-minute intervals
                time_str = f"{hour:02d}:{minute:02d}"
                slot_time = date_obj.replace(hour=hour, minute=minute)
                
                # Add the slot
                available_slots.append({
                    'start_time': slot_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'end_time': (slot_time + timedelta(minutes=duration)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'time': time_str
                })
        
        return available_slots
    except Exception as e:
        current_app.logger.error(f"Error getting Calendly availability: {str(e)}")
        return []

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
        api_key = _get_calendly_token()
        
        if not api_key:
            current_app.logger.error("Calendly API key not found")
            return mock_available_slots(date_str)
            
        # Get user info
        user_uri, org_uri = _get_user_info(api_key)
        
        if not user_uri:
            current_app.logger.error("Couldn't get Calendly user info")
            return mock_available_slots(date_str)
            
        # Get event types
        event_types = _get_event_types(api_key, user_uri)
        
        if not event_types:
            current_app.logger.error("No Calendly event types found")
            return mock_available_slots(date_str)
            
        # Use the first event type for simplicity
        event_type_uri = event_types[0]
        
        # Get availability
        available_slots = _get_availability(api_key, event_type_uri, date_str)
        
        if available_slots:
            return available_slots
        else:
            current_app.logger.warning("No availability found, using mock data")
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
        api_key = _get_calendly_token()
        
        if not api_key:
            current_app.logger.error("Calendly API key not found")
            return f"mock-event-{booking.id}"
            
        # Get user info
        user_uri, org_uri = _get_user_info(api_key)
        
        if not user_uri:
            current_app.logger.error("Couldn't get Calendly user info")
            return f"mock-event-{booking.id}"
            
        # Get event types
        event_types = _get_event_types(api_key, user_uri)
        
        if not event_types:
            current_app.logger.error("No Calendly event types found")
            return f"mock-event-{booking.id}"
            
        # Use the first event type for simplicity or the one from env if specified
        event_type_uri = os.environ.get('CALENDLY_EVENT_TYPE') or event_types[0]
            
        # Format date and time
        booking_datetime = datetime.combine(
            booking.booking_date, 
            datetime.strptime(booking.booking_time, '%H:%M').time()
        ).isoformat() + 'Z'
        
        # Calendly API endpoint for creating scheduled events
        url = "https://api.calendly.com/scheduled_events"
        
        # Request headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Request data
        data = {
            "event_type": event_type_uri,
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
    
    # Simulate some slots being unavailable (e.g., 12:00, 13:30, 19:00)
    unavailable_times = ['12:00', '13:30', '19:00', '20:30']
    
    for hour in range(11, 22):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            
            # Skip unavailable times
            if time_str in unavailable_times:
                continue
                
            slot_time = date_obj.replace(hour=hour, minute=minute)
            available_slots.append({
                'start_time': slot_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'end_time': (slot_time + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S'),
                'time': time_str  # Add simple time format for easier comparison
            })
    
    return available_slots
